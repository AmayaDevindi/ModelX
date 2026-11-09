# ModelX – Sri Lanka Investment Guide
 
A tool for Sri Lankans who want to invest but don't know where to start.
 
You answer a short quiz, and the tool shows how you could split your money across savings, fixed deposits (FDs), T-bills/bonds, unit trusts and S&P SL20 stocks. For that split it shows a likely return range, the chance of losing money, and how it compares with just keeping everything in an FD after inflation.
 
Educational only. Not financial advice.
 
## What's in it
 
### Model 1 – risk profile, recommended split, outcome simulation
 
1. A short quiz, based on the CFA Institute's guidance on investment risk profiling, works out a risk profile. It checks investment knowledge separately, and if that knowledge is low it caps how much can go into shares.
2. A Monte Carlo simulation (10,000 simulated years) turns the split into a likely / bad-case / good-case range, the chance of ending up with less than you put in, and a side-by-side comparison with a fixed deposit.
3. Every number traces back to a real source (CBSL rates, CBSL bill yields, UTASL fund performance, CSE prices). You can see them under "why these numbers?".
### Model 2 – company health clustering
 
Groups all 23 S&P SL20 securities with k-means, using five features per company: price volatility, beta against the market, board independence, whether the auditor is a Big 4 firm, and where the price sits in its 12-month range. Each company's group comes with a plain-words reason (for example "board independence is above average").
 
k-means is written by hand in NumPy instead of using scikit-learn, so it also runs on locked-down machines that block scikit-learn's compiled files.
 
Limits: this is not a full fundamental analysis. It doesn't use profitability, earnings growth or debt ratios from annual reports, because that needs PDF extraction that isn't built yet.
 
Script: `src/model/health_cluster.py`. Data pull: `src/data/cse_company_profile_pull.py`.
 
### Model 3 – news chain reaction
 
Tags each pulled headline with an economic factor (oil, interest rates, the rupee, inflation, tourism, tax) and a direction, then follows a fixed, written-down table of which sectors that usually helps or hurts, and why.
 
Limits: the table is our own common-knowledge reasoning. It has not been checked by a licensed adviser and has not been tested against how prices actually moved (that needs an event study, and the CSE only gives about one year of price history). No LLM or FinBERT is used, just keyword rules.
 
Script: `src/model/news_chain.py`.
 
### Model 4 – price forecast baseline
 
For two liquid blue chips (`JKH.N0000`, `COMB.N0000`), fits a simplified ARIMA(p, 1, 0): an autoregressive model on the first-differenced log price, with no moving-average term. It is written by hand in NumPy because statsmodels ships even more compiled extensions than scikit-learn. The order p is chosen by BIC on training data only, so the backtest isn't tuned to look good.
 
It is backtested on a 30-day holdout against a naive "no change" baseline. On both stocks the AR model beat the baseline. It also gives a forward 30-day projection with a widening confidence band, shown on the QUOTE page.
 
Limits: it is not a full statsmodels ARIMA (no MA term, no formal stationarity tests), it covers only 2 of 23 companies, and it is checked on about 240 days of price history. Treat it as a simple, honestly validated baseline, not a trading signal. See `docs/decisions.md` (D53).
 
Script: `src/model/price_forecast.py`.
 
### Website
 
Next.js site with these tabs:
 
- **PLAN** – the quiz, recommended split and simulated outcomes (Model 1 runs in the browser)
- **FA** – company groups from Model 2
- **NEWS** – the news chain reaction from Model 3
- **QUOTE** – one page per S&P SL20 company, with its live TradingView chart, our own pulled price history next to it, the company's Model 2 group and reasoning, and the Model 4 forecast for the 2 stocks it covers
The CSE has an official TradingView data partnership, so the same symbols used elsewhere in the project work there directly (for example `CSELK:JKH.N0000`). TradingView is only a chart embed for looking around. None of the model numbers come from it.
 
Models 2, 3 and 4 run as part of the daily pipeline (`run_pipeline.py`) and write their output to `data/clean/`.
 
The MKTS, RISK and ECO tabs are placeholders marked "soon".
 
## Data sources
 
Data comes only from Sri Lankan official or authorised sources: CBSL, CSE, UTASL and local news. See `docs/data_sources.md` for each source's URL, how we get it, how much history it has, and the terms of use.
 
## Folder layout
 
```
docs/
  proposal/        original proposal text
  evidence/        screenshots from the data checks
  team-pack/       plain-English plan for the team
  planning/        status, pipeline explorer
  templates/       proposal template
  decisions.md     every decision so far
  data_sources.md  every data source: URL, method, history, terms
  ai_use_log.md    how AI was used
src/data/          scripts that pull and clean each data source
src/model/         Model 1 (assumptions, profile/quiz, simulation),
                   Model 2 (health_cluster.py), Model 3 (news_chain.py),
                   Model 4 (price_forecast.py)
web/               the Next.js website
data/raw/          raw pulls, one file per source per day
data/clean/        cleaned data the models read
.github/           scheduled daily refresh (CSE only; CBSL steps run locally)
scripts/           local refresh script and its scheduled-task setup
```
 
## Getting started
 
### Data pipeline
 
```
pip install -r requirements.txt
python src/data/run_pipeline.py
```
 
This runs every data step in order, writes the cleaned, checked files into `data/clean/`, and finishes by writing the website's numbers to `web/public/data/assumptions.json`. Details of each step are in `docs/data_pipeline.md`.
 
**One source needs a manual step first.** UTASL (unit trust prices and performance) shows a "checking your browser" page to scripts, so two steps read a page you save yourself:
 
1. Open https://www.utasl.lk/unit-prices/ in a normal browser, wait for the table to load, press Ctrl+S and save as "Webpage, HTML only" into `data/raw/utasl/manual/`.
2. Do the same for https://www.utasl.lk/performance-data/, saving into `data/raw/utasl/manual_performance/`.
3. Run `python src/data/run_pipeline.py`.
If you skip this, the pipeline still runs. Those two steps print a one-line warning and are skipped, and everything else refreshes as normal.
 
**Automatic refresh:** `.github/workflows/daily_refresh.yml` runs the CSE steps on a schedule. CSE allows requests from GitHub's servers, but CBSL's firewall blocks them, so the CBSL steps are marked optional and skip with a warning instead of stopping the pipeline. `scripts/refresh_local.bat` is a local version for a machine that can reach CBSL directly. `docs/data_pipeline.md` explains how to schedule it.
 
### Website
 
```
cd web
npm install
npm run dev
```
 
Then open http://localhost:3000. The site reads its numbers from `web/public/data/assumptions.json`, which the pipeline rewrites on every run, so no code change is needed when the data updates.
 
## Known limits
 
- The CSE gives only about one year of daily price history.
- UTASL prices need the manual save-page step above before each pipeline run.
- Model 3 is rule-based and not backtested.
- Model 2 uses governance and market-risk features only, not company financials.
- Model 4 covers 2 of the 23 companies.
