"""
World Cup 2026 — Tournament simulation logic.

Builds on model_utils.predict_match to simulate:
- Single group stage matches
- Full group stage standings
- Knockout rounds (R32 → Final)
- Monte Carlo over thousands of tournaments
"""

import random
from collections import Counter

import pandas as pd

from model_utils import (
    haversine, venue_in_team_country,
    MOMENTUM_CAP, DRAW_PENALTY, KNOCKOUT_VENUES, FEATURE_COLUMNS,
)
from data_constants import (
    GROUPS_2026, ALL_TEAMS_2026, GROUP_FIXTURES,
    VENUES_2026, TRAINING_BASES,
    R16_PAIRS, QF_PAIRS, SF_PAIRS,
)


# ============================================================
# MOMENTUM
# ============================================================

def momentum_delta(team_elo, opponent_elo, result):
    """How much should a team's momentum change after a match?"""
    elo_diff = opponent_elo - team_elo
    if result == "win":
        return 5 + 10 * min(1.0, max(0.0, (elo_diff + 200) / 400))
    elif result == "loss":
        return -10 - 10 * min(1.0, max(0.0, (-elo_diff + 200) / 400))
    return DRAW_PENALTY


def apply_momentum(current, delta):
    """Apply a delta, respecting the ±cap."""
    return max(-MOMENTUM_CAP, min(MOMENTUM_CAP, current + delta))


# ============================================================
# BATCH PREDICTION (vectorized)
# ============================================================

def predict_matches_batch(matchups, *, model, scaler, elo_ratings,
                          team_snapshots, momentums=None):
    """Predict probabilities for many matches in a single sklearn call."""
    if not matchups:
        return []
    momentums = momentums or {}

    rows = []
    for m in matchups:
        team_a, team_b, venue = m["team_a"], m["team_b"], m["venue_city"]
        elo_a = elo_ratings[team_a] + momentums.get(team_a, 0)
        elo_b = elo_ratings[team_b] + momentums.get(team_b, 0)

        a_gs = team_snapshots[team_a]["goals_scored_avg"]
        a_gc = team_snapshots[team_a]["goals_conceded_avg"]
        b_gs = team_snapshots[team_b]["goals_scored_avg"]
        b_gc = team_snapshots[team_b]["goals_conceded_avg"]

        a_home = venue_in_team_country(team_a, venue)
        b_home = venue_in_team_country(team_b, venue)
        home_adv = 1 if (a_home and not b_home) else 0

        venue_coords = VENUES_2026[venue]
        a_base = TRAINING_BASES[team_a]["coords"]
        b_base = TRAINING_BASES[team_b]["coords"]
        a_travel = haversine(*a_base, *venue_coords)
        b_travel = haversine(*b_base, *venue_coords)

        rows.append({
            "elo_diff": elo_a - elo_b,
            "adj_form_diff": 0.0,
            "home_goals_scored_avg": a_gs,
            "home_goals_conceded_avg": a_gc,
            "away_goals_scored_avg": b_gs,
            "away_goals_conceded_avg": b_gc,
            "home_advantage": home_adv,
            "home_travel_km": a_travel,
            "away_travel_km": b_travel,
        })

    X_scaled = scaler.transform(pd.DataFrame(rows))
    probs = model.predict_proba(X_scaled)
    classes = list(model.classes_)
    h_idx, d_idx, a_idx = (classes.index("home_win"),
                            classes.index("draw"),
                            classes.index("away_win"))

    results = []
    for i, m in enumerate(matchups):
        r = {"home_win": float(probs[i, h_idx]),
             "draw":     float(probs[i, d_idx]),
             "away_win": float(probs[i, a_idx])}
        if m.get("knockout"):
            total = r["home_win"] + r["away_win"]
            r["home_win"] /= total
            r["away_win"] /= total
            r["draw"] = 0.0
        results.append(r)
    return results


def sample_outcomes_batch(probs_list):
    outcomes = ["home_win", "draw", "away_win"]
    return [random.choices(outcomes, weights=[p["home_win"], p["draw"], p["away_win"]], k=1)[0]
            for p in probs_list]


# ============================================================
# GROUP STAGE
# ============================================================

