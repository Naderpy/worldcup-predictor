# World Cup 2026 Predictor ⚽

A machine learning model that predicts the outcome of the 2026 FIFA World Cup, built from scratch as a first end-to-end ML project.

## What it does

- Predicts the probability of home win / draw / away win for any 2026 World Cup matchup
- Simulates the entire tournament 10,000 times (Monte Carlo) to estimate each team's chances of winning the cup
- Uses real fixtures, real venues, and real training base coordinates from FIFA's official 2026 announcement

## How it works

1. **Data**: ~21,000 international matches from 2004 to 2026
2. **Elo ratings**: computed from scratch using the World Football Elo formula
3. **Features**: Elo difference, recent form, goal-scoring averages, home advantage, travel distance from training base to venue
4. **Model**: multinomial logistic regression (60% accuracy, 0.879 log loss on a held-out test set)
5. **Tournament simulation**: official FIFA bracket including all 495 third-place qualification combinations
6. **Monte Carlo**: 10,000 full tournament simulations to produce championship probabilities

## The headline result (top 10)

| Rank | Team | Championship Probability |
|---|---|---|
| 1 | Argentina | 32.1% |
| 2 | Spain | 24.7% |
| 3 | France | 10.4% |
| 4 | Brazil | 5.9% |
| 5 | Colombia | 3.4% |
| 6 | Morocco | 3.3% |
| 7 | England | 3.0% |
| 8 | Japan | 3.0% |
| 9 | Ecuador | 2.5% |
| 10 | Portugal | 2.2% |

## Running locally

    pip install -r requirements.txt
    streamlit run app.py

## Built with

Python · scikit-learn · pandas · Streamlit

## Author

Nader Rawashdy — Electrical Engineering student at Tel Aviv University
