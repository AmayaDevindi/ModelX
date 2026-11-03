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
.github/         scheduled daily refresh (turned on in bucket 3)
```

## Getting started

```
pip install -r requirements.txt
python src/data/cse_pull.py          # S&P SL20 snapshot from cse.lk
python src/data/cbsl_load.py         # loads CSVs you exported from the CBSL Data Library
python src/data/unit_trust_pull.py   # unit trust prices (switching to UTASL, see D35)
```

## Data sources

See `docs/data_sources.md`. Every source lists how we get it, how fresh it is,
and what gives us the right to use it.

## AI use

We use Claude for planning, code help and drafting. Details in `docs/ai_use_log.md`.
