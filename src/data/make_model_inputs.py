"""
Step 12: turn the cleaned prices into the numbers the models will read,
and automatically decide how much to trust each stock's data.

Handling rules (no human needed):
  - Splits were already fixed in check_jumps.py (prices are adjusted).
  - Other flagged days are real moves, so they STAY in the data.
  - For the average return we use a "capped" copy, where each stock's most extreme
    days are pulled in (to its 1st and 99th percentile), so one wild day cannot
    drag the average. For risk and the simulation we use the uncapped returns.
  - Each stock gets a data-confidence label, and a warning if something odd
    happened in the last few days.

Reads : data/clean/cse_prices_adjusted.csv, data/clean/adjustments_log.csv
Writes: data/clean/returns_raw.csv      (use for risk and the simulation)
        data/clean/returns_capped.csv   (use for the average return)
        data/clean/data_quality.csv     (one row per stock)

Run from the ModelX folder:  python src/data/make_model_inputs.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

CLEAN = Path("data/clean")

CAP_LOW, CAP_HIGH = 0.01, 0.99     # pull extremes in to the 1st / 99th percentile
RECENT_DAYS = 5                    # an odd day in the last 5 trading days gets a warning
MIN_DAYS_GOOD = 200                # fewer days of history than this lowers confidence
MIN_DAYS_OK = 120
ROBUST_GAP = 0.05                  # average return moving by more than 5 points = not robust


def main():
    prices = pd.read_csv(CLEAN / "cse_prices_adjusted.csv", index_col=0)
    log = pd.read_csv(CLEAN / "adjustments_log.csv")

    # 1. Daily log returns from the adjusted prices
    raw = np.log(prices / prices.shift(1)).iloc[1:]

    # 2. Capped copy: each stock's extremes pulled in to its own 1st / 99th percentile
    low = raw.quantile(CAP_LOW)
    high = raw.quantile(CAP_HIGH)
    capped = raw.clip(lower=low, upper=high, axis=1)

    raw.to_csv(CLEAN / "returns_raw.csv")
    capped.to_csv(CLEAN / "returns_capped.csv")

    # 3. One quality row per stock
    last_days = list(raw.index[-RECENT_DAYS:])
    rows = []
    for symbol in raw.columns:
        mine = log[log["symbol"] == symbol]
        unexplained = mine[mine["action"].str.startswith("flagged")]
        splits = mine[mine["action"].str.startswith("adjusted")]

        days = int(raw[symbol].count())
        mean_raw = raw[symbol].mean() * 252
        mean_capped = capped[symbol].mean() * 252
        recent = bool(unexplained["date"].isin(last_days).any())

        # confidence label from simple, visible rules
        if days < MIN_DAYS_OK or len(unexplained) >= 4:
            confidence = "low"
        elif days < MIN_DAYS_GOOD or len(unexplained) >= 1:
            confidence = "medium"
        else:
            confidence = "high"

        rows.append({
            "symbol": symbol,
            "days_of_history": days,
            "splits_adjusted": len(splits),
            "unexplained_flags": len(unexplained),
            "recent_flag": recent,
            "mean_return_raw": round(mean_raw, 3),
            "mean_return_capped": round(mean_capped, 3),
            "robust": abs(mean_raw - mean_capped) <= ROBUST_GAP,
            "confidence": confidence,
        })

    quality = pd.DataFrame(rows)
    quality.to_csv(CLEAN / "data_quality.csv", index=False)

    print(quality.to_string(index=False))
    print("\nConfidence:", quality["confidence"].value_counts().to_dict())
    print("Not robust to extreme days:", list(quality.loc[~quality["robust"], "symbol"]))
    print("Recent odd days:", list(quality.loc[quality["recent_flag"], "symbol"]) or "none")
    print("\nSaved returns_raw.csv, returns_capped.csv, data_quality.csv in data/clean/")


if __name__ == "__main__":
    main()
