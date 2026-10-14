"""
Pull a snapshot of S&P SL20 stocks from the Colombo Stock Exchange.

cse.lk's own website uses a public JSON API at https://www.cse.lk/api/...
It is NOT officially documented, so endpoints and field names can change.
This script is for Bucket 1: see what we can get, save the raw output,
and note the answers in docs/data_sources.md.

Run:  python src/data/cse_pull.py
"""

import json
import time
from datetime import date
from pathlib import Path

import requests

BASE = "https://www.cse.lk/api/"
OUT = Path("data/raw/cse")
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "ModelX student project (educational)"}


def post(endpoint, data=None):
    r = requests.post(BASE + endpoint, data=data or {}, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def save(name, obj):
    path = OUT / f"{name}_{date.today()}.json"
    path.write_text(json.dumps(obj, indent=2))
    print("saved", path)


def main():
    # 1. Index level for S&P SL20 and market summary
    save("snp_index", post("snpData"))
    save("market_summary", post("marketSummery"))  # (sic) that's the real spelling

    # 2. List of S&P SL20 constituents
    constituents = post("spsl")
    save("spsl_constituents", constituents)

    # The exact shape isn't documented - print it so we can see the fields
    print("\nFirst item of constituents response:")
    print(json.dumps(constituents if not isinstance(constituents, list) else constituents[:1],
                     indent=2)[:1500])

    # 3. Company detail for each symbol (fill symbols after you see the shape above)
    #    Symbols look like "JKH.N0000".
    symbols = ["JKH.N0000"]  # start with one; add the rest once the shape is clear
    for s in symbols:
        save(f"company_{s}", post("companyInfoSummery", {"symbol": s}))
        time.sleep(1)  # be polite to their server

    # 4. Try the chart endpoint the cse.lk company page uses, to see how much
    #    PAST price history we can get. Undocumented - we just print what comes back.
    #    stockId is a number cse.lk uses internally; companyInfoSummery returns it.
    if symbols:
        info = post("companyInfoSummery", {"symbol": symbols[0]})
        stock_id = info.get("reqSymbolInfo", {}).get("id")
        print("\nstockId for", symbols[0], "=", stock_id)
        if stock_id:
            try:
                hist = post("companyChartDataByStock", {"stockId": stock_id, "period": 5})
                save(f"history_{symbols[0]}", hist)
                print(json.dumps(hist, indent=2)[:800])
            except Exception as e:
                print("history request failed:", e)

    print("\nNext: check whether any endpoint gives PAST daily prices (try 'chartData'"
          " and 'companyChartDataByStock' in the browser DevTools Network tab on a"
          " company page). Write what you find in docs/data_sources.md.")


if __name__ == "__main__":
    main()
