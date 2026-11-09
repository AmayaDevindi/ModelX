"""
Model 2 (reduced scope): group S&P SL20 companies by real, measurable
features using k-means clustering (actual unsupervised machine learning,
not a hand-written rule table), then explain each company's group in plain
words.

This is NOT the full fundamental-analysis scoring described in the
proposal (profitability, earnings growth, debt ratios) - those figures
live only in the PDF annual/quarterly reports, which need real extraction
work we don't have time for today (see docs/decisions.md). What we use
instead, for every company, is real and live:
  - price volatility (how much the daily price swings)
  - beta (how much it moves with the rest of the market)
  - independent-director ratio (board governance)
  - whether the auditor is a Big 4 firm (audit quality signal)
  - where today's price sits in its 12-month high/low range

K-means doesn't know in advance which group is "better" - it just finds
companies with similar feature values. We label the groups AFTER fitting,
by looking at which group has lower volatility and better governance
features on average, so the labels describe what the model actually
found, not an assumption we fed it.

Reads : data/clean/company_profile.csv, data/clean/returns_raw.csv,
        data/clean/data_quality.csv
Writes: data/clean/company_health_clusters.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

CLEAN = Path(__file__).resolve().parents[2] / "data" / "clean"

FEATURES = ["volatility", "beta", "independent_ratio", "is_big4_auditor", "position_in_52wk_range"]


def kmeans(X, k, n_init=10, max_iter=300, seed=7):
    """Plain-NumPy k-means (Lloyd's algorithm), written by hand instead of
    using scikit-learn - on this laptop's locked-down Windows security
    policy, scikit-learn's compiled files get blocked at import time
    (Device Guard / Application Control), so this avoids that entirely and
    only needs NumPy, which already works. Standard algorithm: start from
    k random points, repeatedly (1) assign every point to its nearest
    center, (2) move each center to the average of its assigned points,
    until nothing changes; repeat from different random starts and keep
    the tightest result (smallest total squared distance to each point's
    center), since a single run can land in a weak local optimum.
    Returns (labels, centers) for the best of the n_init runs.
    """
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    best_labels, best_centers, best_inertia = None, None, np.inf

    for _ in range(n_init):
        centers = X[rng.choice(n, size=k, replace=False)].copy()
        labels = np.zeros(n, dtype=int)
        for _ in range(max_iter):
            dists = ((X[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
            new_labels = dists.argmin(axis=1)
            new_centers = np.array([
                X[new_labels == j].mean(axis=0) if np.any(new_labels == j) else centers[j]
                for j in range(k)
            ])
            if np.array_equal(new_labels, labels) and np.allclose(new_centers, centers):
                labels, centers = new_labels, new_centers
                break
            labels, centers = new_labels, new_centers

        inertia = ((X - centers[labels]) ** 2).sum()
        if inertia < best_inertia:
            best_inertia, best_labels, best_centers = inertia, labels, centers

    return best_labels, best_centers


def compute_return_features():
    """Per-company volatility and beta vs an equal-weighted market basket,
    from the same daily returns the assumptions.py equity estimate uses."""
    rets = pd.read_csv(CLEAN / "returns_raw.csv", index_col=0)
    qual = pd.read_csv(CLEAN / "data_quality.csv")
    robust = qual[qual.robust].symbol.tolist()

    market = rets[robust].mean(axis=1)  # equal-weighted basket = our market proxy
    market_var = market.var()

    rows = []
    for symbol in rets.columns:
        company = rets[symbol]
        volatility = float(company.std() * np.sqrt(252) * 100)  # annualised, %
        beta = float(company.cov(market) / market_var) if market_var else None
        rows.append(dict(symbol=symbol, volatility=volatility, beta=beta))
    return pd.DataFrame(rows)


def main():
    profile = pd.read_csv(CLEAN / "company_profile.csv")
    returns = compute_return_features()
    df = profile.merge(returns, on="symbol", how="inner")
    df["is_big4_auditor"] = df["is_big4_auditor"].astype(int)
    df = df.dropna(subset=FEATURES).reset_index(drop=True)

    if len(df) < 6:
        raise SystemExit(f"Only {len(df)} companies have complete data - need more to cluster sensibly.")

    X = df[FEATURES].values.astype(float)
    # Standardise by hand (z-score) so every feature counts equally - a
    # company with volatility in the 20s shouldn't dominate distance
    # calculations just because its raw numbers are bigger than a 0-1 ratio.
    means, stds = X.mean(axis=0), X.std(axis=0)
    stds[stds == 0] = 1
    X_scaled = (X - means) / stds

    k = 3
    labels, _centers = kmeans(X_scaled, k, n_init=10, seed=7)
    df["cluster"] = labels

    # Rank clusters by average volatility (lower = steadier) - and ONLY
    # label them on that one dimension. Governance (independence, auditor)
    # does not necessarily move together with volatility across clusters -
    # we checked, and it genuinely doesn't always line up - so the tier
    # name only claims what it's actually based on. Governance is reported
    # as its own separate fact per cluster, not folded into one verdict.
    cluster_order = df.groupby("cluster")["volatility"].mean().sort_values().index.tolist()
    tier_names = ["Lower price volatility", "Medium price volatility", "Higher price volatility"]
    tier_of = {cluster_order[i]: tier_names[i] for i in range(k)}
    df["tier"] = df["cluster"].map(tier_of)

    # Explain each company: which features differ most from the overall
    # average, in plain words - this is what replaces the proposal's
    # "three strongest/weakest points" for the full version.
    overall_mean = df[FEATURES].mean()
    overall_sd = df[FEATURES].std().replace(0, 1)

    def explain(row):
        z = (row[FEATURES] - overall_mean) / overall_sd
        notable = z.abs().sort_values(ascending=False).index[:2]
        bits = []
        for feat in notable:
            direction = "above" if z[feat] > 0 else "below"
            label = {
                "volatility": "price volatility",
                "beta": "sensitivity to market moves",
                "independent_ratio": "board independence",
                "is_big4_auditor": "Big 4 auditor",
                "position_in_52wk_range": "position in its 12-month range",
            }[feat]
            bits.append(f"{label} is {direction} average")
        return "; ".join(bits)

    df["why"] = df.apply(explain, axis=1)

    out_cols = ["symbol", "sector", "tier", "why", "volatility", "beta",
                "independent_ratio", "is_big4_auditor", "position_in_52wk_range"]
    out = CLEAN / "company_health_clusters.csv"
    df[out_cols].sort_values(["tier", "symbol"]).to_csv(out, index=False)

    print(f"Clustered {len(df)} companies into {k} groups:\n")
    for cluster in cluster_order:
        group = df[df.cluster == cluster]
        print(f"[{tier_of[cluster]}] ({len(group)} companies)")
        print(f"  avg volatility {group.volatility.mean():.1f}%, "
              f"avg independent ratio {group.independent_ratio.mean():.0%}, "
              f"Big 4 auditor {group.is_big4_auditor.mean():.0%} of the time")
        for _, r in group.iterrows():
            print(f"    {r.symbol:12} ({r.sector}) - {r.why}")
        print()


if __name__ == "__main__":
    main()
