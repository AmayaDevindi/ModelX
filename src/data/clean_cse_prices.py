"""
Step 9: combine every company's saved history into ONE table.
One row per trading day, one column per company, values = closing price.
Saves it to data/clean/cse_prices.csv.

Run from the ModelX folder:  python src/data/clean_cse_prices.py
"""

import json
from datetime import date
from pathlib import Path

import pandas as pd

RAW = Path("data/raw/cse")
CLEAN = Path("data/clean")
CLEAN.mkdir(parents=True, exist_ok=True)
TODAY = date.today()


def load_one(path):
    """Read one saved history file and return a column of prices indexed by date."""
    rows = json.loads(path.read_text())["chartData"]
    df = pd.DataFrame(rows)
    df["date"] = (
        pd.to_datetime(df["t"], unit="ms", utc=True)
        .dt.tz_convert("Asia/Colombo")
        .dt.date
    )
    return df.set_index("date")["p"]


def main():
    # 1. Load every history file for today, one column per symbol
    columns = {}
    for path in sorted(RAW.glob(f"history_*_{TODAY}.json")):
        symbol = path.name.split("_")[1]          # e.g. "JKH.N0000"
        columns[symbol] = load_one(path)

    prices = pd.DataFrame(columns)                # lines the columns up by date
    prices = prices.sort_index()
    print("Table shape (days, companies):", prices.shape)

    # 2. Find the gaps: a day where some company has no price
    missing = prices.isna().sum()
    missing = missing[missing > 0]
    print("\nGaps before filling (days with no price):")
    print(missing if len(missing) else "none")

    # 3. Fill each gap with the last known price.
    #    No trade that day means the price did not change, so we carry it forward.
    prices = prices.ffill()

    # 4. Check nothing is empty or negative, then save
    assert prices.isna().sum().sum() == 0, "still has empty cells"
    assert (prices > 0).all().all(), "found a zero or negative price"

    out = CLEAN / "cse_prices.csv"
    prices.to_csv(out)
    print("\nSaved", out)
    print("Data as of:", prices.index.max())


if __name__ == "__main__":
    main()
