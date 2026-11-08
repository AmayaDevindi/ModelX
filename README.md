# ModelX 2.0 – Sri Lanka Investment Guide (working name)

A tool that helps Sri Lankans who want to invest but don't know where to start.
The investor enters their amount, risk appetite, strategy and time horizon, and the
tool shows how they could split the money across FDs, T-bills/bonds, unit trusts and
S&P SL20 stocks — with a likely return range, chance of loss, and how it compares to
just keeping it in an FD after inflation.

Educational only. Not financial advice.

## What it does
Three models feed one personal plan (details in `docs/decisions.md`, D26–D37):
1. **Customer identification** – risk questionnaire → risk band → instruments the user picks → age-based split.
2. **Fundamental analysis** – A–E health grade for each S&P SL20 company from its CSE annual and quarterly reports.
3. **News chain reaction** – headline → economic factor → sector → company, combined with the grade into an outlook.

Data comes only from Sri Lankan official or authorised sources (CBSL, CSE, Department of Census and Statistics, UTASL, local news).

## Status
See `docs/planning/status.md`. Proposal submitted. Implementation due Thu 5 Nov (moved from Sun 1 Nov).

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
src/data/        scripts that pull each data source
data/raw/        raw pulls, one file per source per day
.github/         scheduled daily refresh (CSE only; CBSL steps run from a local machine)
scripts/         local refresh script + its scheduled-task setup
```

## Getting started

```
pip install -r requirements.txt
python src/data/run_pipeline.py
```

That one command runs every data step in order and writes the clean, checked files
into `data/clean/`. Full details of each step: `docs/data_pipeline.md`.

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

## Data sources

See `docs/data_sources.md`. Every source lists how we get it, how fresh it is,
and what gives us the right to use it.

## AI use

We use Claude for planning, code help and drafting. Details in `docs/ai_use_log.md`.
