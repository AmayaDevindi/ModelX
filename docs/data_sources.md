# Data sources (Bucket 1 output)

Fill one row per source after you've actually pulled a sample. This table becomes the
Data section of the proposal.

| Source | Owner | URL | Method (API / download / scrape) | History from | Updates | Terms / robots.txt | Gaps or problems | Sample file | Keep? |
|---|---|---|---|---|---|---|---|---|---|
| CSE – S&P SL20 prices + index | Member 1 | cse.lk | Public JSON API (unofficial, undocumented) | ? | daily | robots.txt checked 15 Oct: only blocks /cgi-bin/ – still check Terms of Use | No documented history endpoint (the MIT-licensed `cse-lk` Python client lists 21 endpoints, none for past prices). cse_pull.py now tries `companyChartDataByStock`. If it fails, history is the biggest data risk | data/raw/cse_... | |
| CBSL – T-bill / T-bond yields | Member 2 | cbsl.lk/eresearch | Data Library export | ? | weekly auctions | | | | |
| CBSL – inflation (CCPI) | Member 2 | cbsl.lk/eresearch | Data Library export | ? | monthly | | | | |
| CBSL – FD rates (AWFDR) | Member 2 | cbsl.lk/eresearch | Data Library export | ? | monthly | | | | |
| CBSL – policy rate | Member 2 | cbsl.gov.lk | Data Library / press releases | ? | ~6 weeks | | | | |
| Unit trust NAVs (5–8 funds) | Member 3 | waraka.lk or fund sites | ? | ? | daily | waraka.lk has no robots.txt – check terms | | | |
| News headlines | Member 3 | ? | RSS / API | ? | daily | | | | |

## Rough benchmark for "enough to train on"
At least 3 years of daily or weekly data for prices and rates. If a source only gives
today's value, it can still be used live, but we need another source for history.

## Bucket 1 checklist (run on your own laptop – Claude's sandbox can't reach .lk sites)
1. `python src/data/cse_pull.py` – does the history request print dates + prices? How far back?
2. CBSL Data Library – export the 5 series in cbsl_load.py, then `python src/data/cbsl_load.py`
3. waraka.lk – find the JSON feed in DevTools (steps in unit_trust_pull.py) and read their terms
4. Pick a news source with RSS (e.g. EconomyNext, Daily FT) and check its terms
5. Fill every "?" above, then commit: `git add docs data && git commit -m "data: bucket 1 results"`

## Bucket 1 results – browser checks, 16–17 Oct 2026 (done with Claude in the browser; re-run the scripts to save raw files)
- **CSE**: `snpData` (S&P SL20 = 5,738.83), `aspiData` (ASPI = 20,185.05) and `spsl` (23 securities) all work. `companyChartDataByStock` with `stockId` (JKH = 297) and `period=5` gives ~1 year of daily bars (241 rows, 21 Oct 2025 – 16 Oct 2026); periods 6+ return only a week. Index history: `chartData` with `chartId` 1 (ASPI) or 40 (S&P SL20), `period=5` → 240 daily values; longer periods return `[]`. **History = ~1 year only.** robots.txt blocks only /cgi-bin/. Terms of use for the data endpoints still not found – email CSE.
- **CBSL Data Library**: reachable. Monthly series available: CCPI(2021=100) headline/core, AWFDR, AWNFDR, LCB 1-yr FD rates min/max, LCB savings rates min/max, NSB FD and savings rates; Treasury Bills / Treasury Bonds / Share Market Data subjects exist. Web form only (no API) – export CSV.
- **Unit trusts**: use UTASL (utasl.lk/unit-prices), not Waraka. Daily buying/selling prices for ~65–80 funds, latest 15 Oct 2026; site history from Jan 2026 (fewer funds then). Data via WordPress AJAX `filter_financial_data` (post_type=unit_price, date=YYYY-MM-DD). robots.txt allows all.
- **News**: EconomyNext RSS https://economynext.com/feed/ works (20 items, latest 17 Oct 2026); robots.txt blocks only /wp-admin/.