def simulate_group_stage(*, model, scaler, elo_ratings, team_snapshots, momentums):
    """Simulate all 72 group matches. Updates momentums in place. Returns standings."""
    standings = {t: {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0}
                 for t in ALL_TEAMS_2026}

    matchups = [{"team_a": a, "team_b": b, "venue_city": v, "knockout": False}
                for a, b, v in GROUP_FIXTURES]
    probs = predict_matches_batch(matchups, model=model, scaler=scaler,
                                  elo_ratings=elo_ratings, team_snapshots=team_snapshots,
                                  momentums=momentums)
    outcomes = sample_outcomes_batch(probs)

    for (team_a, team_b, _venue), outcome in zip(GROUP_FIXTURES, outcomes):
        a_gs = team_snapshots[team_a]["goals_scored_avg"]
        b_gs = team_snapshots[team_b]["goals_scored_avg"]

        if outcome == "home_win":
            score_a = max(1, round(random.gauss(a_gs, 0.8)))
            score_b = max(0, round(random.gauss(b_gs * 0.5, 0.6)))
            if score_a <= score_b: score_a = score_b + 1
        elif outcome == "away_win":
            score_b = max(1, round(random.gauss(b_gs, 0.8)))
            score_a = max(0, round(random.gauss(a_gs * 0.5, 0.6)))
            if score_b <= score_a: score_b = score_a + 1
        else:
            shared = max(0, round(random.gauss((a_gs + b_gs) / 2, 0.6)))
            score_a = score_b = shared

        standings[team_a]["P"] += 1; standings[team_b]["P"] += 1
        standings[team_a]["GF"] += score_a; standings[team_a]["GA"] += score_b
        standings[team_b]["GF"] += score_b; standings[team_b]["GA"] += score_a

        elo_a_full = elo_ratings[team_a] + momentums.get(team_a, 0)
        elo_b_full = elo_ratings[team_b] + momentums.get(team_b, 0)

        if outcome == "home_win":
            standings[team_a]["W"] += 1; standings[team_b]["L"] += 1
            standings[team_a]["Pts"] += 3
            momentums[team_a] = apply_momentum(momentums.get(team_a, 0),
                                               momentum_delta(elo_a_full, elo_b_full, "win"))
            momentums[team_b] = apply_momentum(momentums.get(team_b, 0),
                                               momentum_delta(elo_b_full, elo_a_full, "loss"))
        elif outcome == "away_win":
            standings[team_b]["W"] += 1; standings[team_a]["L"] += 1
            standings[team_b]["Pts"] += 3
            momentums[team_b] = apply_momentum(momentums.get(team_b, 0),
                                               momentum_delta(elo_b_full, elo_a_full, "win"))
            momentums[team_a] = apply_momentum(momentums.get(team_a, 0),
                                               momentum_delta(elo_a_full, elo_b_full, "loss"))
        else:
            standings[team_a]["D"] += 1; standings[team_b]["D"] += 1
            standings[team_a]["Pts"] += 1; standings[team_b]["Pts"] += 1
            momentums[team_a] = apply_momentum(momentums.get(team_a, 0), DRAW_PENALTY)
            momentums[team_b] = apply_momentum(momentums.get(team_b, 0), DRAW_PENALTY)

    for t in standings:
        standings[t]["GD"] = standings[t]["GF"] - standings[t]["GA"]
    return standings


def get_advancing_teams(standings):
    winners, runners_up, thirds = [], [], []
    for letter in "ABCDEFGHIJKL":
        teams = GROUPS_2026[letter]
        sorted_g = sorted(teams,
                          key=lambda t: (standings[t]["Pts"], standings[t]["GD"], standings[t]["GF"]),
                          reverse=True)
        winners.append(sorted_g[0])
        runners_up.append(sorted_g[1])
        thirds.append((sorted_g[2], letter))

    thirds_sorted = sorted(thirds,
                           key=lambda x: (standings[x[0]]["Pts"], standings[x[0]]["GD"],
                                          standings[x[0]]["GF"]),
                           reverse=True)
    best_thirds = [t[0] for t in thirds_sorted[:8]]
    qualifying_letters = {t[1] for t in thirds_sorted[:8]}

    qualified_groups = {}
    for team, letter in thirds_sorted[:8]:
        qualified_groups[letter] = team

    return {"winners": winners, "runners_up": runners_up,
            "best_thirds": best_thirds, "qualified_groups": qualified_groups}


# ============================================================
# KNOCKOUTS
# ============================================================

