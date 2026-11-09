# 08 – Timeline and tasks

> **Superseded.** This was the original plan from 15 Oct. The real timeline moved a lot since (deadline changes, scope cuts). For what actually happened and the final status, see `docs/planning/status.md` and `docs/decisions.md` (D41-D53), not the table below.

Owners: [NEED: agree who leads each bucket – the proposal (section 8) needs names]

| Bucket | What | Target | Owner | Status (15 Oct) |
|---|---|---|---|---|
| 1 | Data check – prove every source works (07-data-sources.md) | Fri 16 Oct | | in progress – scripts ready, nothing run |
| 2 | Proposal, 12 sections, Google Doc / Word template | draft Sat 17, final Sun 18, **submit Mon 19 Oct** | | not started |
| 3 | Data pipeline: fetchers, PDF extraction + checks, GitHub Actions (intraday / daily / weekly), JSON output | Thu 22 Oct | | not started |
| 4 | Models: forecasts + baseline, investor profile quiz, fundamental score + ML experiment, news linking + sentiment | Mon 26 Oct | | not started |
| 5 | Optimiser + Monte Carlo + FD-after-inflation + monthly income (`/api/plan`) | Wed 28 Oct | | not started |
| 6 | Website: dashboard, plan page, trackers, unit trust explorer, SL20 screener, outlook | Fri 30 Oct | | not started |
| 7 | Evaluation, technical report, 2-page summary, 3-min video, README | **Sun 1 Nov** | | not started |

Buckets 3–6 overlap in practice – the website can start with placeholder JSON while the pipeline is built.

## Right now
1. Run the bucket 1 data checks on the laptop and write down results.
2. Create the public GitHub repo and push (private = disqualified). Everyone commits regularly from now on – judges score sustained git history.
3. Draft the proposal from the data findings. Order: data section first, then solution, evaluation, risks.

## Proposal sections (template order – don't change it)
1 Problem · 2 The user · 3 Literature review · 4 Proposed solution · 5 Data · 6 Approach & methodology · 7 System design · 8 Implementation plan · 9 Evaluation plan · 10 Risks · 11 References · 12 Team details
Aim 8–12 pages excluding cover and references. Domain tick: 01 "Cost of living and everyday economics". Each section drafted in `docs/proposal/NN-name.md`, then rewritten in our own words.

## Main risks
| Risk | Fallback |
|---|---|
| CSE gives little price history | use what we get + other permitted sources; shorter backtests, wider ranges, say so |
| PDFs too messy to extract | fewer fields, manual check list, "not scored" |
| Waraka / a news site forbids reuse | fund managers' own sites; drop that news source |
| No LLM credits | FinBERT |
| Running out of time | cut preset questions → "what changed" → fundamental ML experiment (keep the score) |
| Member unavailable | buckets documented here so anyone can pick one up |
