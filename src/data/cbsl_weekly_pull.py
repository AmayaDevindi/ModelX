"""
Read the latest T-bill and T-bond yields from CBSL's Weekly Economic Indicators PDF.

Source : https://www.cbsl.gov.lk/en/statistics/economic-indicators/weekly-indicators
         A new PDF (WEI_YYYYMMDD_e.pdf) comes out every Friday.
         Table 3.5 = Two Way Quotes (Treasury Bills), 1 week to 12 months
         Table 3.6 = Two Way Quotes (Treasury Bonds), one row per bond series
Method : find the newest PDF link, download it (10 s crawl delay), read the two tables
         with pdfplumber, check they look right, and add them to a growing history.

Writes : data/raw/cbsl/WEI_YYYYMMDD_e.pdf     (untouched copy)
         data/clean/cbsl_tbill_curve.csv      (one row per maturity per week)
         data/clean/cbsl_tbond_curve.csv      (one row per bond per week)

Run from the ModelX folder:  python src/data/cbsl_weekly_pull.py
"""

import re
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import pdfplumber
import requests

PAGE = "https://www.cbsl.gov.lk/en/statistics/economic-indicators/weekly-indicators"
HEADERS = {"User-Agent": "ModelX student project (educational)"}
CRAWL_DELAY = 10

RAW = Path("data/raw/cbsl")
CLEAN = Path("data/clean")
RAW.mkdir(parents=True, exist_ok=True)
CLEAN.mkdir(parents=True, exist_ok=True)

NUM = r"([\d,]*\.?\d+)"
TBILL_LINE = re.compile(rf"^(1-7 Days|\d+ Months?)\s+{NUM}\s+{NUM}\s+{NUM}\s+{NUM}\s+{NUM}$")
TBOND_LINE = re.compile(
    rf"^(\d\d\.\d+%\d{{4}}\s?[A-Z]?)\s+(\d+)\s+(\d\d-[A-Za-z]{{3}}-\d\d)\s+{NUM}\s+{NUM}\s+{NUM}\s+{NUM}\s+{NUM}\s+{NUM}$"
)


def find_latest_pdf():
    resp = requests.get(PAGE, headers=HEADERS, timeout=30)
    html = resp.text
    found = re.findall(r'href="([^"]*WEI_(\d{8})_e\.pdf)"', html)
    if not found:
        raise RuntimeError("Could not find a weekly PDF link on the CBSL page. "
                           f"Status {resp.status_code}, {len(html)} characters, starts: "
                           f"{html[:200]!r}")
    url, stamp = max(found, key=lambda x: x[1])
    if url.startswith("/"):
        url = "https://www.cbsl.gov.lk" + url
    return url, stamp


def download(url, stamp):
    path = RAW / f"WEI_{stamp}_e.pdf"
    if path.exists():
        print("Already have", path.name)
        return path
    time.sleep(CRAWL_DELAY)
    r = requests.get(url, headers=HEADERS, timeout=120)
    r.raise_for_status()
    path.write_bytes(r.content)
    print("Downloaded", path.name, f"({len(r.content)} bytes)")
    return path


def read_tables(pdf_path):
    """Return (as_of_date, tbill_rows, tbond_rows) read from the PDF text."""
    as_of, bills, bonds = None, [], []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if "Two Way Quotes (Treasury Bills)" not in text:
                continue
            mode = None
            for line in text.splitlines():
                line = line.strip()
                m = re.search(r"Two Way Quotes \(Treasury Bills\)\s*-\s*(\d+ [A-Za-z]+ \d{4})", line)
                if m:
                    as_of = datetime.strptime(m.group(1), "%d %B %Y").date()
                    mode = "bills"
                elif "Two Way Quotes (Treasury Bonds)" in line:
                    mode = "bonds"
                elif re.match(r"^3\.7\b", line):
                    mode = None
                elif mode == "bills" and TBILL_LINE.match(line):
                    bills.append(TBILL_LINE.match(line).groups())
                elif mode == "bonds" and TBOND_LINE.match(line):
                    bonds.append(TBOND_LINE.match(line).groups())
    return as_of, bills, bonds


def to_float(x):
    return float(str(x).replace(",", ""))


def build_frames(as_of, bills, bonds):
    tb = pd.DataFrame(bills, columns=["maturity", "buy_price", "buy_yield", "sell_price", "sell_yield", "spread"])
    for c in tb.columns[1:]:
        tb[c] = tb[c].map(to_float)
    tb.insert(1, "maturity_months", [0.1 if m.startswith("1-7") else int(m.split()[0]) for m in tb["maturity"]])

    bd = pd.DataFrame(bonds, columns=["series", "maturity_years", "maturity_date", "days_to_maturity",
                                      "buy_price", "buy_yield", "sell_price", "sell_yield", "spread"])
    for c in ["maturity_years", "days_to_maturity", "buy_price", "buy_yield", "sell_price", "sell_yield", "spread"]:
        bd[c] = bd[c].map(to_float)
    bd["maturity_date"] = pd.to_datetime(bd["maturity_date"], format="%d-%b-%y").dt.date

    tb.insert(0, "as_of", as_of)
    bd.insert(0, "as_of", as_of)
    return tb, bd


def check(as_of, tb, bd):
    assert as_of is not None, "could not read the date of the quotes"
    assert len(tb) == 13, f"expected 13 T-bill maturities, found {len(tb)}"
    assert len(bd) >= 30, f"expected at least 30 T-bond series, found {len(bd)}"
    for name, df in (("T-bill", tb), ("T-bond", bd)):
        for col in ("buy_yield", "sell_yield"):
            assert df[col].between(0, 40).all(), f"{name} {col} outside 0-40%"
    assert (bd["days_to_maturity"] > 0).all(), "a bond has already matured"
    assert (tb["buy_yield"] >= tb["sell_yield"]).all(), "buying yield should be at least the selling yield"


def add_to_history(new, path):
    """Append this week's rows; if the same week is already there, replace it."""
    if path.exists():
        old = pd.read_csv(path)
        old = old[old["as_of"] != str(new["as_of"].iloc[0])]
        new = pd.concat([old, new], ignore_index=True)
    new.to_csv(path, index=False)
    return new


def main():
    url, stamp = find_latest_pdf()
    print("Newest weekly PDF on the CBSL page is dated", stamp)
    pdf_path = download(url, stamp)

    as_of, bills, bonds = read_tables(pdf_path)
    tb, bd = build_frames(as_of, bills, bonds)
    check(as_of, tb, bd)

    tb_all = add_to_history(tb, CLEAN / "cbsl_tbill_curve.csv")
    bd_all = add_to_history(bd, CLEAN / "cbsl_tbond_curve.csv")

    print(f"\nQuotes as of {as_of}: {len(tb)} T-bill maturities, {len(bd)} T-bond series")
    print(f"History now holds {tb_all['as_of'].nunique()} week(s)")
    print("\nT-bill yield curve (buying yield):")
    print(tb[["maturity", "buy_yield"]].to_string(index=False))
    print("\nShortest and longest T-bond:")
    print(bd.sort_values("days_to_maturity").iloc[[0, -1]][["series", "maturity_date", "buy_yield"]].to_string(index=False))


if __name__ == "__main__":
    main()
