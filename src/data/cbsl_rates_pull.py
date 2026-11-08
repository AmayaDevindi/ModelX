"""
Download CBSL's monthly interest-rate table and turn it into a clean CSV.

Source : CBSL Statistical Tables, Monetary Sector, "4.04 Interest Rates - Monthly"
         https://www.cbsl.gov.lk/en/statistics/statistical-tables/monetary-sector
Method : the page links to an Excel file whose name contains its publication date
         (table4.04_YYYYMMDD.xlsx), so we read the page, find the newest link,
         download it, and parse it.
Politeness: CBSL's robots.txt asks for a 10 second crawl delay, so we wait 10 s
         between the two requests. We download once a day at most.

Reads  : the CBSL web page
Writes : data/raw/cbsl/table4.04_YYYYMMDD.xlsx   (untouched copy)
         data/clean/cbsl_rates_monthly.csv       (one row per month)

Run from the ModelX folder:  python src/data/cbsl_rates_pull.py
"""

import re
import time
from pathlib import Path

import openpyxl
import pandas as pd
import requests

PAGE = "https://www.cbsl.gov.lk/en/statistics/statistical-tables/monetary-sector"
HEADERS = {"User-Agent": "ModelX student project (educational)"}
CRAWL_DELAY = 10

RAW = Path("data/raw/cbsl")
CLEAN = Path("data/clean")
RAW.mkdir(parents=True, exist_ok=True)
CLEAN.mkdir(parents=True, exist_ok=True)

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# column position in the sheet -> (our name, text that must appear in that column's header)
# If CBSL changes the layout, the header check below fails and the pipeline stops.
COLUMNS = {
    3: ("opr", "OPR"),
    4: ("sdfr", "SDFR"),
    7: ("tbill_3m", "3-Month"),
    8: ("tbill_12m", "12-Month"),
    12: ("fd_12m", "12 Months"),
    14: ("savings", "Savings"),
    15: ("awdr", "AWDR"),
    16: ("awfdr", "AWFDR"),
    17: ("awndr", "AWNDR"),
    18: ("awnfdr", "AWNFDR"),
    24: ("awpr", "AWPR"),
}
RANGE_COLUMNS = {"fd_12m", "savings"}    # these are printed as "low-high" in recent years


def find_latest_link():
    resp = requests.get(PAGE, headers=HEADERS, timeout=30)
    html = resp.text
    found = re.findall(r'href="([^"]*table4\.04_(\d{8})\.xlsx)"', html)
    if not found:
        raise RuntimeError("Could not find the table 4.04 link on the CBSL page. "
                           f"Status {resp.status_code}, {len(html)} characters, starts: "
                           f"{html[:200]!r}")
    url, stamp = max(found, key=lambda x: x[1])
    if url.startswith("/"):
        url = "https://www.cbsl.gov.lk" + url
    return url, stamp


def download(url, stamp):
    path = RAW / f"table4.04_{stamp}.xlsx"
    if path.exists():
        print("Already have", path.name)
        return path
    time.sleep(CRAWL_DELAY)
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)
    print("Downloaded", path.name, f"({len(r.content)} bytes)")
    return path


def to_number(cell):
    """Turn a cell into a float. Returns None for blanks like 'n.a.'"""
    if cell is None:
        return None
    if isinstance(cell, (int, float)):
        return float(cell)
    text = re.sub(r"\([a-z]\)", "", str(cell)).strip()      # drop footnote marks like (o)
    try:
        return float(text)
    except ValueError:
        return None


def to_range(cell):
    """'2.50-12.00' -> (2.5, 12.0).  A single number -> (n, n)."""
    if isinstance(cell, (int, float)):
        return float(cell), float(cell)
    text = re.sub(r"\([a-z]\)", "", str(cell or "")).strip()
    parts = text.split("-")
    try:
        if len(parts) == 2:
            return float(parts[0]), float(parts[1])
        return float(text), float(text)
    except ValueError:
        return None, None


def parse(path):
    ws = openpyxl.load_workbook(path, data_only=True).active
    rows = list(ws.iter_rows(values_only=True))

    # 1. Check the layout is what we expect (header rows are rows 4 to 9)
    for col, (name, must_contain) in COLUMNS.items():
        header = " ".join(str(rows[i][col]) for i in range(3, 9) if rows[i][col] is not None)
        if must_contain not in header:
            raise RuntimeError(f"Layout changed: column {col} should be '{must_contain}' "
                               f"but the header says '{header[:60]}'")

    # 2. Read one record per month (the year is only written on its first row)
    records, year = [], None
    for r in rows[9:]:
        if isinstance(r[1], (int, float)):
            year = int(r[1])
        if r[2] in MONTHS and year:
            rec = {"month": f"{year}-{MONTHS.index(r[2]) + 1:02d}"}
            for col, (name, _) in COLUMNS.items():
                if name in RANGE_COLUMNS:
                    rec[name + "_min"], rec[name + "_max"] = to_range(r[col])
                else:
                    rec[name] = to_number(r[col])
            records.append(rec)

    df = pd.DataFrame(records).set_index("month")
    return df


def check(df):
    """Stop if the data looks wrong. Better a failed run than a wrong number."""
    assert len(df) > 250, "far fewer months than expected"
    assert df.index.is_monotonic_increasing and not df.index.duplicated().any()
    rates = df.drop(columns=[c for c in df.columns if c.startswith("savings")], errors="ignore")
    assert (rates.stack().dropna().between(0, 60)).all(), "a rate is outside 0-60%"
    latest = df.dropna(subset=["awnfdr", "tbill_12m"]).index.max()
    return latest


def main():
    url, stamp = find_latest_link()
    print("Newest table 4.04 on the CBSL page is dated", stamp)
    path = download(url, stamp)

    df = parse(path)
    latest = check(df)
    out = CLEAN / "cbsl_rates_monthly.csv"
    df.to_csv(out)

    print(f"\nSaved {out}   ({len(df)} months, {df.index.min()} to {df.index.max()})")
    print("Data as of (last month with deposit and T-bill rates):", latest)
    print("\nLast 3 months:")
    print(df.loc[:latest].tail(3)[["tbill_12m", "fd_12m_min", "fd_12m_max", "awfdr", "awnfdr"]].to_string())


if __name__ == "__main__":
    main()
