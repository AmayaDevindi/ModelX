# Status
Last updated: 9 Nov 2026

**Deadline confirmed: Mon 10 Nov 2026** (was moved to 5 Nov on 3 Nov, then confirmed as 10 Nov on 9 Nov - see D49 in decisions.md). Final pitch Sat 14 Nov (confirm).
Needed: technical report, public repo with README, 2-page summary, 3-minute video on real data.

**Work split (D41):** Amaya builds the models, website and data pipeline, and pushes everything
to the repo. Chanula and Thisara write the technical report, 2-page summary and video, using
README.md and docs/decisions.md as the source of truth for what was actually built - not the
original proposal, which describes a larger system than there was time for.

| Bucket | What | Owner | Status |
|---|---|---|---|
| 1 | Data check | Member 1 / 2 | Done |
| 2 | Proposal | All | Submitted 19 Oct |
| 3 | Data pipeline (CSE, CBSL, UTASL, news) | Member 2 | Done - `python src/data/run_pipeline.py` |
| 4 | Forecast baseline + ARIMA check | Member 2 | **Done, reduced scope** (Model 4, 9 Nov) - a simplified AR(p,1,0) on 2 stocks, hand-written in NumPy (not statsmodels), backtested against a naive baseline. See D53 |
| 5 | Model 1: quiz, split, Monte Carlo, FD-after-inflation | Member 2 | **Done**, live on the website (PLAN tab) |
| 6 | Model 2: company health clustering | **Done, reduced scope** - k-means (hand-written NumPy) on governance/risk features, not the full profitability scoring. Live on the website (FA tab). See D50 |
| 7 | Model 3: news chain reaction | **Done, reduced scope** - keyword tagging + a fixed effect table, not an LLM. Live on the website (NEWS tab). See D51 |
| 8 | Website: PLAN, FA, NEWS, QUOTE (per-company pages, TradingView charts, Model 4 forecast) | Member 2 | **Done** |
| 9 | Report, 2-page summary, video, README, public repo | All | README done; report/summary/video = Chanula & Thisara's work |

See `README.md` ("What's built") and `docs/decisions.md` (D47-D53) for exactly what was built,
reduced, or cut, and why - that's the accurate picture for whoever writes the report.

## Still open (not blocking submission)
- CSE gives only ~1 year of daily price history
- No LLM/FinBERT budget confirmed (D21) - Model 3 stays rule-based
- UTASL unit trust prices need a manual save-page step before each pipeline run (see README)