def build_round_of_32(advancing, third_place_table):
    W, R = advancing["winners"], advancing["runners_up"]
    qualified_groups = advancing["qualified_groups"]

    slot = {}
    for i, letter in enumerate("ABCDEFGHIJKL"):
        slot[f"1{letter}"] = W[i]
        slot[f"2{letter}"] = R[i]
    for letter, team in qualified_groups.items():
        slot[f"3{letter}"] = team

    assignments = third_place_table[frozenset(qualified_groups.keys())]
    vs_1A, vs_1B, vs_1D, vs_1E, vs_1G, vs_1I, vs_1K, vs_1L = assignments

    return {
        73: (slot["2A"], slot["2B"]),  74: (slot["1E"], slot[vs_1E]),
        75: (slot["1F"], slot["2C"]),  76: (slot["1C"], slot["2F"]),
        77: (slot["1I"], slot[vs_1I]), 78: (slot["2E"], slot["2I"]),
        79: (slot["1A"], slot[vs_1A]), 80: (slot["1L"], slot[vs_1L]),
        81: (slot["1D"], slot[vs_1D]), 82: (slot["1G"], slot[vs_1G]),
        83: (slot["2K"], slot["2L"]),  84: (slot["1H"], slot["2J"]),
        85: (slot["1B"], slot[vs_1B]), 86: (slot["1J"], slot["2H"]),
        87: (slot["1K"], slot[vs_1K]), 88: (slot["2D"], slot["2G"]),
    }


def simulate_knockout_round(fixtures, *, model, scaler, elo_ratings,
                            team_snapshots, momentums):
    matchups = []
    for match_num, (a, b) in fixtures.items():
        venue = KNOCKOUT_VENUES[match_num % len(KNOCKOUT_VENUES)]
        matchups.append({"team_a": a, "team_b": b, "venue_city": venue, "knockout": True})

    probs = predict_matches_batch(matchups, model=model, scaler=scaler,
                                  elo_ratings=elo_ratings, team_snapshots=team_snapshots,
                                  momentums=momentums)
    outcomes = sample_outcomes_batch(probs)

    winners = {}
    for (match_num, (a, b)), outcome in zip(fixtures.items(), outcomes):
        elo_a = elo_ratings[a] + momentums.get(a, 0)
        elo_b = elo_ratings[b] + momentums.get(b, 0)
        if outcome == "home_win":
            winners[match_num] = a
            momentums[a] = apply_momentum(momentums.get(a, 0), momentum_delta(elo_a, elo_b, "win"))
            momentums[b] = apply_momentum(momentums.get(b, 0), momentum_delta(elo_b, elo_a, "loss"))
        else:
            winners[match_num] = b
            momentums[b] = apply_momentum(momentums.get(b, 0), momentum_delta(elo_b, elo_a, "win"))
            momentums[a] = apply_momentum(momentums.get(a, 0), momentum_delta(elo_a, elo_b, "loss"))
    return winners


def simulate_tournament(*, model, scaler, elo_ratings, team_snapshots,
                        third_place_table, use_momentum=True):
    """Run one complete World Cup. Returns dict with champion + key stages."""
    momentums = {t: 0.0 for t in ALL_TEAMS_2026} if use_momentum else {}

    standings = simulate_group_stage(model=model, scaler=scaler, elo_ratings=elo_ratings,
                                     team_snapshots=team_snapshots, momentums=momentums)
    advancing = get_advancing_teams(standings)

    r32 = build_round_of_32(advancing, third_place_table)
    r32_w = simulate_knockout_round(r32, model=model, scaler=scaler, elo_ratings=elo_ratings,
                                    team_snapshots=team_snapshots, momentums=momentums)

    r16 = {m: (r32_w[a], r32_w[b]) for m, (a, b) in R16_PAIRS.items()}
    r16_w = simulate_knockout_round(r16, model=model, scaler=scaler, elo_ratings=elo_ratings,
                                    team_snapshots=team_snapshots, momentums=momentums)

    qf = {m: (r16_w[a], r16_w[b]) for m, (a, b) in QF_PAIRS.items()}
    qf_w = simulate_knockout_round(qf, model=model, scaler=scaler, elo_ratings=elo_ratings,
                                   team_snapshots=team_snapshots, momentums=momentums)

    sf = {m: (qf_w[a], qf_w[b]) for m, (a, b) in SF_PAIRS.items()}
    sf_w = simulate_knockout_round(sf, model=model, scaler=scaler, elo_ratings=elo_ratings,
                                   team_snapshots=team_snapshots, momentums=momentums)

    final = {103: (sf_w[101], sf_w[102])}
    final_w = simulate_knockout_round(final, model=model, scaler=scaler, elo_ratings=elo_ratings,
                                      team_snapshots=team_snapshots, momentums=momentums)
    champion = final_w[103]
    runner_up = sf_w[101] if champion == sf_w[102] else sf_w[102]

    return {
        "champion": champion,
        "runner_up": runner_up,
        "semifinalists": list(qf_w.values()),
        "quarterfinalists": list(r16_w.values()),
        "r16_teams": list(r32_w.values()),
    }
