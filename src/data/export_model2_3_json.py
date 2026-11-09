"""
Export Model 2 (company health clusters) and Model 3 (news chain tags) for
the website to read, the same way export_model_json.py does for Model 1.

Reads : data/clean/company_health_clusters.csv, data/clean/news_chain_tags.csv
Writes: web/public/data/company_clusters.json, web/public/data/news_chain.json
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CLEAN = ROOT / "data" / "clean"
OUT = ROOT / "web" / "public" / "data"


def export_clusters():
    path = CLEAN / "company_health_clusters.csv"
    if not path.exists():
        print("No company_health_clusters.csv yet - skipping Model 2 export.")
        return
    df = pd.read_csv(path)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "companies": df.to_dict(orient="records"),
    }
    out = OUT / "company_clusters.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out} - {len(df)} companies")


def export_news_chain():
    path = CLEAN / "news_chain_tags.csv"
    if not path.exists():
        print("No news_chain_tags.csv yet - skipping Model 3 export.")
        return
    df = pd.read_csv(path).fillna("")
    df = df.sort_values("published", ascending=False)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tags": df.to_dict(orient="records"),
    }
    out = OUT / "news_chain.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out} - {len(df)} tagged headlines")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    export_clusters()
    export_news_chain()


if __name__ == "__main__":
    main()