## Script results – cse_pull.py run by Amaya on her laptop, 3 Nov 2026
- First real run of the script (data/raw/cse/ was empty before). All five requests worked; files saved with date 2026-11-03.
- S&P SL20 index 5,722.57 on 3 Nov (day range 5,697.55 – 5,736.53). Constituents list has 23 securities (20 companies plus non-voting shares).
- JKH daily history: 243 rows, 4 Nov 2025 to 3 Nov 2026 (about 1 year, as found on 16 Oct). Fields h, l, p, q, s, t, id are filled; o, c, pc, n are empty in every row.
- Timestamps (t) are milliseconds since 1970, set to midnight Sri Lanka time. Field meanings (h=high, l=low, p=price/close, q=volume) are our reading and still to be checked against cse.lk.
- 3 Nov, cse_history_all.py: history saved for all 23 securities. 21 have 243 daily rows (4 Nov 2025 to 3 Nov 2026); ACL has 238 and NDB 242 (days with no trade have no row).
- 3 Nov, clean_cse_prices.py: combined into data/clean/cse_prices.csv (243 days x 23 securities). Gaps filled by carrying the last price forward (5 days for ACL, 1 for NDB). Data as of 2026-11-03.
- To check: ACL's price falls by about two thirds on 2025-12-29 (log return -1.11, price ratio about 0.33); looks like a share split not adjusted in the prices. NDB falls 15% on 2026-04-07. Check both against CSE announcements before using them.
- 3 Nov, check_jumps.py: flags any one-day move over 15%. ACL on 2025-12-29 (price ratio 0.329, volume about 16x) treated as a 3-for-1 split and earlier prices divided by 3 (still to confirm against the CSE announcement). NDB on 2026-04-07 (ratio 0.849, volume about 5x) flagged only, not adjusted. Output: data/clean/cse_prices_adjusted.csv and data/clean/adjustments_log.csv.
- 3 Nov, check_jumps.py updated to the per-stock yardstick method (decision D44). Replaces the fixed 15% limit described above; ACL and NDB are still the two clearest cases.
- 3 Nov, CBSL Data Library monthly export (Amaya, files read by Claude): CCPI(2021=100) headline year-on-year runs Feb 2023 to Oct 2026 (latest 8.3%) and is current. The deposit-rate series are NOT current: AWFDR ends Mar 2024, AWNFDR and AWNDR end Feb 2024, savings rate (min) and the NSB and licensed-bank one-year FD rates end Jan-Feb 2024 (the second export confirmed this; it starts Jan 2022). The files are HTML tables saved with an .xls name, so they are read with pandas read_html, not read_excel.
- Current FD rates therefore come from CBSL PDFs instead: Monetary Policy Review Table 04 (monthly AWNFDR, AWFDR, AWNDR; MPR 02/2026 reaches end Feb 2026) and the Weekly Economic Indicators (weekly T-bill yields, AWPR). Values read from these PDFs must be checked by hand against the PDF before use.
- 3 Nov, BETTER SOURCE FOR RATES: CBSL Statistical Tables, Monetary Sector, "4.04 Interest Rates - Monthly (2003 to latest)", a real .xlsx file: https://www.cbsl.gov.lk/sites/default/files/cbslweb_documents/statistics/sheets/table4.04_20261012.xlsx (page: https://www.cbsl.gov.lk/en/statistics/statistical-tables/monetary-sector). Downloaded and read by Claude on 3 Nov 2026 and saved as data/raw/cbsl/table4.04_20261012.xlsx. 283 monthly rows, Jan 2003 to Jul 2026 (latest official month). Holds: OPR (from Nov 2024), SDFR, SLFR, bank rate, T-bill 3-month and 12-month primary yields, FD rates by tenor (3/6/12/24 months), savings, AWDR, AWFDR, AWNDR and AWNFDR (both from Apr 2014), AWPR and lending rates. Replaces the Data Library export for deposit rates (the Data Library series stop in early 2024). The file name carries the publication date, so the link changes when CBSL updates it; the script must find the current link on the page. robots.txt and terms for cbsl.gov.lk still to be noted.
- Latest values in that table (Jul 2026): AWNFDR 8.83%, AWFDR 9.20%, AWDR 7.39%, T-bill 3-month 9.86% and 12-month 10.20%, OPR 8.75%. CCPI headline year-on-year: 7.3% (Jul), 8.0% (Aug), 8.0% (Sep), 8.3% (Oct). The proposal's illustration (AWNFDR 6.5-7.0% against 8.0% inflation) used Q1 2026 rates, so the FD-after-inflation insight must be recomputed with the newest rates before it is quoted again.
- Still not covered by an Excel source: T-bond yields, weekly T-bill yields (weekly PDFs only: https://www.cbsl.gov.lk/en/statistics/economic-indicators/weekly-indicators), CCPI back to 2013 (check Real Sector, Prices, Wages and Employment tables).
- 3 Nov, cbsl_rates_pull.py: automatic pull of CBSL table 4.04. It reads the Monetary Sector page, finds the newest table4.04_YYYYMMDD.xlsx link, downloads it once (skips if already saved), checks the column headers still match, and writes data/clean/cbsl_rates_monthly.csv (283 months, 2003-01 to 2026-07, data as of 2026-07). robots.txt for cbsl.gov.lk (checked 3 Nov): no rule blocks the statistics pages or files for general crawlers; Crawl-delay is 10 seconds, which the script respects (one 10 s wait between its two requests, at most one run per day). Tested from Claude's environment, not yet run on Amaya's laptop. Added to run_pipeline.py.
- 3 Nov, more CBSL sources found and checked by Claude (same site, same robots.txt rules: no block, 10 s crawl delay):
  - Inflation: "CCPI and CCPI Core" Excel (2021=100) on https://www.cbsl.gov.lk/en/statistics/statistical-tables/real-sector/prices-wages-employment, file CCPI_and_CCPI_CORE_20261030_e.xlsx. Holds only the latest 13 months (Oct 2025 to Oct 2026): headline year-on-year 8.3% in Oct 2026, core 5.6%. Matches the Weekly Indicators text. Longer history (Feb 2023 on) is the Data Library export Amaya made.
  - T-bill and T-bond auction results: Excel files on https://www.cbsl.gov.lk/en/statistics/statistical-tables/fiscal-sector (Treasury_Bill_Auctions, weekly from 1996; Treasury_Bond_Auctions from 1997) but both files were last updated 24 Dec 2025 (T-bill data to 28 Nov 2025, T-bond to 1 Dec 2025). Usable for history only, not for current yields.
  - Current T-bill and T-bond yields: CBSL Weekly Economic Indicators PDF (https://www.cbsl.gov.lk/en/statistics/economic-indicators/weekly-indicators, e.g. WEI_20261030_e.pdf). Tables 3.5 (T-bill two-way quotes, 1 week to 12 months) and 3.6 (T-bond two-way quotes by series) extract cleanly as text (pdftotext -layout); 30 Oct 2026: T-bill 3-month 9.33% / 12-month 10.00% (buying yield), T-bond yields rise from about 9.5% (Dec 2026 maturity) to about 13.1% (2045). The exchange-rate page of the same PDF extracts badly; use another source for USD/LKR.
- 3 Nov, cbsl_ccpi_pull.py and cbsl_weekly_pull.py added (both in run_pipeline.py). CCPI: downloads the CBSL inflation Excel and adds new months to data/clean/cbsl_ccpi_history.csv (the file only holds 13 months, so our own history grows over time). Weekly: finds the newest Weekly Economic Indicators PDF, reads Table 3.5 (13 T-bill maturities) and Table 3.6 (54 T-bond series, as of 30 Oct 2026) with pdfplumber, checks counts and ranges, and appends each week to data/clean/cbsl_tbill_curve.csv and cbsl_tbond_curve.csv. Needs the pdfplumber package (added to requirements.txt). Tested from Claude's environment; values for 30 Oct 2026 match the text of the PDF (T-bill 3-month 9.33%, 12-month 10.00%; T-bond 11.25%2026A 9.45%, 12.50%2045A 13.13%).

## UTASL unit trust prices (added 3 Nov 2026)
- Source: https://www.utasl.lk/unit-prices/ (robots.txt allows all). Script: `src/data/utasl_pull.py`.
- The page's own HTML holds the latest day's table (79 funds, buy and sell price). One plain request per run.
- The site's filter endpoint (admin-ajax) is behind a "Checking your browser" gate. We do not work around it, so older dates are not pulled.
- Consequence: history only grows from the first run (first price date 2 Nov 2026). Daily runs build it up. For the report we state this as a limit; unit trust risk and return in the model use the proposal's evidence and the CSE equity data until enough days exist.
- Source quirk: CAL Balanced Fund and CAL Quant Equity Fund show buy above sell on 2 Nov. Kept as published.
- To do: ask UTASL (contact page) about licence terms and a history file.

## UTASL monthly performance (added 3 Nov 2026)
- Source: https://www.utasl.lk/performance-data/ . Script: `src/data/utasl_performance_pull.py`.
- Table "Performance Report of <month>": fund, category, company, YTD %, 5-year CAGR %. First report: September 2026 (89 funds, 62 with a 5-year figure).
- Same access rule as the price page: one plain request; if a browser check appears we do not bypass it, we read a page saved by hand into `data/raw/utasl/manual_performance/`.
- Use in the model: category medians give the return and risk-level evidence for unit trusts (5-year CAGR is a point estimate, not a range, so we show it as a band and say so).
- Not used: waraka.lk (terms forbid reproducing or deriving from its content; it only re-publishes UTASL data).

## CBSL USD/LKR and news headlines (added 3 Nov 2026)
- USD/LKR: CBSL daily indicative spot rate via its lookup form (`src/data/cbsl_fx_pull.py`). robots.txt allows `/cbsl_custom/`; 10 s crawl delay respected. First run pulls 2015 to today (2,856 days in test), later runs append only new days. The 9 Mar 2022 jump (about 203 to 229.5) is the real float, not an error.
- News: EconomyNext RSS (`src/data/news_pull.py`), robots.txt allows the feed. We store title, link, date only (no article text). Used as on-screen context, not as a model input.
