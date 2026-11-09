"""Model 4 (added late, 9 Nov): forecast baseline + ARIMA-style check.

The original plan (docs/decisions.md D43) called for "a baseline-vs-ARIMA
check on one or two series" before the Thu 5 Nov deadline. It got cut when
the deadline first moved and never got picked back up — until now.

What this is: a simplified ARIMA(p, 1, 0) — an autoregressive model fitted
on the first difference of log price, with NO moving-average (q=0) term —
written by hand in plain NumPy rather than using statsmodels. statsmodels
ships even more compiled Cython extensions than scikit-learn (which was
blocked earlier today by this team's laptop's Windows Device Guard /
Application Control policy), so using it here would risk the exact same
failure, this close to the deadline. This is the same tradeoff already
made for Model 2 (hand-written k-means instead of scikit-learn).

What it does, per chosen stock:
1. Holds out the last HOLDOUT_DAYS as a test set.
2. Fits AR(p) on log-return (first-differenced log price) using ordinary
   least squares, choosing p (1-5) by BIC on the TRAINING data only (so the
   backtest number isn't picked to look good).
3. Forecasts the holdout period recursively (each step uses the model's own
   prior forecasts, like a real forecaster would - not the true future
   values) and compares it against a naive "no change" baseline (tomorrow's
   price = last known price), which is the standard, honest baseline for
   financial series.
4. Reports which one actually wins on the holdout - no cherry-picking.
5. Refits on ALL available data and produces a genuine forward-looking
   projection with a widening confidence band (the band grows with the
   square root of the number of days ahead, same idea as a random walk's
   uncertainty growing over time).

This is a real, honestly-validated forecast - but it is NOT the same as a
full statsmodels ARIMA (no moving-average term, no formal stationarity
tests), and it's checked on only ~240 days of price history, the most the
CSE currently gives us. Treat it as a simple, explainable baseline, not a
polished trading signal - see docs/decisions.md D53.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PRICES_PATH = ROOT / "data" / "clean" / "cse_prices_adjusted.csv"
BACKTEST_OUT = ROOT / "data" / "clean" / "price_forecast_backtest.csv"
WEB_OUT = ROOT / "web" / "public" / "data" / "price_forecast.json"

# "one or two series" per the original plan - two well-known, liquid
# blue-chips rather than all 23, kept small and explainable on purpose.
SYMBOLS = ["JKH.N0000", "COMB.N0000"]

HOLDOUT_DAYS = 30
FORECAST_DAYS = 30
MAX_AR_ORDER = 5


def fit_ar(returns: np.ndarray, p: int):
    """Fit AR(p) on a 1-D array of returns via OLS. Returns (coefs, intercept, resid_std)."""
    n = len(returns)
    X = np.column_stack([returns[p - 1 - lag : n - 1 - lag] for lag in range(p)])
    X = np.column_stack([np.ones(len(X)), X])
    y = returns[p:]
    coefs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coefs
    resid_std = resid.std(ddof=p + 1) if len(resid) > p + 1 else resid.std()
    return coefs, resid_std


def bic_for_order(returns: np.ndarray, p: int) -> float:
    n = len(returns) - p
    coefs, resid_std = fit_ar(returns, p)
    sse = max(resid_std**2 * n, 1e-12)
    return n * np.log(sse / n) + (p + 1) * np.log(n)


def choose_order(returns: np.ndarray) -> int:
    scores = {p: bic_for_order(returns, p) for p in range(1, MAX_AR_ORDER + 1)}
    return min(scores, key=scores.get)


def forecast_ar(returns_history: np.ndarray, coefs: np.ndarray, p: int, steps: int) -> np.ndarray:
    """Recursive multi-step forecast of future returns, using only the
    model's own prior forecasts (not real future data) for each next step -
    the honest way to backtest or project forward."""
    history = list(returns_history[-p:])
    out = []
    for _ in range(steps):
        lags = history[-p:][::-1]
        pred = coefs[0] + np.dot(coefs[1:], lags)
        out.append(pred)
        history.append(pred)
    return np.array(out)


def run_one(symbol: str, log_prices: pd.Series):
    n = len(log_prices)
    train_log = log_prices.iloc[: n - HOLDOUT_DAYS]
    test_log = log_prices.iloc[n - HOLDOUT_DAYS :]

    train_returns = train_log.diff().dropna().to_numpy()
    p = choose_order(train_returns)
    coefs, resid_std = fit_ar(train_returns, p)

    # Backtest: forecast the holdout window recursively from the end of train.
    pred_returns = forecast_ar(train_returns, coefs, p, HOLDOUT_DAYS)
    pred_log = train_log.iloc[-1] + np.cumsum(pred_returns)
    pred_price = np.exp(pred_log)

    naive_log = np.full(HOLDOUT_DAYS, train_log.iloc[-1])
    naive_price = np.exp(naive_log)

    actual_price = np.exp(test_log.to_numpy())

    ar_rmse = float(np.sqrt(np.mean((pred_price - actual_price) ** 2)))
    naive_rmse = float(np.sqrt(np.mean((naive_price - actual_price) ** 2)))
    ar_mae = float(np.mean(np.abs(pred_price - actual_price)))
    naive_mae = float(np.mean(np.abs(naive_price - actual_price)))
    winner = "AR" if ar_rmse < naive_rmse else "naive (no-change)"

    # Forward-looking projection: refit on ALL available data, project
    # FORECAST_DAYS ahead from today, with a widening confidence band.
    all_returns = log_prices.diff().dropna().to_numpy()
    p_full = choose_order(all_returns)
    coefs_full, resid_std_full = fit_ar(all_returns, p_full)
    future_returns = forecast_ar(all_returns, coefs_full, p_full, FORECAST_DAYS)
    future_log = log_prices.iloc[-1] + np.cumsum(future_returns)
    future_price = np.exp(future_log)
    # Band grows with sqrt(days ahead), same shape as a random walk's
    # cumulative variance - a simple, standard, honest way to show growing
    # uncertainty the further out the projection goes.
    days_ahead = np.arange(1, FORECAST_DAYS + 1)
    band_log = 1.28 * resid_std_full * np.sqrt(days_ahead)  # ~80% band
    future_low = np.exp(future_log - band_log)
    future_high = np.exp(future_log + band_log)

    print(f"\n{symbol}: chosen AR order p={p} (train-only BIC)")
    print(f"  Holdout ({HOLDOUT_DAYS} days) RMSE:  AR=Rs{ar_rmse:.2f}  naive=Rs{naive_rmse:.2f}  -> {winner} wins")
    print(f"  Holdout MAE:                  AR=Rs{ar_mae:.2f}  naive=Rs{naive_mae:.2f}")
    print(f"  {FORECAST_DAYS}-day forward projection from Rs{np.exp(log_prices.iloc[-1]):.2f}: "
          f"Rs{future_price[-1]:.2f} (80% range Rs{future_low[-1]:.2f}-Rs{future_high[-1]:.2f})")

    backtest_row = {
        "symbol": symbol,
        "ar_order": p,
        "holdout_days": HOLDOUT_DAYS,
        "ar_rmse": round(ar_rmse, 4),
        "naive_rmse": round(naive_rmse, 4),
        "ar_mae": round(ar_mae, 4),
        "naive_mae": round(naive_mae, 4),
        "winner": winner,
    }

    web_row = {
        "symbol": symbol,
        "ar_order": int(p_full),
        "backtest": {
            "holdout_days": HOLDOUT_DAYS,
            "ar_rmse": round(ar_rmse, 2),
            "naive_rmse": round(naive_rmse, 2),
            "winner": winner,
        },
        "last_price": round(float(np.exp(log_prices.iloc[-1])), 2),
        "last_date": str(log_prices.index[-1].date()),
        "forecast": [
            {
                "date": str((log_prices.index[-1] + pd.Timedelta(days=int(d))).date()),
                "price": round(float(p_), 2),
                "low": round(float(lo), 2),
                "high": round(float(hi), 2),
            }
            for d, p_, lo, hi in zip(days_ahead, future_price, future_low, future_high)
        ],
    }
    return backtest_row, web_row


def main():
    df = pd.read_csv(PRICES_PATH, index_col=0, parse_dates=True)
    backtest_rows = []
    web_rows = []
    for symbol in SYMBOLS:
        if symbol not in df.columns:
            print(f"Skipping {symbol}: not in {PRICES_PATH.name}")
            continue
        series = df[symbol].dropna()
        log_prices = np.log(series)
        bt, wr = run_one(symbol, log_prices)
        backtest_rows.append(bt)
        web_rows.append(wr)

    pd.DataFrame(backtest_rows).to_csv(BACKTEST_OUT, index=False)
    print(f"\nSaved {BACKTEST_OUT.relative_to(ROOT)}")

    WEB_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(WEB_OUT, "w") as f:
        json.dump(
            {
                "generated_at": pd.Timestamp.utcnow().isoformat(),
                "note": (
                    "Simplified ARIMA-style forecast (AR fitted on first-differenced "
                    "log price, no moving-average term), hand-written in NumPy, "
                    "validated against a naive no-change baseline on a holdout. "
                    "Covers 2 stocks only. See README and docs/decisions.md D53."
                ),
                "companies": web_rows,
            },
            f,
            indent=2,
        )
    print(f"Saved {WEB_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
