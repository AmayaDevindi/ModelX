"""
Pull the CBSL daily indicative USD/LKR spot rate (LKR per 1 USD).

Source: CBSL lookup form on
https://www.cbsl.gov.lk/en/rates-and-indicators/exchange-rates/daily-indicative-usd-spot-exchange-rates
(robots.txt allows /cbsl_custom/; CBSL asks for a 10 second crawl delay, so we wait 10 s.)

First run asks for 2015-01-01 up to today (one request). Later runs only ask
for the days after the newest one we already hold, and append.

Output: data/clean/cbsl_usdlkr.csv  (date, usd_lkr)
"""
import sys
import time
from datetime import date, timedelta
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

URL = "https://www.cbsl.gov.lk/cbsl_custom/exrates/exrates_results_spot_mid.php"
HEADERS = {"User-Agent": "ModelX-student-project (educational; contact via GitHub repo)"}
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "cbsl"
OUT = ROOT / "data" / "clean" / "cbsl_usdlkr.csv"
FIRST_DAY = date(2015, 1, 1)


def main():
    old = pd.read_csv(OUT, dtype={"date": str}) if OUT.exists() else None
    start = FIRST_DAY if old is None else date.fromisoformat(old["date"].max()) + timedelta(days=1)
    end = date.today()
    if start > end:
        print("Already up to date.")
        return

    time.sleep(10)  # CBSL crawl-delay
    resp = requests.post(URL, headers=HEADERS, timeout=120, data={
        "lookupPage": "lookup_daily_exchange_rates.php", "startRange": "2006-11-11",
        "rangeType": "dates", "txtStart": start.isoformat(), "txtEnd": end.isoformat(),
        "chk_cur[]": "USD~US Dollar", "submit_button": "Submit"})
    resp.raise_for_status()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"usdlkr_{end}.html").write_text(resp.text, encoding="utf-8")

    try:
        t = pd.read_html(StringIO(resp.text))[0]
    except ValueError:
        if old is not None:
            print("No new rows (weekend/holiday?). Keeping existing file.")
            return
        sys.exit("FAILED: no table in reply on first run.")

    cols = list(t.columns)
    if cols[0] != "Date" or "USD" not in cols[1]:
        sys.exit(f"FAILED: columns changed: {cols}")
    new = pd.DataFrame({"date": pd.to_datetime(t["Date"]).dt.strftime("%Y-%m-%d"),
                        "usd_lkr": pd.to_numeric(t[cols[1]], errors="coerce")})
    new = new.dropna()
    if not new["usd_lkr"].between(100, 600).all():
        sys.exit("FAILED: USD/LKR value outside 100-600. Check the raw reply.")
    if old is None and len(new) < 1000:
        sys.exit(f"FAILED: only {len(new)} rows for a 2015+ request.")

    df = new if old is None else pd.concat([old, new])
    df = df.drop_duplicates("date").sort_values("date").reset_index(drop=True)
    jump = df["usd_lkr"].pct_change().abs()
    big = df[jump > 0.10]
    if len(big):
        print(f"NOTE: {len(big)} day(s) moved more than 10% (real in 2022 devaluation; check others):")
        print(big.tail(5).to_string(index=False))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Added {len(new)} row(s). File now {len(df)} days, {df['date'].min()} to {df['date'].max()}. Latest: {df['usd_lkr'].iloc[-1]}")


if __name__ == "__main__":
    main()
