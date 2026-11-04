"""
Pull recent Sri Lankan economy headlines from the EconomyNext RSS feed
(https://economynext.com/feed/; robots.txt allows it).

We keep only title, link, date and source, NOT the article text. Headlines are
context for the app ("what is in the news"), not a model input. Each run
appends new items to a growing file.

Output: data/clean/news_headlines.csv  (published, title, link, source)
Raw copy: data/raw/news/economynext_<date>.xml
"""
import sys
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

import pandas as pd
import requests

URL = "https://economynext.com/feed/"
HEADERS = {"User-Agent": "ModelX-student-project (educational; contact via GitHub repo)"}
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "news"
OUT = ROOT / "data" / "clean" / "news_headlines.csv"


def main():
    resp = requests.get(URL, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    rows = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = item.findtext("pubDate")
        if not (title and link and pub):
            continue
        when = parsedate_to_datetime(pub).astimezone().strftime("%Y-%m-%d %H:%M")
        rows.append({"published": when, "title": title, "link": link, "source": "EconomyNext"})
    if len(rows) < 5:
        sys.exit(f"FAILED: only {len(rows)} items in feed.")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = pd.Timestamp.today().strftime("%Y-%m-%d")
    (RAW_DIR / f"economynext_{stamp}.xml").write_bytes(resp.content)

    new = pd.DataFrame(rows)
    df = pd.concat([pd.read_csv(OUT), new]) if OUT.exists() else new
    df = df.drop_duplicates("link").sort_values("published").reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Feed items: {len(rows)}. File now {len(df)} headlines, {df['published'].min()} to {df['published'].max()}")


if __name__ == "__main__":
    main()
