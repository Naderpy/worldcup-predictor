"""
World Cup 2026 Predictor — Core ML and simulation logic.

This module loads the trained model and provides functions for:
- Predicting individual match outcomes
- Simulating the 2026 World Cup tournament
- Running Monte Carlo simulations

All UI code lives in app.py.
"""

import json
import pickle
import random
from collections import Counter

import numpy as np
import pandas as pd


# ============================================================
# CONSTANTS
# ============================================================

MOMENTUM_CAP = 40
DRAW_PENALTY = -2
HOME_ADVANTAGE_BONUS = 100

US_VENUES = {"Atlanta", "Boston", "Dallas", "Houston", "Kansas City",
             "Los Angeles", "Miami", "New York/NJ", "Philadelphia",
             "San Francisco", "Seattle"}
MEXICO_VENUES = {"Mexico City", "Guadalajara", "Monterrey"}
CANADA_VENUES = {"Toronto", "Vancouver"}

KNOCKOUT_VENUES = [
    "Los Angeles", "New York/NJ", "Dallas", "Atlanta",
    "Miami", "Boston", "Philadelphia", "Kansas City",
    "Houston", "Seattle", "San Francisco", "Mexico City",
    "Toronto", "Vancouver", "Guadalajara", "Monterrey",
]

FEATURE_COLUMNS = [
    "elo_diff", "adj_form_diff",
    "home_goals_scored_avg", "home_goals_conceded_avg",
    "away_goals_scored_avg", "away_goals_conceded_avg",
    "home_advantage", "home_travel_km", "away_travel_km",
]


# ============================================================
# DATA LOADING
# ============================================================

def load_artifacts(data_dir="data"):
    """Load model, third-place table, and all reference data from disk."""
    with open(f"{data_dir}/worldcup_model.pkl", "rb") as f:
        bundle = pickle.load(f)

    with open(f"{data_dir}/third_place_table.json", "r") as f:
        raw_table = json.load(f)
        third_place_table = {frozenset(k): tuple(v) for k, v in raw_table.items()}

    with open(f"{data_dir}/baseline_montecarlo.pkl", "rb") as f:
        baseline_mc = pickle.load(f)

    with open(f"{data_dir}/momentum_montecarlo.pkl", "rb") as f:
        momentum_mc = pickle.load(f)

    return {
        "model": bundle["model"],
        "scaler": bundle["scaler"],
        "feature_columns": bundle["feature_columns"],
        "third_place_table": third_place_table,
        "baseline_mc": baseline_mc,
        "momentum_mc": momentum_mc,
    }


# ============================================================
# GEOGRAPHY
# ============================================================

def haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance in km between two (lat, lon) points."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))


def venue_in_team_country(team, venue_city):
    """Is the venue in the team's home country? Only matters for hosts."""
    if team == "United States" and venue_city in US_VENUES:
        return True
    if team == "Mexico" and venue_city in MEXICO_VENUES:
        return True
    if team == "Canada" and venue_city in CANADA_VENUES:
        return True
    return False


# ============================================================
# PREDICTION
# ============================================================

def predict_match(team_a, team_b, venue_city, *,
                  model, scaler, elo_ratings, team_snapshots,
                  training_bases, venues, momentums=None, knockout=False):
    """Predict probabilities for a single match between team_a (home) and team_b."""
    momentums = momentums or {}

    elo_a = elo_ratings[team_a] + momentums.get(team_a, 0)
    elo_b = elo_ratings[team_b] + momentums.get(team_b, 0)
    elo_diff = elo_a - elo_b

    a_gs = team_snapshots[team_a]["goals_scored_avg"]
    a_gc = team_snapshots[team_a]["goals_conceded_avg"]
    b_gs = team_snapshots[team_b]["goals_scored_avg"]
    b_gc = team_snapshots[team_b]["goals_conceded_avg"]

    a_home = venue_in_team_country(team_a, venue_city)
    b_home = venue_in_team_country(team_b, venue_city)
    home_adv = 1 if (a_home and not b_home) else 0

    venue_coords = venues[venue_city]
    a_base = training_bases[team_a]["coords"]
    b_base = training_bases[team_b]["coords"]
    a_travel = haversine(*a_base, *venue_coords)
    b_travel = haversine(*b_base, *venue_coords)

    features = pd.DataFrame([{
        "elo_diff": elo_diff,
        "adj_form_diff": 0.0,
        "home_goals_scored_avg": a_gs,
        "home_goals_conceded_avg": a_gc,
        "away_goals_scored_avg": b_gs,
        "away_goals_conceded_avg": b_gc,
        "home_advantage": home_adv,
        "home_travel_km": a_travel,
        "away_travel_km": b_travel,
    }])

    X_scaled = scaler.transform(features)
    probs = model.predict_proba(X_scaled)[0]
    classes = list(model.classes_)

    result = {
        "home_win": float(probs[classes.index("home_win")]),
        "draw":     float(probs[classes.index("draw")]),
        "away_win": float(probs[classes.index("away_win")]),
        "elo_a":    elo_a,
        "elo_b":    elo_b,
        "travel_a": a_travel,
        "travel_b": b_travel,
        "home_adv": home_adv,
    }

    if knockout:
        total = result["home_win"] + result["away_win"]
        result["home_win"] /= total
        result["away_win"] /= total
        result["draw"] = 0.0

    return result


def get_winner_label(team_a, team_b, probs):
    """Return a one-line text summary of the prediction."""
    if probs["home_win"] > probs["away_win"] and probs["home_win"] > probs["draw"]:
        return f"{team_a} favored ({probs['home_win']:.0%})"
    elif probs["away_win"] > probs["home_win"] and probs["away_win"] > probs["draw"]:
        return f"{team_b} favored ({probs['away_win']:.0%})"
    else:
        return "Match is too close to call"
