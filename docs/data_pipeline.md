# How we collect and clean data

Short guide for the team. Everything lives in `src/data/`.

## Run it

```
python src\data\run_pipeline.py
```

This runs every step below in order and stops if one fails. Raw files are saved
as they came in (`data/raw/`), and the cleaned, checked files go to `data/clean/`.
We never edit raw files by hand. Every script can be re-run safely.

Needs: requests, pandas, openpyxl, pdfplumber, lxml (all in `requirements.txt`).
No AI model is used to collect data. These are plain scripts reading public pages and files.

## Where the data comes from

| What | Site | Script | History we get |
|---|---|---|---|
| Stock prices, 23 S&P SL20 shares | cse.lk (CSE's public data) | `cse_pull.py`, `cse_history_all.py` | about 1 year, daily |
| Savings and FD rates | cbsl.gov.lk, Table 4.04 (Excel) | `cbsl_rates_pull.py` | monthly since 2003 |
| Inflation (CCPI) | cbsl.gov.lk, CCPI Excel file | `cbsl_ccpi_pull.py` | 13 months, grows each run |
| T-bill and T-bond yields | cbsl.gov.lk, Weekly Economic Indicators (PDF) | `cbsl_weekly_pull.py` | weekly, grows each run |
| USD/LKR rate | cbsl.gov.lk, daily indicative rate | `cbsl_fx_pull.py` | daily since 2015 |
| Unit trust prices (79 funds) | utasl.lk/unit-prices | `utasl_pull.py` | grows daily from 2 Nov 2026 |
| Unit trust performance (89 funds, YTD and 5-year growth) | utasl.lk/performance-data | `utasl_performance_pull.py` | monthly, September 2026 first |
| News headlines | economynext.com RSS feed | `news_pull.py` | latest 20, grows each run |

## How each kind of source is read

- **CSE:** asks the site's data service for each stock's price history, one stock at a time, with a 1 second pause.
- **CBSL Excel files:** the script finds the newest file link on the CBSL page (the date is in the file name), downloads it, and checks the column headings are what we expect before reading anything.
- **CBSL weekly PDF:** `pdfplumber` reads the text, and patterns pick out the T-bill table (13 rows) and the T-bond table (54 rows).
- **USD/LKR:** fills in CBSL's own lookup form. The first run asks for 2015 to today, later runs only ask for new days. CBSL asks for a 10 second delay, so we wait.
- **UTASL:** the page already holds the latest table, so one plain request is enough. See the note below about the browser check.
- **News:** reads the RSS feed. We keep the headline, link and date only, not the article text. It is shown as context in the app and is not used by the model.

Files that only show recent data (inflation, weekly yields, UTASL, news) are saved into a history file that gets longer each run. That is why we want the pipeline to run daily.

## Checks built into every script

Each script stops with a clear message if something looks wrong, so bad data does not slip through quietly. For example: wrong column headings, too few rows, rates outside a sensible range, months missing in a row, or a page layout that changed.

## Price anomalies (automatic, nobody checks by hand)

`check_jumps.py` looks at every daily return for every stock.

1. Take off the market's move that day, so a day when everything fell is not flagged.
2. Compare what is left with that stock's own normal size of move over the last 60 days.
3. Flag it if it is more than 8 times normal (decision D44 in `docs/decisions.md`).
4. If the price fell by a clean factor (2, 3, 4, 5 or 10) and trading volume jumped, treat it as a share split and adjust the earlier prices.
5. Anything else is only flagged and written to `adjustments_log.csv`, not changed.

Last run: 5,566 returns checked, 10 flagged. One was adjusted (ACL, divided by 3 on 29 Dec 2025). The ACL adjustment is inferred from price and volume and still needs confirming against the CSE announcement.

`make_model_inputs.py` then makes two return files: one with extreme returns capped (used for estimating average return) and one untouched (used for risk and simulation). It also gives each stock a confidence label, based on how many days of data it has.

## Things to know

- **UTASL browser check.** The UTASL site sometimes shows a "checking your browser" page to scripts. We do not work around it. If the live request fails, the script reads a page you saved by hand: open the page, Ctrl+S, choose "Webpage, HTML only", and save into `data/raw/utasl/manual/` (prices) or `data/raw/utasl/manual_performance/` (performance). If no saved page exists the step is skipped and the rest of the pipeline carries on.
- **Not used:** TradingView and waraka.lk. Their terms do not allow reusing their data, and waraka.lk only repeats UTASL's numbers anyway.
- **Respecting the sites:** all sources are public, robots.txt was checked, each script sends one small request set with a clear User-Agent, and CBSL's 10 second delay is kept.
- **Short history.** One year of CSE data is enough to estimate risk but not to forecast returns, so the model uses wide ranges and a baseline. Unit trust price history starts on 2 Nov 2026, so for returns we use UTASL's 5-year figures.
- **Dates do not line up yet.** Rates run to July 2026 while inflation runs to October 2026. The report has to say this wherever the two are compared.
- **Daily automation.** `.github/workflows/daily_refresh.yml` runs the pipeline, but it is switched off (`if: false`) until we check that GitHub's servers can reach cse.lk.

## Sources and credit

CSE (cse.lk), Central Bank of Sri Lanka (cbsl.gov.lk), Unit Trust Association of Sri Lanka (utasl.lk), EconomyNext (economynext.com). AI help used while writing these scripts is listed in `docs/ai_use_log.md`.
