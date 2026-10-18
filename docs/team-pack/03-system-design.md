# 03 – System design

## Big picture

```
 SOURCES                      PIPELINE (Python, GitHub Actions)              WEBSITE (Next.js on Vercel)
 ───────                      ─────────────────────────────────              ───────────────────────────
 CSE prices & announcements ─┐
 CSE financial statement PDFs┤   1. fetch      (scheduled jobs)
 CBSL rates / inflation PDFs ┤   2. extract    (PDF → numbers, D29)          dashboard + trackers
 Bank FD & savings rates     ┼─► 3. clean + check                    ──►     read the JSON files
 Unit trust NAVs             ┤   4. models     (forecasts, fundamental       │
 News RSS feeds              ┘                   score, news linking)        ▼
                                 5. write JSON  data/*.json + "as_of"      user fills the form
                                 6. git commit  (history = proof)                 │
                                                                                  ▼
                                                                    /api/plan  (Vercel function)
                                                                    quiz score → limits
                                                                    optimiser → split
                                                                    Monte Carlo → range, chance of loss,
                                                                    FD after inflation, monthly income
                                                                    (instant, < 1–2 s)
```

## What "real time" means for us (D25)
We don't have (and can't afford) a live tick feed. Instead:

| Data | How often | Why |
|---|---|---|
| CSE prices (SL20, ASPI, S&P SL20 index) | about every 30 min during trading hours [NEED: confirm CSE trading hours] | Prices move during the day |
| News + sentiment | about every 30 min | Headlines are the fastest-moving input |
| FD / savings rates, T-bill & T-bond yields, USD/LKR, unit trust NAVs | daily | They change at most daily (T-bills weekly at auction) |
| CCPI inflation | when CBSL/DCS publish (monthly) | Monthly series |
| Financial statement PDFs (fundamentals) | daily check for new filings | Quarterly, but filing dates vary |
| Model retraining (forecasts, fundamental ML) | weekly | Monthly/daily series don't need more |

The **user's result is instant**: all the heavy work (training, extraction, scoring) is done ahead of time and saved as JSON. When someone presses "Build my plan", a small Vercel function only does the cheap maths (quiz score, optimiser, a few thousand Monte Carlo paths).

Every panel shows "data as of …". If a source failed today, the panel shows the last good value with its older date and a "stale" tag – it never pretends to be fresh. This is how we "fail safely".

## Why this setup
- **GitHub Actions** runs the Python on a schedule for free and every data update is a commit → visible, sustained git history (judges score this).
- **Vercel** hosts the Next.js site for free and runs the small `/api/plan` function.
- **No database for 1 Nov** – JSON files in the repo are enough for our data size.

## Things to watch (check before building)
- Scheduled GitHub Actions can start a few minutes late – fine for us, just don't promise exact times.
- Each commit to the main branch triggers a Vercel redeploy. Committing data every 30 min may hit Vercel's free-plan deploy limits [NEED: check current limits]. Option: write data to a separate `data` branch and have the site fetch the JSON from there (raw GitHub URL or jsDelivr) so data updates don't redeploy the site.
- Vercel's own cron on the free plan is limited, so scheduling stays in GitHub Actions.
- Python on Vercel works, but keep `/api/plan` light. Simplest: write it in TypeScript so the whole site is one language; the Python models only produce JSON.

## Repo layout (planned)
```
ModelX/
  pipeline/            Python
    fetch/             one file per source (cse.py, cbsl.py, banks.py, unit_trusts.py, news.py)
    extract/           pdf_tables.py, pdf_ocr.py, statement_parser.py
    models/            forecast.py, baseline.py, fundamental.py, news_link.py, sentiment.py
    checks/            data quality checks
    run_intraday.py    prices + news
    run_daily.py       rates, NAVs, PDFs
    run_weekly.py      retrain models
  data/                JSON output, each file has "as_of" and "source"
    raw/               original PDFs/pages we downloaded (for evidence)
  web/                 Next.js app
    app/               pages: dashboard, trackers, unit-trusts, screener, outlook, plan
    app/api/plan/      the instant calculation
  .github/workflows/   intraday.yml, daily.yml, weekly.yml
  docs/                decisions.md, data_sources.md, ai_use_log.md, proposal/
```

## JSON shape (example – values are placeholders, not real data)
```json
{
  "as_of": "2026-10-20T10:30:00+05:30",
  "source": "https://www.cse.lk/...",
  "status": "ok",
  "items": [
    { "symbol": "XXXX.N0000", "price": 0.0, "change_pct": 0.0 }
  ]
}
```
`status` is `ok`, `stale` (using last good value) or `missing`.
