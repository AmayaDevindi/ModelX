"""
Pull per-company governance and live price-range data for every S&P SL20
company - the inputs Model 2 (health_cluster.py) needs that daily price
history alone doesn't give us: who's on the board and whether they're
independent, who the auditor is, and where today's price sits versus the
last 12 months' high/low.

The CSE's live API doesn't expose financial-statement figures (profit,
ROE, earnings) directly - those only exist in the PDF annual/quarterly
reports, which would need real extraction work we don't have time for
today (see docs/decisions.md, Model 2 scope note). This script pulls what
IS available live and real: board composition, auditor, sector, and the
12-month price range.

Reads : data/raw/cse/spsl_constituents_<today>.json (written by cse_pull.py)
Writes: data/clean/company_profile.csv
"""
import json
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

BASE = "https://www.cse.lk/api/"
RAW = Path("data/raw/cse")
CLEAN = Path("data/clean")
HEADERS = {"User-Agent": "ModelX student project (educational)"}
TODAY = date.today()

BIG_4_AUDITORS = ["ernst & young", "kpmg", "pricewaterhousecoopers", "pwc", "deloitte"]


def post(endpoint, data):
    r = requests.post(BASE + endpoint, data=data, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def is_big4(auditor_name):
    if not auditor_name:
        return False
    name = auditor_name.lower()
    return any(b in name for b in BIG_4_AUDITORS)


def governance_for(symbol):
    profile = post("companyProfile", {"symbol": symbol})
    directors = profile.get("infoCompanyDirector") or []
    total = len(directors)
    independent = sum(
        1 for d in directors
        if "independent" in (d.get("firstName") or "").lower()
    )
    sum_info = (profile.get("reqComSumInfo") or [{}])[0]
    return dict(
        sector=sum_info.get("sector"),
        auditor=sum_info.get("auditors"),
        is_big4_auditor=is_big4(sum_info.get("auditors")),
        director_count=total,
        independent_director_count=independent,
        independent_ratio=round(independent / total, 3) if total else None,
    )


def price_range_for(symbol):
    info = post("companyInfoSummery", {"symbol": symbol})
    s = info.get("reqSymbolInfo") or {}
    last = s.get("lastTradedPrice")
    hi = s.get("p12HiPrice")
    lo = s.get("p12LowPrice")
    position = None
    if last is not None and hi is not None and lo is not None and hi != lo:
        position = round((last - lo) / (hi - lo), 3)
    return dict(last_price=last, p12_high=hi, p12_low=lo, position_in_52wk_range=position)


def main():
    list_file = RAW / f"spsl_constituents_{TODAY}.json"
    if not list_file.exists():
        raise SystemExit(f"Missing {list_file} - run cse_pull.py first.")
    securities = json.loads(list_file.read_text())["reqSNPIndices"]

    rows = []
    for s in securities:
        symbol = s["symbol"]
        try:
            row = {"symbol": symbol}
            row.update(governance_for(symbol))
            row.update(price_range_for(symbol))
            rows.append(row)
            print(f"{symbol:12} sector={row['sector']!r:25} "
                  f"independent={row['independent_director_count']}/{row['director_count']} "
                  f"big4={row['is_big4_auditor']}")
        except Exception as e:
            print(f"{symbol:12} FAILED: {e}")
        time.sleep(1)  # be polite to the CSE's server

    df = pd.DataFrame(rows)
    CLEAN.mkdir(parents=True, exist_ok=True)
    out = CLEAN / "company_profile.csv"
    df.to_csv(out, index=False)
    print(f"\nWrote {out} - {len(df)} companies")


if __name__ == "__main__":
    main()
