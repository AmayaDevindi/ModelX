# ModelX 2.0 - implementation handover for Chanula and Thisara (9 Nov 2026)

Team **Fushiguro** - Submission 2 deadline **Mon 10 Nov 2026** - Repo: https://github.com/AmayaDevindi/ModelX

Amaya has finished building and pushed everything: the data pipeline, all 4 models, and the
website. Your job now is the report, 2-page summary and video (D41) - built from what's
actually in this repo, not from the original proposal, which describes a bigger system than
there was time for. The judging rubric scores "report matches code" (engineering 25%), so
honesty about what's real, reduced, or cut matters more than sounding impressive.

## Read these two files first - they're the accurate, final picture
1. **`README.md`** - "What's built" section: exactly what each of the 4 models does, in plain words.
2. **`docs/decisions.md`**, entries **D47 to D54** - exactly what was reduced or cut from the
   original proposal, and why. Every gap between the proposal and the code is explained here.

## What's actually built, in one paragraph each

**Model 1 (full)** - a short risk quiz (CFA-style, no jargon) plus a separate knowledge check
that caps how much goes into shares if you don't have real investing experience. Produces a
personal split across savings/FDs/T-bills/unit trusts/shares, a Monte Carlo simulation (10,000
runs) giving a likely/bad/good outcome range and chance of loss, and a side-by-side comparison
against leaving the money in an FD after inflation. Live on the **PLAN** tab.

**Model 2 (reduced)** - k-means clustering (genuine unsupervised ML, written by hand in NumPy)
groups all 23 S&P SL20 companies by 5 real features: price volatility, beta, board
independence, Big 4 auditor, and position in the 12-month price range. This is NOT the full
A-E fundamental grade from annual-report PDFs the proposal described - that needed PDF
extraction work there wasn't time for (D50). Live on the **FA** tab.

**Model 3 (reduced)** - tags news headlines with an economic factor (oil, rates, the rupee,
inflation, tourism, tax) and a direction, then a fixed, hand-written table of which sectors
that helps or hurts and why. Rule-based, not an LLM/FinBERT, not backtested (D51). Live on the
**NEWS** tab.

**Model 4 (added late, 9 Nov)** - this is the "baseline-vs-ARIMA check" from the original plan,
cut on 3 Nov and finished once the deadline was confirmed as 10 Nov. A simplified AR model
(hand-written NumPy, not statsmodels/ARIMA - D53) for 2 stocks (JKH.N0000, COMB.N0000),
honestly backtested against a naive "no change" baseline - the AR model beat the baseline on
both stocks, a real result, not cherry-picked. Shown on their **QUOTE** pages with the backtest
numbers right next to the projection, so it's clear how reliable it actually was.

**Website**: PLAN, QUOTE (all 23 companies, each with a live TradingView chart), FA, NEWS are
all real and working. MKTS, RISK, ECO are shown as "soon" - not built, out of scope for this
submission (this was decided, not forgotten - see D43). No login/accounts (D43, confirmed
still cut in D54) - the site works as a guest, every plan stays in your own browser only.

## Chanula: technical report

1. Read `README.md` and `docs/decisions.md` (D47-D54) before writing anything.
2. Suggested structure, following the proposal's own sections where they still apply:
   - Problem / user / literature review - mostly unchanged from the proposal, reuse it
   - What was actually built: Models 1-4, each with what it does, what data it uses, and how
     it differs from the proposal (cite the decisions.md entry each time - this is what
     "report matches code" means)
   - Data pipeline: sources, daily refresh, cleaning and anomaly detection
     (`src/data/check_jumps.py`, D44, D45 are good material - data work is 30% of the grade)
   - Evaluation: Model 4's real backtest numbers are in
     `data/clean/price_forecast_backtest.csv` - use them, they're honest (AR beat the naive
     baseline on both stocks tested)
   - Limitations / what we'd do with more time: full Model 2 PDF-based scoring, real ARIMA,
     login, the MKTS/RISK/ECO tabs, forecasting more than 2 stocks
   - AI use disclosure: `docs/ai_use_log.md` already has a running log - keep adding to it if
     you use Claude too, the rules require this
3. Check `docs/competition/booklet-summary.md` for the exact submission format the booklet asks for.

## Thisara: 2-page summary + 3-minute video

**2-page summary**: a condensed version of the report above - problem, what was built, one
standout real insight (pick one: the FD-vs-inflation real loss number from Model 1, a notable
Model 2 grouping, or a real Model 3 tagged headline with its reasoning), and how it addresses
the judging criteria.

**Video (3 minutes), live demo, not slides**:
1. Open the site, run the PLAN quiz live, show the result - split, range, chance of loss, the
   FD-after-inflation comparison.
2. Click into QUOTE -> JKH.N0000 or COMB.N0000: show the TradingView chart, then scroll to the
   Model 4 forecast panel and say the backtest number out loud ("this model beat a naive
   guess on the last 30 days") - that's a strong, honest moment, use it.
3. Show the FA tab (Model 2 groups) and NEWS tab (Model 3 tags) briefly.
4. Close by naming what's genuine ML (the k-means clustering, the AR forecast) versus
   rule-based (the news tagging) - don't overclaim either way.

To run it yourself for recording:
```
cd web
npm install
npm run dev
```
Then open http://localhost:3000.

## If anything's unclear
Ask Amaya directly - she owns the code, data and models (D41); you two own the writing and
video. Everything you need to cite is already in the repo and dated, so you shouldn't need to
guess at any number.
