"""
Step 7: turn JKH prices into daily returns and measure how bumpy they are.
Run from the ModelX folder:  python src/explore/jkh_returns.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

# --- same loading steps as Step 6 ---
path = Path("data/raw/cse/history_JKH.N0000_2026-11-03.json")
with open(path) as f:
    raw = json.load(f)

df = pd.DataFrame(raw["chartData"])
df["date"] = (
    pd.to_datetime(df["t"], unit="ms", utc=True)
    .dt.tz_convert("Asia/Colombo")
    .dt.date
)
df = df[["date", "p"]]
df.columns = ["date", "price"]

# --- new in Step 7 ---
# Daily log return = ln(today's price / yesterday's price)
df["return"] = np.log(df["price"] / df["price"].shift(1))

print(df.head())
print()

r = df["return"].dropna()   # the first day has no "yesterday", so drop it

print("Days with a return:", len(r))
print("Average daily return: {:.4%}".format(r.mean()))
print("Daily standard deviation: {:.4%}".format(r.std()))
print("Worst day: {:.2%}".format(r.min()))
print("Best day: {:.2%}".format(r.max()))
print()
print("Yearly return (average x 252): {:.1%}".format(r.mean() * 252))
print("Yearly volatility (std x sqrt 252): {:.1%}".format(r.std() * np.sqrt(252)))
