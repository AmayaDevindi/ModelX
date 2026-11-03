"""
Step 6: open the JKH price history we saved and look at it as a table.
Run from the ModelX folder:  python src/explore/look_at_jkh.py
"""

import json
from pathlib import Path

import pandas as pd

# 1. Find the saved file (the date in the name is the day we pulled it)
path = Path("data/raw/cse/history_JKH.N0000_2026-11-03.json")

# 2. Read the JSON text into Python
with open(path) as f:
    raw = json.load(f)

# 3. Turn the list of days into a table
df = pd.DataFrame(raw["chartData"])

# 4. Turn the long number in "t" into a real date.
#    The number is in UTC time, so we convert to Sri Lanka time first,
#    otherwise every date would be one day behind.
df["date"] = (
    pd.to_datetime(df["t"], unit="ms", utc=True)
    .dt.tz_convert("Asia/Colombo")
    .dt.date
)

# 5. Keep only the columns we need and give them readable names
df = df[["date", "h", "l", "p", "q"]]
df.columns = ["date", "high", "low", "price", "volume"]

# 6. Look at it
print("Rows and columns:", df.shape)
print()
print("First 5 days:")
print(df.head())
print()
print("Last 5 days:")
print(df.tail())
print()
print("Lowest price:", df["price"].min())
print("Highest price:", df["price"].max())
