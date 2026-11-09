"""
Step 1 of Model 1: turn the clean data files into 5 numbers.

For each asset class we work out:
  mean  - a typical yearly return (%)
  sd    - how much it can swing in a year (%), i.e. the risk
  low/high - a plain-words range to show the user
and a note saying exactly which file and row the number came from.

IMPORTANT: this file reads data/clean/*.csv fresh every time it runs. Nothing
here is a frozen number pulled from today's rates - if CBSL's rate changes
tomorrow and you re-run the data pipeline, this file picks up the new rate
automatically next time it runs. The ONE number that is NOT read from data,
because there is no file that measures it, is EQUITY_PREMIUM below - that is
our own judgment call, written here so it is easy to find and change.
(Decision + reasoning: docs/decisions.md, D47.)
"""
from pathlib import Path

import numpy as np
import pandas as pd

CLEAN = Path(__file__).resolve().parents[2] / "data" / "clean"

# ---- the one judgment call in this whole file ----
# Shares need an "extra return for extra risk" on top of the risk-free rate.
# We can't measure this from one year of (falling) CSE prices, so we use a
# number from research instead. Change this one line if the team disagrees.
EQUITY_PREMIUM = 5.0   # percentage points above the 12-month T-bill yield

ASSETS = ["Savings", "Fixed deposits", "T-bills & bonds", "Unit trusts", "Shares (S&P SL20)"]


def load_assumptions():
    rates = pd.read_csv(CLEAN / "cbsl_rates_monthly.csv")
    bills = pd.read_csv(CLEAN / "cbsl_tbill_curve.csv")
    perf = pd.read_csv(CLEAN / "utasl_performance.csv")
    qual = pd.read_csv(CLEAN / "data_quality.csv")
    rets = pd.read_csv(CLEAN / "returns_raw.csv", index_col=0)

    out, notes = {}, {}

    # --- Savings: CBSL publishes a min-max range each month; use the middle ---
    r = rates.dropna(subset=["savings_max"]).iloc[-1]
    out["Savings"] = dict(mean=(r.savings_min + r.savings_max) / 2, sd=0.0,
                          low=r.savings_min, high=r.savings_max)
    notes["Savings"] = f"CBSL Table 4.04, {r.month}: banks pay {r.savings_min}% to {r.savings_max}%."

    # --- Fixed deposits: average new FD rate, with the quoted 12-month range ---
    r = rates.dropna(subset=["awnfdr"]).iloc[-1]
    out["Fixed deposits"] = dict(mean=r.awnfdr, sd=0.0, low=r.fd_12m_min, high=r.fd_12m_max)
    notes["Fixed deposits"] = (f"CBSL Table 4.04, {r.month}: average new FD rate {r.awnfdr}%, "
                               f"12-month FDs quoted {r.fd_12m_min}% to {r.fd_12m_max}%.")

    # --- T-bills & bonds: today's 12-month yield; risk = how much that yield
    #     itself has moved, month to month, over the last 3 years ---
    b = bills[bills.maturity == "12 Month"].sort_values("as_of").iloc[-1]
    mid = (b.buy_yield + b.sell_yield) / 2
    t12 = rates.set_index("month").tbill_12m.dropna().tail(37)
    sd_bill = float(t12.diff().dropna().std() * np.sqrt(12))
    out["T-bills & bonds"] = dict(mean=mid, sd=sd_bill, low=mid - sd_bill, high=mid + sd_bill)
    notes["T-bills & bonds"] = (f"CBSL weekly PDF, {b.as_of}: 12-month bill yield {mid:.2f}%. "
                                f"Risk = size of month-to-month yield moves over the last 3 years.")

    # --- Unit trusts: low-risk fund categories only; UTASL's year-to-date
    #     return scaled to a full year; risk = spread between funds (a stand-in
    #     until enough daily price history builds up) ---
    kinds = ["Open-ended income funds", "Open-ended money-market funds", "Open-ended gilt-edged funds"]
    month_no = int(perf.report_month.max()[-2:])
    p = perf[(perf.report_month == perf.report_month.max()) & perf.category.isin(kinds)].dropna(subset=["ytd_pct"])
    ann = p.ytd_pct * 12 / month_no
    out["Unit trusts"] = dict(mean=float(ann.median()), sd=float(ann.std()),
                              low=float(ann.quantile(0.1)), high=float(ann.quantile(0.9)))
    notes["Unit trusts"] = (f"UTASL report {perf.report_month.max()}: {len(p)} income/money-market/gilt funds, "
                            f"year-to-date return scaled to 12 months.")

    # --- Shares: risk-free rate + our stated premium for the average; real
    #     price history (one year) for the risk. We do NOT average last
    #     year's actual returns - see docstring for why. ---
    ok = qual[qual.robust].symbol.tolist()
    basket = rets[ok].mean(axis=1)
    sd_eq = float(basket.std() * np.sqrt(252) * 100)
    mean_eq = mid + EQUITY_PREMIUM
    out["Shares (S&P SL20)"] = dict(mean=mean_eq, sd=sd_eq, low=mean_eq - sd_eq, high=mean_eq + sd_eq)
    notes["Shares (S&P SL20)"] = (f"{len(ok)} CSE stocks, {len(basket)} days: yearly risk {sd_eq:.1f}%. "
                                  f"Average return = today's 12-month T-bill ({mid:.2f}%) + our {EQUITY_PREMIUM}% "
                                  f"premium (D47). For reference, actual return over the last {len(basket)} days "
                                  f"was {basket.mean()*252*100:.1f}% - too short and too unusual a period to use directly.")

    return out, notes


if __name__ == "__main__":
    a, n = load_assumptions()
    for k in ASSETS:
        v = a[k]
        print(f"{k:20s}  mean {v['mean']:6.2f}%   risk {v['sd']:5.2f}%   range {v['low']:.1f}% to {v['high']:.1f}%")
        print("   ", n[k])
