"""
World Cup 2026 Predictor — Streamlit app.

Three pages:
- Single match prediction
- Monte Carlo tournament results
- Methodology
"""

import json
import pickle
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Make local modules importable
sys.path.insert(0, str(Path(__file__).parent))

from model_utils import predict_match, get_winner_label
from data_constants import (
    ALL_TEAMS_2026, GROUPS_2026, VENUES_2026, TRAINING_BASES,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="World Cup 2026 Predictor",
    page_icon="⚽",
    layout="wide",
)


# ============================================================
# DATA LOADING (cached so it only happens once per session)
# ============================================================

@st.cache_resource
def load_all_data():
    """Load model, scaler, and all reference data. Cached across reruns."""
    data_dir = Path(__file__).parent / "data"

    with open(data_dir / "worldcup_model.pkl", "rb") as f:
        bundle = pickle.load(f)

    with open(data_dir / "team_data.json", "r") as f:
        team_data = json.load(f)

    with open(data_dir / "baseline_montecarlo.pkl", "rb") as f:
        baseline_mc = pickle.load(f)

    with open(data_dir / "momentum_montecarlo.pkl", "rb") as f:
        momentum_mc = pickle.load(f)

    return {
        "model": bundle["model"],
        "scaler": bundle["scaler"],
        "elo_ratings": team_data["elo_ratings"],
        "team_snapshots": team_data["team_snapshots"],
        "baseline_mc": baseline_mc,
        "momentum_mc": momentum_mc,
    }


