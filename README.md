# ModelX 2.0 – Sri Lanka Investment Guide (working name)

A tool that helps Sri Lankans who want to invest but don't know where to start.
The investor enters their amount, risk appetite, strategy and time horizon, and the
tool shows how they could split the money across FDs, T-bills/bonds, unit trusts and
S&P SL20 stocks — with a likely return range, chance of loss, and how it compares to
just keeping it in an FD after inflation.

Educational only. Not financial advice.

## Status

| Bucket | What | Due | Status |
|---|---|---|---|
| 1 | Data check – prove every source works | Wed 14 Oct | in progress |
| 2 | Proposal | Mon 19 Oct | not started |
| 3 | Data pipeline (daily refresh) | – | not started |
| 4 | Forecast models + baseline | – | not started |
| 5 | Allocation engine + projections | – | not started |
| 6 | Website | – | not started |
| 7 | Evaluation, report, demo video | Sun 1 Nov | not started |

## Folder layout

```
docs/          brief, decisions log, data sources table, AI-use log
src/data/      scripts that pull each data source
data/raw/      raw pulls, one file per source per day
.github/       scheduled daily refresh (turned on in Bucket 3)
```

## Getting started

```
pip install -r requirements.txt
python src/data/cse_pull.py          # S&P SL20 snapshot from cse.lk
python src/data/cbsl_load.py         # loads CSVs you exported from the CBSL Data Library
python src/data/unit_trust_pull.py   # unit trust NAVs (see notes inside)
```

## Data sources

See `docs/data_sources.md`. Every source lists how we get it, how fresh it is,
and what gives us the right to use it.

## AI use

We use Claude for planning, code help and drafting. Details in `docs/ai_use_log.md`.
