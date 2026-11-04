"""
Pull UTASL's monthly unit trust PERFORMANCE table (YTD % and 5-year CAGR %)
from https://www.utasl.lk/performance-data/.

Same approach as utasl_pull.py: one plain request; if the site shows a browser
check we do not work around it, we read a page you saved yourself instead
(Ctrl+S, "Webpage, HTML only") into data/raw/utasl/manual_performance/.

The page shows one month's report ("Performance Report of September 2026").
Each run appends that month to a history file.

Outputs:
  data/raw/utasl/performance_<report month>.html
  data/clean/utasl_performance.csv  (report_month, fund, category, company, ytd_pct, cagr5_pct)
"""
import re
import sys
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

URL = "https://www.utasl.lk/performance-data/"
HEADERS = {"User-Agent": "ModelX-student-project (educational; contact via GitHub repo)"}
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "utasl"
OUT = ROOT / "data" / "clean" / "utasl_performance.csv"
EXPECTED_COLS = ["Fund Name", "Category", "Management Company", "YTD (%)", "5 Yr CAGR (%)"]
TITLE = r"Performance Report of (\w+ \d{4})"


def main():
    html, m = None, None
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        html = resp.text
        m = re.search(TITLE, html)
    except requests.RequestException as e:
        print("Live request failed:", e)

    if not m:
        manual = sorted((RAW_DIR / "manual_performance").glob("*.htm*"),
                        key=lambda f: f.stat().st_mtime)
        if not manual:
            print("SKIPPED: live page blocked and no saved page in data/raw/utasl/manual_performance/. "
                  "Open https://www.utasl.lk/performance-data/ in your browser, Ctrl+S, "
                  "'Webpage, HTML only', save into that folder, run this again.")
            return
        print("Live page blocked. Using your saved page:", manual[-1].name)
        html = manual[-1].read_text(encoding="utf-8", errors="ignore")
        m = re.search(TITLE, html)
        if not m:
            sys.exit("FAILED: saved file has no performance table. Save again after the page fully loads.")

    month = pd.to_datetime(m.group(1), format="%B %Y").strftime("%Y-%m")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"performance_{month}.html").write_text(html, encoding="utf-8")

    table = pd.read_html(StringIO(html))[0]
    if list(table.columns) != EXPECTED_COLS:
        sys.exit(f"FAILED: columns changed: {list(table.columns)}")

    df = pd.DataFrame({
        "report_month": month,
        "fund": table["Fund Name"].str.strip(),
        "category": table["Category"].str.strip(),
        "company": table["Management Company"].str.strip(),
        "ytd_pct": pd.to_numeric(table["YTD (%)"], errors="coerce"),
        "cagr5_pct": pd.to_numeric(table["5 Yr CAGR (%)"], errors="coerce"),
    })

    if len(df) < 50:
        sys.exit(f"FAILED: only {len(df)} funds, expected 50+.")
    if df["ytd_pct"].isna().mean() > 0.2:
        sys.exit("FAILED: too many missing YTD values; layout may have changed.")
    wild = df[(df["ytd_pct"].abs() > 100) | (df["cagr5_pct"].abs() > 100)]
    if len(wild):
        print(f"NOTE: {len(wild)} row(s) with returns beyond +/-100% (check):")
        print(wild[["fund", "ytd_pct", "cagr5_pct"]].to_string(index=False))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        old = pd.read_csv(OUT, dtype={"report_month": str})
        df = pd.concat([old[old["report_month"] != month], df])
    df = df.sort_values(["report_month", "category", "fund"]).reset_index(drop=True)
    df.to_csv(OUT, index=False)

    cur = df[df["report_month"] == month]
    print(f"Report month: {month}  funds: {len(cur)}  with 5-yr CAGR: {cur['cagr5_pct'].notna().sum()}")
    print(cur.groupby("category")[["ytd_pct", "cagr5_pct"]].median().round(2).to_string())
    print(f"History covers {df['report_month'].nunique()} month(s). Saved {OUT}")


if __name__ == "__main__":
    main()
