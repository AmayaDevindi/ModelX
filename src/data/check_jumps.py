"""
Step 10: find unusual one-day price moves, work out which look like share splits,
adjust those automatically, and flag the rest for a human to look at.

How a day gets flagged
  1. Take the stock's daily return and subtract the market's move that day
     (the median of all stocks), so market-wide days are not flagged.
  2. Measure how big a normal day is for THIS stock over the last 60 days
     (MAD: the median is not fooled by one crazy day).
  3. Flag the day if it is more than K times that normal size.
  4. For the first 30 days, where we cannot measure "normal" yet, use a plain 15% limit.

Reads : data/raw/cse/history_*.json   (prices and volumes)
Writes: data/clean/cse_prices_adjusted.csv
        data/clean/adjustments_log.csv   (every flag and every change)

Run from the ModelX folder:  python src/data/check_jumps.py
"""

import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw/cse")
CLEAN = Path("data/clean")
TODAY = date.today()

K = 8                  # flag a move bigger than 8 "normal days" for that stock
WINDOW = 60            # days used to learn what is normal
MIN_DAYS = 30          # need at least this many days before we trust the yardstick
FLOOR = 0.005          # a normal day is never smaller than 0.5%, so quiet stocks do not over-flag
BACKUP_LIMIT = 0.15    # plain limit used when we cannot measure "normal" yet

SPLIT_FACTORS = [2, 3, 4, 5, 10]   # splits we look for (price falls to 1/2, 1/3, ...)
TOLERANCE = 0.10                   # price ratio times factor must be within 10% of 1


def load_prices_and_volumes():
    """Return two tables (days x companies): closing price and shares traded."""
    prices, volumes = {}, {}
    for path in sorted(RAW.glob(f"history_*_{TODAY}.json")):
        symbol = path.name.split("_")[1]
        df = pd.DataFrame(json.loads(path.read_text())["chartData"])
        df["date"] = (
            pd.to_datetime(df["t"], unit="ms", utc=True)
            .dt.tz_convert("Asia/Colombo")
            .dt.date
        )
        df = df.set_index("date")
        prices[symbol] = df["p"]
        volumes[symbol] = df["q"]
    prices = pd.DataFrame(prices).sort_index().ffill()
    volumes = pd.DataFrame(volumes).sort_index().fillna(0)
    return prices, volumes


def normal_size(window_values):
    """Typical size of a day: median absolute deviation, scaled to match a standard deviation."""
    x = window_values[~np.isnan(window_values)]
    return 1.4826 * np.median(np.abs(x - np.median(x)))


def looks_like_split(ratio, vol_before, vol_after):
    """Return the split factor (2, 3, ...) if the jump looks like a split, else None."""
    for factor in SPLIT_FACTORS:
        close_enough = abs(ratio * factor - 1) < TOLERANCE   # e.g. ratio 0.33 x 3 = 0.99
        # after a split there are `factor` times more shares, so volume should rise too
        volume_rose = vol_after > vol_before * factor * 0.5
        if close_enough and volume_rose:
            return factor
    return None


def main():
    prices, volumes = load_prices_and_volumes()
    returns = np.log(prices / prices.shift(1)).iloc[1:]

    # 1. Remove the market's move, then score each stock against its own normal
    market = returns.median(axis=1)
    leftover = returns.sub(market, axis=0)
    yardstick = (
        leftover.shift(1)                       # shift: do not let today judge itself
        .rolling(WINDOW, min_periods=MIN_DAYS)
        .apply(normal_size, raw=True)
        .clip(lower=FLOOR)
    )
    score = leftover / yardstick

    # 2. Flag: big score, or (no yardstick yet and a plain 15% move)
    flag = (score.abs() > K) | (yardstick.isna() & (returns.abs() > BACKUP_LIMIT))
    flags = flag.stack()
    flags = flags[flags]

    adjusted = prices.copy()
    log = []

    for (day, symbol), _ in flags.items():
        i = prices.index.get_loc(day)
        ratio = prices[symbol].iloc[i] / prices[symbol].iloc[i - 1]
        vol_before = volumes[symbol].iloc[max(0, i - 20):i].median()
        vol_after = volumes[symbol].iloc[i:i + 5].median()

        # 3. Does it look like a split?
        factor = looks_like_split(ratio, vol_before, vol_after)

        if factor:
            # scale every EARLIER price down so the series lines up
            adjusted.loc[prices.index < day, symbol] *= 1 / factor
            action = f"adjusted: earlier prices divided by {factor}"
        else:
            action = "flagged only: needs a human check"

        log.append({
            "symbol": symbol, "date": day,
            "own_return": round(returns.loc[day, symbol], 3),
            "market_return": round(market.loc[day], 3),
            "score": round(score.loc[day, symbol], 1) if pd.notna(score.loc[day, symbol]) else None,
            "price_ratio": round(ratio, 3),
            "action": action,
        })

    # 4. Save the adjusted prices and the log
    adjusted.to_csv(CLEAN / "cse_prices_adjusted.csv")
    log_df = pd.DataFrame(log).sort_values("date")
    log_df.to_csv(CLEAN / "adjustments_log.csv", index=False)

    print(f"Returns checked: {returns.size}   Flagged (K={K}): {len(log_df)}\n")
    print(log_df.to_string(index=False))
    print("\nSaved data/clean/cse_prices_adjusted.csv and adjustments_log.csv")


if __name__ == "__main__":
    main()
