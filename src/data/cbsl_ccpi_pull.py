"""
Download CBSL's inflation file (CCPI, 2021=100) and keep a growing monthly history.

Source : CBSL Statistical Tables, Real Sector, Prices, Wages and Employment
         https://www.cbsl.gov.lk/en/statistics/statistical-tables/real-sector/prices-wages-employment
         The page links to CCPI_and_CCPI_CORE_YYYYMMDD_e.xlsx, which holds only the
         LATEST 13 MONTHS. So every time we run, we add any new months to our own
         history file and the history grows over time.
Politeness: 10 second wait between requests (CBSL's robots.txt crawl delay).

Writes : data/raw/cbsl/CCPI_and_CCPI_CORE_YYYYMMDD_e.xlsx   (untouched copy)
         data/clean/cbsl_ccpi_history.csv                   (one row per month)

Run from the ModelX folder:  python src/data/cbsl_ccpi_pull.py
"""

import re
import time
from datetime import datetime
from pathlib import Path

import openpyxl
import pandas as pd
import requests

PAGE = "https://www.cbsl.gov.lk/en/statistics/statistical-tables/real-sector/prices-wages-employment"
HEADERS = {"User-Agent": "ModelX student project (educational)"}
CRAWL_DELAY = 10

RAW = Path("data/raw/cbsl")
CLEAN = Path("data/clean")
RAW.mkdir(parents=True, exist_ok=True)
CLEAN.mkdir(parents=True, exist_ok=True)
HISTORY = CLEAN / "cbsl_ccpi_history.csv"


def find_latest_link():
    resp = requests.get(PAGE, headers=HEADERS, timeout=30)
    html = resp.text
    found = re.findall(r'href="([^"]*CCPI_and_CCPI_CORE_(\d{8})_e\.xlsx)"', html)
    if not found:
        raise RuntimeError("Could not find the CCPI file link on the CBSL page. "
                           f"Status {resp.status_code}, {len(html)} characters, starts: "
                           f"{html[:200]!r}")
    url, stamp = max(found, key=lambda x: x[1])
    if url.startswith("/"):
        url = "https://www.cbsl.gov.lk" + url
    return url, stamp


def download(url, stamp):
    path = RAW / f"CCPI_and_CCPI_CORE_{stamp}_e.xlsx"
    if path.exists():
        print("Already have", path.name)
        return path
    time.sleep(CRAWL_DELAY)
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)
    print("Downloaded", path.name, f"({len(r.content)} bytes)")
    return path


def parse(path):
    ws = openpyxl.load_workbook(path, data_only=True).active
    rows = list(ws.iter_rows(values_only=True))

    # Layout check: the title and the column labels must be what we expect
    title = str(rows[0][1])
    labels = " ".join(str(c) for c in rows[2] + rows[3] if c)
    if "CCPI" not in title or "2021=100" not in title or "Year-on-Year" not in labels:
        raise RuntimeError("Layout changed: this does not look like the CCPI (2021=100) table")

    records = []
    for r in rows:
        period = str(r[1]).strip() if r[1] else ""
        if re.fullmatch(r"20\d\d [A-Za-z]+", period):
            month = datetime.strptime(period, "%Y %B").strftime("%Y-%m")
            records.append({
                "month": month,
                "ccpi_index": r[2], "core_index": r[3],
                "ccpi_monthly_pct": r[4], "core_monthly_pct": r[5],
                "ccpi_yoy_pct": r[6], "core_yoy_pct": r[7],
                "ccpi_annual_avg_pct": r[8], "core_annual_avg_pct": r[9],
            })
    df = pd.DataFrame(records).set_index("month").sort_index()
    return df


def check(df):
    assert len(df) >= 12, "fewer than 12 months found"
    assert not df.index.duplicated().any()
    # turn "2026-03" into a month counter (year x 12 + month); consecutive months differ by 1
    counter = [int(m[:4]) * 12 + int(m[5:7]) for m in df.index]
    assert all(b - a == 1 for a, b in zip(counter, counter[1:])), "months are not consecutive"
    assert df["ccpi_yoy_pct"].between(-20, 100).all(), "inflation outside -20% to 100%"
    assert df["ccpi_index"].between(50, 1000).all(), "index outside the expected range"


def main():
    url, stamp = find_latest_link()
    print("Newest CCPI file on the CBSL page is dated", stamp)
    path = download(url, stamp)

    new = parse(path)
    check(new)

    # Add to our growing history: new rows overwrite old ones for the same month
    if HISTORY.exists():
        old = pd.read_csv(HISTORY, index_col="month")
        history = pd.concat([old[~old.index.isin(new.index)], new]).sort_index()
        added = len(history) - len(old)
    else:
        history, added = new, len(new)
    history.to_csv(HISTORY)

    latest = history.index.max()
    print(f"\nSaved {HISTORY}   ({len(history)} months, {history.index.min()} to {latest}; {added} new)")
    print("Data as of:", latest)
    print("\nLast 3 months:")
    print(history.tail(3)[["ccpi_index", "ccpi_yoy_pct", "core_yoy_pct"]].to_string())


if __name__ == "__main__":
    main()
