"""
Load rates and inflation exported from the CBSL Data Library.

The Data Library (https://www.cbsl.lk/eresearch) is a query tool, so the simplest
reliable way is:
  1. Open the Data Library, pick the series, set the date range (as far back as it goes),
     and export to Excel/CSV.
  2. Save the files into data/raw/cbsl/ with these names:
        tbill_yields.xlsx      91 / 182 / 364-day weighted average yields
        tbond_yields.xlsx      (if available) secondary market or auction yields
        ccpi_inflation.xlsx    CCPI year-on-year inflation
        fd_rates.xlsx          AWFDR (average weighted fixed deposit rate)
        policy_rate.xlsx       OPR / SDFR / SLFR
  3. Run:  python src/data/cbsl_load.py

This script just opens each file and reports date range, rows and missing values,
which is what you need for the data sources table.
Later (Bucket 3) we can automate the download if CBSL allows it.
"""

from pathlib import Path

import pandas as pd

RAW = Path("data/raw/cbsl")
RAW.mkdir(parents=True, exist_ok=True)

FILES = ["tbill_yields", "tbond_yields", "ccpi_inflation", "fd_rates", "policy_rate"]


def read_any(name):
    for ext in (".xlsx", ".xls", ".csv"):
        p = RAW / (name + ext)
        if p.exists():
            return pd.read_csv(p) if ext == ".csv" else pd.read_excel(p)
    return None


def main():
    for name in FILES:
        df = read_any(name)
        if df is None:
            print(f"[missing] {name} - export it from the Data Library first")
            continue
        print(f"\n== {name} ==")
        print("rows:", len(df), "| columns:", list(df.columns)[:8])
        print(df.head(3).to_string())
        print("missing values per column:")
        print(df.isna().sum().to_string())


if __name__ == "__main__":
    main()
