"""
Last step of the data pipeline: write the model's numbers as a plain JSON
file the website can read directly - no Python needed when someone visits
the site, and the numbers update automatically every time this pipeline runs.

Reads : src/model/assumptions.py (the 5 asset numbers), data/clean/cbsl_ccpi_history.csv
Writes: web/public/data/assumptions.json
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "model"))
from assumptions import ASSETS, EQUITY_PREMIUM, load_assumptions  # noqa: E402

OUT = ROOT / "web" / "public" / "data" / "assumptions.json"


def latest_inflation():
    ccpi = pd.read_csv(ROOT / "data" / "clean" / "cbsl_ccpi_history.csv")
    row = ccpi.dropna(subset=["ccpi_yoy_pct"]).iloc[-1]
    return float(row.ccpi_yoy_pct), row.month


def main():
    assumptions, notes = load_assumptions()
    inflation, inflation_month = latest_inflation()

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "equity_premium": EQUITY_PREMIUM,
        "inflation": inflation,
        "inflation_month": inflation_month,
        "assets": [
            {"name": name, **assumptions[name], "note": notes[name]}
            for name in ASSETS
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} - {len(ASSETS)} assets, inflation {inflation}% ({inflation_month})")


if __name__ == "__main__":
    main()