DATA = load_all_data()


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("⚽ World Cup 2026")
st.sidebar.markdown("*An ML predictor for the upcoming tournament*")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🎯 Predict a Match", "🏆 Tournament Simulation", "📖 How It Works"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.caption("Built by Nader — [GitHub](https://github.com/Naderpy)")


# ============================================================
# PAGE 1: SINGLE MATCH PREDICTION
# ============================================================

if page == "🎯 Predict a Match":
    st.title("Predict a Match")
    st.markdown("Pick two teams and a venue. The model returns probabilities for each outcome.")

    col1, col2, col3 = st.columns(3)
    sorted_teams = sorted(ALL_TEAMS_2026)
    with col1:
        team_a = st.selectbox("Team A (home)", sorted_teams,
                              index=sorted_teams.index("Argentina"))
    with col2:
        team_b_options = [t for t in sorted_teams if t != team_a]
        team_b = st.selectbox("Team B (away)", team_b_options,
                              index=team_b_options.index("Brazil") if "Brazil" in team_b_options else 0)
    with col3:
        venue = st.selectbox("Venue", sorted(VENUES_2026.keys()))

    if st.button("Predict outcome", type="primary", use_container_width=True):
        probs = predict_match(
            team_a, team_b, venue,
            model=DATA["model"], scaler=DATA["scaler"],
            elo_ratings=DATA["elo_ratings"],
            team_snapshots=DATA["team_snapshots"],
            training_bases=TRAINING_BASES, venues=VENUES_2026,
        )

        st.markdown("---")
        st.subheader(f"{team_a} vs {team_b} @ {venue}")

        # Big number row
        m1, m2, m3 = st.columns(3)
        m1.metric(f"🔵 {team_a} win", f"{probs['home_win']:.0%}")
        m2.metric("⚪ Draw", f"{probs['draw']:.0%}")
        m3.metric(f"🔴 {team_b} win", f"{probs['away_win']:.0%}")

        # Bar chart
        chart_df = pd.DataFrame({
            "Outcome": [f"{team_a} win", "Draw", f"{team_b} win"],
            "Probability": [probs["home_win"], probs["draw"], probs["away_win"]],
        })
        st.bar_chart(chart_df, x="Outcome", y="Probability", height=250)

        # Why the model thinks this
        st.markdown("### Why this prediction?")
        feat_col1, feat_col2 = st.columns(2)
        with feat_col1:
            st.markdown(f"**{team_a}**")
            st.write(f"- Current Elo: **{probs['elo_a']:.0f}**")
            st.write(f"- Training base: {TRAINING_BASES[team_a]['city']}")
            st.write(f"- Travel to venue: **{probs['travel_a']:.0f} km**")
        with feat_col2:
            st.markdown(f"**{team_b}**")
            st.write(f"- Current Elo: **{probs['elo_b']:.0f}**")
            st.write(f"- Training base: {TRAINING_BASES[team_b]['city']}")
            st.write(f"- Travel to venue: **{probs['travel_b']:.0f} km**")

        if probs["home_adv"]:
            st.info(f"🏠 {team_a} has home advantage at this venue.")

        st.success(f"**Bottom line:** {get_winner_label(team_a, team_b, probs)}")


# ============================================================
# PAGE 2: TOURNAMENT SIMULATION RESULTS
# ============================================================

elif page == "🏆 Tournament Simulation":
    st.title("Tournament Simulation Results")
    st.markdown(
        "These are aggregated results from running the entire 2026 World Cup "
        "**10,000 times**, sampling realistic randomness in every match."
    )

    # Toggle between baseline and momentum
    view = st.radio(
        "View:",
        ["Baseline model", "With tournament momentum", "Compare both"],
        horizontal=True,
    )

    mc = DATA["baseline_mc"]
    mc_alt = DATA["momentum_mc"]
    n_sims = mc["n_simulations"]

    def build_summary(mc_data):
        rows = []
        for team in ALL_TEAMS_2026:
            rows.append({
                "Team": team,
                "Champ %":  mc_data["champion_count"].get(team, 0) / n_sims * 100,
                "Final %":  mc_data["final_count"].get(team, 0) / n_sims * 100,
                "Semi %":   mc_data["sf_count"].get(team, 0) / n_sims * 100,
                "QF %":     mc_data["qf_count"].get(team, 0) / n_sims * 100,
                "R16 %":    mc_data["r16_count"].get(team, 0) / n_sims * 100,
            })
        return pd.DataFrame(rows).sort_values("Champ %", ascending=False).reset_index(drop=True)

    df_main = build_summary(mc if view != "With tournament momentum" else mc_alt)

    # Top 10 bar chart
    st.subheader("Top 10 most likely champions")
    top10 = df_main.head(10).set_index("Team")["Champ %"]
    st.bar_chart(top10, height=350)

    # Full table
    st.subheader(f"All 48 teams — probability of reaching each stage")

    if view == "Compare both":
        df_a = build_summary(mc).rename(columns={"Champ %": "Champ % (baseline)"})
        df_b = build_summary(mc_alt).rename(columns={"Champ %": "Champ % (+ momentum)"})
        combined = df_a[["Team", "Champ % (baseline)"]].merge(
            df_b[["Team", "Champ % (+ momentum)"]], on="Team"
        )
        combined["Δ"] = combined["Champ % (+ momentum)"] - combined["Champ % (baseline)"]
        combined = combined.sort_values("Champ % (baseline)", ascending=False).reset_index(drop=True)
        st.dataframe(combined.style.format({
            "Champ % (baseline)": "{:.1f}%",
            "Champ % (+ momentum)": "{:.1f}%",
            "Δ": "{:+.2f}",
        }), height=600, use_container_width=True)
    else:
       st.dataframe(
            df_main,
            height=600,
            use_container_width=True,
            column_config={
                "Champ %":  st.column_config.NumberColumn(format="%.1f%%"),
                "Final %":  st.column_config.NumberColumn(format="%.1f%%"),
                "Semi %":   st.column_config.NumberColumn(format="%.1f%%"),
                "QF %":     st.column_config.NumberColumn(format="%.1f%%"),
                "R16 %":    st.column_config.NumberColumn(format="%.1f%%"),
            },
        )
    # Surprising findings
    st.markdown("---")
    st.subheader("🔍 Findings worth noticing")
    findings_col1, findings_col2 = st.columns(2)

    with findings_col1:
        morocco_sf = mc["sf_count"].get("Morocco", 0) / n_sims * 100
        colombia_champ = mc["champion_count"].get("Colombia", 0) / n_sims * 100
        st.markdown(f"**Morocco reaches the semifinals in {morocco_sf:.1f}% of simulations** — "
                    f"validating that their 2022 World Cup run wasn't a fluke.")
        st.markdown(f"**Colombia wins the tournament in {colombia_champ:.1f}% of runs** — "
                    f"higher than Portugal or Netherlands.")

    with findings_col2:
        germany_champ = mc["champion_count"].get("Germany", 0) / n_sims * 100
        japan_qf = mc["qf_count"].get("Japan", 0) / n_sims * 100
        st.markdown(f"**Germany wins only {germany_champ:.1f}% of simulations** — "
                    f"the model sees them as a tier-2 team, not a contender.")
        st.markdown(f"**Japan reaches the quarterfinals in {japan_qf:.1f}% of runs** — "
                    f"rated above several European powers.")


# ============================================================
# PAGE 3: METHODOLOGY
# ============================================================

else:
    st.title("How It Works")

    st.markdown("""
This is a **first ML project** built end-to-end:
data collection → feature engineering → model training → Monte Carlo simulation → demo deployment.
Source code: [github.com/Naderpy](https://github.com/Naderpy)
""")

    st.markdown("---")
    st.header("1 · The data")
    st.markdown("""
- **~21,000 international football matches** from 2004 to 2026 (Kaggle's *international results* dataset)
- **Elo ratings** computed from scratch by walking through every match chronologically, applying the standard *World Football Elo* formula (with home advantage and goal-difference multiplier)
- **Real 2026 fixtures** with venues from the FIFA schedule
- **Real training base coordinates** from FIFA's official May 2026 announcement
""")

    st.markdown("---")
    st.header("2 · The model")
    st.markdown("""
**Multinomial logistic regression** predicting `{home_win, draw, away_win}` from 9 features:

| Feature | What it captures |
|---|---|
| Elo difference | Overall team strength gap |
| Adjusted form | Recent performance vs Elo expectation |
| Avg goals scored (both teams) | Attacking output |
| Avg goals conceded (both teams) | Defensive solidity |
| Home advantage flag | Real home crowd benefit |
| Travel distance (both teams) | Distance from training base to venue |

**Test set performance:** 60% accuracy, log loss 0.879 — in the range of professionally published models.
""")

    st.markdown("---")
    st.header("3 · Monte Carlo — the part that took me a while to wrap my head around")
    st.markdown("""
The model predicts probabilities for individual matches.
But the question I want to answer is *"who wins the World Cup?"* — and that depends on **7 rounds of branching matches**, each one's opponent determined by who won earlier rounds.

The math for "P(Argentina wins) = sum over all possible bracket paths" is intractable. You'd need to enumerate millions of branching scenarios.

**Monte Carlo simulation is the shortcut:**

1. Simulate one full tournament. Sample a random outcome for each match using the model's probabilities. Record the champion.
2. Reset. Do it again.
3. Do this **10,000 times.**
4. *"Argentina won in 3,210 of those tournaments → Argentina has a ~32% chance of winning."*

This is the same technique used by FiveThirtyEight, Opta, and most professional sports models. It originated in the 1940s with physicists doing nuclear weapon calculations.

**Two things make it work for us:**
- Each simulation must be genuinely random. The model says "60% home win" — sometimes the 40% has to happen. Otherwise every simulation produces the same result.
- The probabilities must be **calibrated** — when the model says 70%, that has to actually happen ~70% of the time across many matches. That's what our log-loss score measures.

The result isn't "the model predicts X to win." It's a **distribution over possible futures**. Some simulations have Brazil winning, some have France, a few have surprise runs by Morocco. The aggregate over thousands of simulations is the signal.
""")

    st.markdown("---")
    st.header("4 · Tournament momentum (an experiment)")
    st.markdown("""
On top of the baseline model, I added a "momentum" feature: during simulation, teams that win matches get a small Elo boost for their next match (capped at ±40). Beating a strong team gives more boost than beating a minnow.

**The finding:** momentum changes individual simulations a lot, but the *aggregate* championship probabilities barely shift (±1.2 percentage points at most). Even at full momentum, an underdog can't catch the elite teams across 7 rounds.

This was an interesting non-result: at this calibration, tournament hot streaks are real but smaller than fan intuition suggests.
""")

    st.markdown("---")
    st.header("5 · Limitations (the honest list)")
    st.markdown("""
- No injury or player-level data — purely team-level
- Training base distances substituted for home-country distances at training time
- Goal scorelines in simulations are heuristic, not from a Poisson model
- The model trusts recent form heavily; Argentina's high probability may partly reflect their absurd recent goal-scoring streak rather than long-term skill
- Bookmaker odds (the gold standard) usually have the favorite at 18-22% — my model has Argentina at 32%, which is on the bullish side
""")

    st.markdown("---")
    st.caption("Built with Python, scikit-learn, and Streamlit. No models were harmed in the making of this app.")
