"""
Step 3 of Model 1: Monte Carlo simulation.

Takes a final split (from profile.py) and an amount, and generates thousands
of possible 5-year (or however many years) futures, year by year, so we can
show a real range of outcomes instead of one fake-precise number.

Assumption we're making and should say out loud to the user: we assume the
investor RE-BALANCES back to their target split at the start of every year
(doesn't let winners drift into a bigger share of the pot over time). That's
a simplification - real people rarely rebalance that precisely - but it
keeps the model matching the split we actually recommended.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from assumptions import ASSETS, load_assumptions

CLEAN = Path(__file__).resolve().parents[2] / "data" / "clean"

# Unit trusts here are specifically income/money-market/gilt funds (see
# assumptions.py), which hold very little real equity - so their correlation
# with Shares should be small, not large. 0.15 is a modest, stated choice,
# not something measured (we don't have enough overlapping daily history for
# both yet to measure it directly).
UT_SHARE_CORRELATION = 0.15


def latest_inflation():
    """Read the latest year-on-year inflation straight from the data file,
    so this is never a number we typed in by hand - it updates automatically
    whenever the CCPI pull script gets a newer month."""
    ccpi = pd.read_csv(CLEAN / "cbsl_ccpi_history.csv")
    row = ccpi.dropna(subset=["ccpi_yoy_pct"]).iloc[-1]
    return float(row.ccpi_yoy_pct), row.month


def simulate(final_split, amount, years, inflation=None, assumptions=None, n_paths=10_000, seed=7):
    a = assumptions or load_assumptions()[0]
    if inflation is None:
        inflation, _ = latest_inflation()

    weights = np.array([final_split[k] for k in ASSETS], dtype=float) / 100
    mu = np.array([a[k]["mean"] for k in ASSETS]) / 100
    sd = np.array([a[k]["sd"] for k in ASSETS]) / 100

    # Build the correlation matrix: everything independent except Unit
    # trusts <-> Shares, which get the modest correlation above.
    corr = np.eye(len(ASSETS))
    i_ut = ASSETS.index("Unit trusts")
    i_eq = ASSETS.index("Shares (S&P SL20)")
    corr[i_ut, i_eq] = corr[i_eq, i_ut] = UT_SHARE_CORRELATION
    chol = np.linalg.cholesky(corr)   # turns independent random draws into correlated ones

    rng = np.random.default_rng(seed)
    value = np.full(n_paths, float(amount))

    for _ in range(int(years)):
        z = rng.standard_normal((n_paths, len(ASSETS))) @ chol.T   # one random draw per asset, per path
        yearly_returns = mu + sd * z
        yearly_returns = np.clip(yearly_returns, -0.95, None)       # can't lose more than 95% in a year
        portfolio_return = yearly_returns @ weights                 # blend by the split we recommended
        value = value * (1 + portfolio_return)

    inflation_adjusted_target = amount * (1 + inflation / 100) ** years

    return dict(
        final_values=value,
        bad_case=float(np.percentile(value, 5)),
        middle_case=float(np.percentile(value, 50)),
        good_case=float(np.percentile(value, 95)),
        chance_of_loss=float((value < amount).mean()),
        chance_beats_inflation=float((value > inflation_adjusted_target).mean()),
        inflation_adjusted_target=inflation_adjusted_target,
        inflation_used=inflation,
    )


if __name__ == "__main__":
    from profile import recommend

    amount = 500_000
    years = 5
    cases = [
        ("Cautious, no shares",       [0, 0, 0, 0], [True, True, True, True]),
        ("Balanced",                  [2, 2, 2, 2], [True, True, True, True]),
        ("Adventurous, knows little", [4, 4, 4, 4], [False, False, True, True]),
    ]
    for label, qa, kf in cases:
        r = recommend(qa, kf)
        s = simulate(r["final_split"], amount, years)
        print(f"\n{label}  (split: {r['final_split']})")
        print(f"  Rs {amount:,} over {years} years, inflation assumed {s['inflation_used']:.1f}%:")
        print(f"    bad case (5th pct):    Rs {s['bad_case']:>10,.0f}")
        print(f"    middle case (median):  Rs {s['middle_case']:>10,.0f}")
        print(f"    good case (95th pct):  Rs {s['good_case']:>10,.0f}")
        print(f"    chance of ending below what you put in: {s['chance_of_loss']:.1%}")
        print(f"    chance of beating inflation:            {s['chance_beats_inflation']:.1%}  "
             f"(need Rs {s['inflation_adjusted_target']:,.0f} just to keep buying power)")
