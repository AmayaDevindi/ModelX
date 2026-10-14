# Data sources (Bucket 1 output)

Fill one row per source after you've actually pulled a sample. This table becomes the
Data section of the proposal.

| Source | Owner | URL | Method (API / download / scrape) | History from | Updates | Terms / robots.txt | Gaps or problems | Sample file | Keep? |
|---|---|---|---|---|---|---|---|---|---|
| CSE – S&P SL20 prices + index | Member 1 | cse.lk | Public JSON API (unofficial, undocumented) | ? | daily | robots.txt only blocks /cgi-bin/ – still check Terms of Use | | data/raw/cse_... | |
| CBSL – T-bill / T-bond yields | Member 2 | cbsl.lk/eresearch | Data Library export | ? | weekly auctions | | | | |
| CBSL – inflation (CCPI) | Member 2 | cbsl.lk/eresearch | Data Library export | ? | monthly | | | | |
| CBSL – FD rates (AWFDR) | Member 2 | cbsl.lk/eresearch | Data Library export | ? | monthly | | | | |
| CBSL – policy rate | Member 2 | cbsl.gov.lk | Data Library / press releases | ? | ~6 weeks | | | | |
| Unit trust NAVs (5–8 funds) | Member 3 | waraka.lk or fund sites | ? | ? | daily | waraka.lk has no robots.txt – check terms | | | |
| News headlines | Member 3 | ? | RSS / API | ? | daily | | | | |

## Rough benchmark for "enough to train on"
At least 3 years of daily or weekly data for prices and rates. If a source only gives
today's value, it can still be used live, but we need another source for history.
