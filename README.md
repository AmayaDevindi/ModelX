# ModelX 2.0 – Sri Lanka Investment Guide (working name)

A tool that helps Sri Lankans who want to invest but don't know where to start.
The investor answers a short quiz, and the tool shows how they could split their
money across savings, FDs, T-bills/bonds, unit trusts and S&P SL20 stocks — with a
likely return range, chance of loss, and how it compares to just keeping it in an
FD after inflation.

Educational only. Not financial advice.

## What's built (this submission)

**Model 1 – risk profile → recommended split → outcome simulation**, live on the
website:
1. A short quiz (grounded in the CFA Institute's investment risk-profiling
   guidance) works out a risk profile, separately checks real investment
   knowledge, and caps how much goes into shares if that knowledge is low.
2. A Monte Carlo simulation (10,000 simulated years) turns that split into a
   likely / bad-case / good-case outcome range, a chance of ending up with less
   than you put in, and a side-by-side comparison against putting it all in a
   fixed deposit.
3. Every number traces back to a real source — CBSL rates, CBSL bill yields,
   UTASL fund performance, CSE prices — shown on request ("why these numbers?").

**Model 2 – company health clustering (reduced scope)**: groups all 23 S&P SL20
securities with k-means clustering (written by hand in plain NumPy, not a
library, so it also runs on a locked-down machine where scikit-learn's compiled
files get blocked) using five real, live features per company — price
volatility, beta against the market, board independence, whether the auditor is
a Big 4 firm, and where the price sits in its 12-month range. This is NOT the
full fundamental-analysis scoring the proposal describes (profitability,
earnings growth, debt ratios from annual report PDFs) — that needs real PDF
extraction work the team didn't have time for in this submission. Every
company's group assignment comes with a plain-words reason (e.g. "board
independence is above average"). Script: `src/model/health_cluster.py`, data
pull: `src/data/cse_company_profile_pull.py`.

**Model 3 – news chain reaction (reduced scope)**: tags each pulled headline
with an economic factor (oil, interest rates, the rupee, inflation, tourism,
tax) and a direction, then follows a fixed, written-down table of which sectors
that typically helps or hurts and why. This is the team's own common-knowledge
reasoning — NOT verified by a licensed adviser, and NOT yet tested against how
prices actually moved (that would need an event study, which needs more price
history than the one year the CSE currently gives). No LLM or FinBERT used —
plain keyword rules, per the team's own documented fallback. Script:
`src/model/news_chain.py`.

Both Model 2 and Model 3 run automatically as part of the daily pipeline
(`run_pipeline.py`) and write their output to `data/clean/`.

Data comes only from Sri Lankan official or authorised sources (CBSL, CSE, UTASL,
local news).

## Status
See `docs/planning/status.md`. Proposal submitted 19 Oct. Implementation due 10 Nov.

## Folder layout

```
docs/
  proposal/      proposal text, the built .docx and the script that builds it
  evidence/      screenshots from the data checks (18 Oct 2026)
  team-pack/     plain-English plan for the team (start with README.md)
  planning/      status, pipeline explorer
  competition/   booklet summary: dates, judging, rules
  templates/     official proposal template
  decisions.md   every decision so far – the live list
  data_sources.md  every data source: URL, method, history, terms
  ai_use_log.md  AI use, as the rules require
src/data/        scripts that pull and clean each data source
src/model/       Model 1 (assumptions, profile/quiz, simulation), Model 2
                (health_cluster.py), Model 3 (news_chain.py)
web/             the Next.js website (the PLAN page runs Model 1 in the browser)
data/raw/        raw pulls, one file per source per day
data/clean/      cleaned data the model reads
.github/         scheduled daily refresh (CSE only; CBSL steps run from a local machine)
scripts/         local refresh script + its scheduled-task setup
```

## Getting started

### Data pipeline

```
pip install -r requirements.txt
python src/data/run_pipeline.py
```

That one command runs every data step in order, writes the clean, checked files
into `data/clean/`, and finishes by writing the website's numbers to
`web/public/data/assumptions.json`. Full details of each step: `docs/data_pipeline.md`.

**One source needs a manual step first.** UTASL (unit trust prices and performance)
shows a "checking your browser" page to scripts, so two of the steps read a page you
save yourself instead of fetching it live:

1. Open https://www.utasl.lk/unit-prices/ in a normal browser, wait for the table to
   load, press Ctrl+S, save as "Webpage, HTML only" into `data/raw/utasl/manual/`.
2. Do the same for https://www.utasl.lk/performance-data/, saving into
   `data/raw/utasl/manual_performance/`.
3. Then run `python src/data/run_pipeline.py`.

If you skip this, the pipeline still runs — those two steps just print a one-line
warning and skip, and everything else still refreshes.

**Automatic refresh:** `.github/workflows/daily_refresh.yml` runs CSE on a schedule
(CSE allows requests from GitHub's servers; CBSL's firewall blocks them, so those
steps are marked optional and skip with a warning rather than stopping the pipeline).
`scripts/refresh_local.bat` is a local version of the same command for a machine that
can reach CBSL directly — see `docs/data_pipeline.md` for how to schedule it.

### Website

```
cd web
npm install
npm run dev
```

Then open http://localhost:3000 — the PLAN tab runs the quiz and shows your
recommended split and simulated outcomes. The site reads its numbers from
`web/public/data/assumptions.json`, which the data pipeline writes automatically
on every run (see above) — no code change needed when the underlying data updates.

## Data sources

See `docs/data_sources.md`. Every source lists how we get it, how fresh it is,
and what gives us the right to use it.

## AI use

We use Claude for planning, code help and drafting. Details in `docs/ai_use_log.md`.
