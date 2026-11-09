"""
Export company names/snapshots and daily price history for the website's
QUOTE pages (one page per stock, like the proposal describes).

Reads : data/clean/cse_prices_adjusted.csv, data/clean/company_profile.csv,
        the newest data/raw/cse/spsl_constituents_*.json
Writes: web/public/data/companies.json       (one row per company: name, sector, latest price/change)
        web/public/data/price_history.json   (daily closing price per company, for the chart)
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CLEAN = ROOT / "data" / "clean"
RAW_CSE = ROOT / "data" / "raw" / "cse"
OUT = ROOT / "web" / "public" / "data"


def latest_constituents():
    files = sorted(RAW_CSE.glob("spsl_constituents_*.json"))
    if not files:
        raise SystemExit("No spsl_constituents_*.json found - run cse_pull.py first.")
    return json.loads(files[-1].read_text())["reqSNPIndices"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    constituents = latest_constituents()
    by_symbol = {c["symbol"]: c for c in constituents}

    profile_path = CLEAN / "company_profile.csv"
    sectors = {}
    if profile_path.exists():
        prof = pd.read_csv(profile_path)
        sectors = dict(zip(prof.symbol, prof.sector))

    companies = []
    for symbol, c in by_symbol.items():
        companies.append(dict(
            symbol=symbol,
            name=c.get("name"),
            sector=sectors.get(symbol),
            last_price=c.get("price"),
            change=c.get("change"),
            change_pct=c.get("changePercentage"),
        ))
    companies.sort(key=lambda r: r["symbol"])
    (OUT / "companies.json").write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "companies": companies}, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote companies.json - {len(companies)} companies")

    prices_path = CLEAN / "cse_prices_adjusted.csv"
    prices = pd.read_csv(prices_path)
    date_col = prices.columns[0]
    history = {}
    for symbol in prices.columns[1:]:
        series = prices[[date_col, symbol]].dropna()
        history[symbol] = [
            {"date": str(row[date_col]), "price": float(row[symbol])}
            for _, row in series.iterrows()
        ]
    (OUT / "price_history.json").write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "history": history}),
        encoding="utf-8",
    )
    print(f"Wrote price_history.json - {len(history)} companies, "
          f"{max(len(v) for v in history.values())} days max")


if __name__ == "__main__":
    main()
