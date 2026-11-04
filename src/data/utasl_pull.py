"""
Pull the latest unit trust prices from the Unit Trust Association of Sri Lanka
(UTASL) public page https://www.utasl.lk/unit-prices/.

How it works (plain words):
  * The page already contains the newest day's table in its HTML, so one normal
    page request is enough. We do NOT call the site's hidden filter endpoint
    (it sits behind a browser check, and we do not work around checks).
  * The site only shows the latest day, so we save it and APPEND it to a growing
    history file. Run daily and the history grows (same idea as the CBSL curves).
  * robots.txt allows this page. We make one request per run, with a clear
    User-Agent.

Outputs:
  data/raw/utasl/unit_prices_<price date>.html   (untouched copy)
  data/clean/utasl_unit_prices.csv                (date, company, fund, sell, buy)
"""
import re
import sys
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

URL = "https://www.utasl.lk/unit-prices/"
HEADERS = {"User-Agent": "ModelX-student-project (educational; contact via GitHub repo)"}
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "utasl"
OUT = ROOT / "data" / "clean" / "utasl_unit_prices.csv"
EXPECTED_COLS = ["Company", "Fund Name", "Selling Price (LKR)", "Buying Price (LKR)"]


def main():
    html, m = None, None
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        html = resp.text
        m = re.search(r"Unit Trust Price on (\d{1,2} \w{3} \d{4})", html)
    except requests.RequestException as e:
        print("Live request failed:", e)

    if not m:
        # The site sometimes shows a browser check to scripts. We do not work around it.
        # Fallback: a page you saved yourself from a normal browser (Ctrl+S, "HTML only")
        # into data/raw/utasl/manual/. The newest file there is used.
        manual = sorted((RAW_DIR / "manual").glob("*.htm*"), key=lambda f: f.stat().st_mtime)
        if not manual:
            # Not fatal: the rest of the pipeline should still run.
            print("SKIPPED: live page blocked and no saved page in data/raw/utasl/manual/. "
                  "Open https://www.utasl.lk/unit-prices/ in your browser, press Ctrl+S, "
                  "save as 'Webpage, HTML only' into that folder, then run this again.")
            return
        print("Live page blocked. Using your saved page:", manual[-1].name)
        html = manual[-1].read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"Unit Trust Price on (\d{1,2} \w{3} \d{4})", html)
        if not m:
            sys.exit("FAILED: the saved file has no price table. Save the page again after it fully loads.")
    price_date = pd.to_datetime(m.group(1), format="%d %b %Y").date()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"unit_prices_{price_date}.html").write_text(html, encoding="utf-8")

    table = pd.read_html(StringIO(html), attrs={"class": "uta-table"})[0]
    if list(table.columns) != EXPECTED_COLS:
        sys.exit(f"FAILED: columns changed: {list(table.columns)}")

    df = pd.DataFrame({
        "date": price_date.isoformat(),
        "company": table["Company"].str.strip(),
        "fund": table["Fund Name"].str.strip(),
        "sell": pd.to_numeric(table["Selling Price (LKR)"], errors="coerce"),
        "buy": pd.to_numeric(table["Buying Price (LKR)"], errors="coerce"),
    })

    # Checks: enough funds, prices positive, buy not above sell.
    if len(df) < 50:
        sys.exit(f"FAILED: only {len(df)} funds found, expected 50+.")
    bad = df[df[["sell", "buy"]].isna().any(axis=1) | (df[["sell", "buy"]] <= 0).any(axis=1)]
    if len(bad):
        print(f"WARNING: dropping {len(bad)} rows with missing or non-positive prices:")
        print(bad.to_string())
        df = df.drop(bad.index)
    odd = df[df["buy"] > df["sell"] * 1.0001]
    if len(odd):
        print(f"NOTE: {len(odd)} fund(s) show buy above sell in the source (kept as published):")
        print(odd[["fund", "sell", "buy"]].to_string(index=False))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        old = pd.read_csv(OUT, dtype={"date": str})
        df = pd.concat([old[old["date"] != price_date.isoformat()], df])
    df = df.sort_values(["date", "company", "fund"]).reset_index(drop=True)
    df.to_csv(OUT, index=False)

    print(f"Price date: {price_date}  funds today: {(df['date'] == price_date.isoformat()).sum()}")
    print(f"History now covers {df['date'].nunique()} day(s). Saved {OUT}")


if __name__ == "__main__":
    main()
