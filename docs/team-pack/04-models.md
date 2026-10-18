# 04 – The models and how they connect

We have three models of our own plus the forecast and simulation steps. Here's how they fit:

```
  USER                                   MARKET (pre-computed in GitHub Actions)
  ────                                   ─────────────────────────────────────────
  quiz + goal + liquidity + horizon      Forecast models (ARIMA/Prophet vs baseline)
          │                                → expected return + volatility per asset
          ▼                                → correlations between assets
  ① Investor profile model                        │
     → risk band 1–5                       ② Fundamental analysis model
     → limits for the split                  → score 0–100 per SL20 stock
          │                                  → picks the stock basket
          │                                        │
          └───────────────┬────────────────────────┘
                          ▼
                 Optimiser (inside the limits)  → THE SPLIT
                          ▼
                 Monte Carlo simulation → likely / bad / good, chance of loss,
                                          FD after inflation, monthly income
                          ▼
                 ③ News model → flags + headlines shown beside each asset
                                (context only – doesn't change the numbers, D30)
```

---

## ① Investor profile model ("customer identification") – D27
**What it does:** turns the user's answers into a risk band and a set of limits the optimiser must respect.

**Why not ML:** to train a classifier we'd need many real investors labelled with their "correct" risk level. That data doesn't exist for us. A scored quiz is how brokers profile clients anyway, it's transparent, and the user can see why they got their band.

**How:**
1. 5–6 multiple-choice questions, each answer worth 1–4 points. Topics (draft): investing experience, reaction to a 20% drop, main goal, how much of their savings this is, income stability, how soon they might need the money.
2. Total points → band: 1 Very cautious · 2 Cautious · 3 Balanced · 4 Growth · 5 Aggressive.
3. Horizon and liquidity are separate inputs and can only make the limits *stricter* (e.g. short horizon caps stocks even for a band-5 user).
4. Band → limits. **Draft only – the numbers are our design choice, to agree as a team and sanity-check with the stockbroker:**

| Band | Max in stocks | Max in equity unit trusts | Min in cash-like (savings, short FD, T-bills) |
|---|---|---|---|
| 1 | 0% | 10% | 40% |
| 2 | 10% | 20% | 25% |
| 3 | 25% | 30% | 15% |
| 4 | 40% | 40% | 10% |
| 5 | 60% | 50% | 5% |

Extra rules: needs money within 1 year → mostly cash-like; "need to withdraw early" → no long FDs/bonds beyond the horizon; goal = income → prefer interest-paying and dividend assets.

**How we check it:** walk 5–6 made-up personas through it and see if the bands make sense; ask the stockbroker to review the questions. Show the scoring rules on the site.

---

## ② Fundamental analysis model – D28 ("both")
**Input:** figures extracted from S&P SL20 companies' quarterly and annual financial statement PDFs (see 05-pdf-extraction.md) + share prices.

**Part (a) – ratio score (the one we rely on):**
1. Per company per quarter: revenue, net profit (attributable to shareholders), EPS, total assets, total equity, borrowings, dividends per share, net assets per share.
2. Ratios: P/E, P/B, dividend yield, ROE, debt-to-equity, EPS growth year on year.
3. Rank each ratio across the SL20 (percentiles), group into Value, Quality, Growth, Income, average into a 0–100 score.
4. Used in two places: the screener (score + its parts, with "data as of" and filing date), and the plan (the stock slice of the split goes to the top-scoring stocks, spread out so no single stock or sector dominates).
5. If a company's latest figures failed checks, it shows "not scored" rather than a guess.

**Part (b) – ML return model (an honest experiment):**
1. Features: the ratios above, plus recent price momentum and volatility.
2. Target: next-quarter return relative to the S&P SL20.
3. Models to try: linear regression and a small gradient-boosting model.
4. Test with walk-forward validation (train on earlier quarters, test on later ones – never shuffle time) against a baseline that predicts the historical average.
5. Expect it to be weak: 20 stocks × limited quarters is a small dataset. If it doesn't beat the baseline, we say so in the report and the plan keeps using the score only. Admitting this is scored positively ("knows what the data can't support").

---

## ③ News model – D30 (details in 06-news-linking.md)
1. Collect headlines (local sites, CSE announcements, CBSL press releases, a little global) every ~30 min.
2. **Link** each headline to what it's about: a specific SL20 company, a sector, or a macro instrument (policy rates → FDs/T-bills; inflation; rupee; oil).
3. **Score** sentiment −1 to +1 (LLM API if we get credits, otherwise FinBERT – D21).
4. **Aggregate** per asset over the last 7 days, newer news weighted more.
5. **Show** it beside the asset on the dashboard, screener and plan. If an asset in the user's split has strongly negative recent news (several articles, clearly negative), show a warning flag with the headlines. The split itself doesn't change.

---

## Forecast models – D4, D19
- Per asset series (T-bill/T-bond yields, FD rates, inflation, ASPI/S&P SL20, unit trust NAVs): try ARIMA and/or Prophet.
- Always compare with the **historical-average baseline** on a held-out recent period (error metric: MAE / RMSE).
- Use whichever wins for each asset, and say which one on the site. If neither is reliable for an asset, use the baseline and show a wide range.
- Output per asset: expected return, volatility; plus correlations between assets (from history).

## Optimiser
Mean-variance optimisation (Markowitz): find the split with the best expected return for the risk level, **inside the limits from ①**. Libraries: `scipy.optimize` in Python for testing; the live version in `/api/plan` (TypeScript) or a small Python function.

## Monte Carlo – D20
- Simulate a few thousand possible paths of the portfolio value over the user's horizon using the expected returns, volatilities and correlations.
- Report the 50th percentile (likely), 10th (bad), 90th (good), and the % of paths ending below the starting amount = chance of loss.
- Same amount in an FD minus inflation, plotted beside it. Expected monthly income from interest and dividends.
- Chart styled like TradingView's forecast cone.

## How the whole thing is evaluated (for the proposal / report)
- Forecasts: error vs the historical-average baseline on held-out data.
- Chance-of-loss calibration: backtest – for past start dates, did roughly X% of portfolios we'd have said had an X% chance of loss actually lose?
- Allocation backtest: our split vs a simple "all FD" and an equal split, over past periods.
- PDF extraction: accuracy on a hand-checked sample (see 05).
- News linking and sentiment: accuracy on ~100 hand-labelled headlines (see 06).
- If something fails, we fall back (baseline forecast, score-only stocks, "not scored", stale tag) and report it.
