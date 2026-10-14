"""
Unit trust NAVs - Bucket 1 exploration.

waraka.lk lists 80+ Sri Lankan unit trusts, but the page loads its data with
JavaScript, so a plain requests.get() of the page won't show the numbers.

How to find the real data feed (5 minutes):
  1. Open a fund page on waraka.lk in Chrome.
  2. Right-click > Inspect > Network tab > filter "Fetch/XHR" > reload.
  3. Look for a request that returns JSON with NAV / price / date.
  4. Copy its URL into FEED_URL below.
  5. BEFORE using it in the project: read waraka.lk's Terms of Use. If they don't allow
     reuse, email them for permission, or use the fund managers' own sites instead
     (they publish NAVs daily).

Note the answer (allowed or not, and how) in docs/data_sources.md.

Run:  python src/data/unit_trust_pull.py
"""

import json
from datetime import date
from pathlib import Path

import requests

FEED_URL = ""  # paste the JSON URL you found here
OUT = Path("data/raw/unit_trusts")
OUT.mkdir(parents=True, exist_ok=True)


def main():
    if not FEED_URL:
        print("Set FEED_URL first - see the instructions at the top of this file.")
        return
    r = requests.get(FEED_URL, headers={"User-Agent": "ModelX student project"}, timeout=30)
    r.raise_for_status()
    data = r.json()
    path = OUT / f"waraka_{date.today()}.json"
    path.write_text(json.dumps(data, indent=2))
    print("saved", path)
    print(json.dumps(data, indent=2)[:1500])


if __name__ == "__main__":
    main()
