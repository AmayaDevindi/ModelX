# Status
Last updated: 3 Nov 2026

**Implementation deadline moved to Thu 5 Nov 2026** (was Sun 1 Nov). Final pitch Sat 14 Nov (confirm).
Needed: technical report, public repo with README, 2-page summary, 3-minute video on real data.

| Bucket | What | Owner | Target | Status |
|---|---|---|---|---|
| 1 | Data check | Member 1 / 2 | - | checked in the browser 16-18 Oct; no script has been run yet (data/raw is empty) |
| 2 | Proposal | All | 19 Oct | submitted |
| 3 | Data pipeline (CSE, CBSL, UTASL, news) | Member 1 | Wed 4 Nov | not started |
| 4 | Forecast baseline + ARIMA check | Member 2 | Wed 4 Nov | not started |
| 5 | Model 1: quiz, split, Monte Carlo, FD-after-inflation | Member 2 | Wed 4 Nov | not started |
| 6 | Website: dashboard + plan page | Member 3 | Wed 4 Nov | not started |
| 7 | Report, 2-page summary, video, README, public repo | All | Thu 5 Nov | not started |

Scope for 5 Nov is in decisions.md (D43). Model 2 for ~3 companies only if time allows.

## Next actions
1. Run the three pull scripts on the laptop and fill docs/data_sources.md
2. Email CSE about using its data endpoints
3. Turn on the daily GitHub Action (remove "if: false" in daily_refresh.yml)
