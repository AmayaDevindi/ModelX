"""
Step 8: download the daily price history of every S&P SL20 security.

It reads the constituents file we saved in Step 5 (to get each stock's id),
then asks the CSE for about 1 year of daily prices for each one.
Raw answers are saved untouched in data/raw/cse/.

Run from the ModelX folder:  python src/data/cse_history_all.py
"""

import json
import time
from datetime import date
from pathlib import Path

import requests

BASE = "https://www.cse.lk/api/"
OUT = Path("data/raw/cse")
HEADERS = {"User-Agent": "ModelX student project (educational)"}
TODAY = date.today()


def post(endpoint, data):
    r = requests.post(BASE + endpoint, data=data, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def main():
    # 1. Read the list of securities we saved earlier
    list_file = OUT / f"spsl_constituents_{TODAY}.json"
    securities = json.loads(list_file.read_text())["reqSNPIndices"]
    print(f"{len(securities)} securities in the list\n")

    done, failed = 0, []

    # 2. Ask for each one's history and save the answer
    for s in securities:
        symbol, stock_id = s["symbol"], s["id"]
        try:
            hist = post("companyChartDataByStock", {"stockId": stock_id, "period": 5})
            rows = hist.get("chartData") or []
            (OUT / f"history_{symbol}_{TODAY}.json").write_text(json.dumps(hist, indent=2))
            print(f"{symbol:12} {len(rows):4} days")
            done += 1
        except Exception as e:
            print(f"{symbol:12} FAILED: {e}")
            failed.append(symbol)
        time.sleep(1)  # be polite to the CSE's server

    print(f"\nSaved {done} files. Failed: {failed if failed else 'none'}")


if __name__ == "__main__":
    main()
