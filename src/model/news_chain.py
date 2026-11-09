"""
Step 1 of Model 3: tag each headline with an economic factor and a direction,
then follow a simple, STATED set of expert rules (factor -> sector) to show
which sectors a story likely affects and which way.

This is deliberately simple and keyword-based, not a learned model - see
docs/decisions.md (D7, D21, the 3 Nov scope cut) for why: no labelled data to
train on, no LLM/FinBERT budget confirmed yet, and no licensed adviser to
validate a learned chain against. The CHAIN_RULES below are OUR OWN
common-knowledge economic reasoning, written down so they can be checked and
argued with - NOT from a licensed financial adviser, and NOT yet tested
against how prices actually moved (that would need an event study, which
needs more price history than the one year the CSE currently gives us -
see docs/decisions.md, "CSE daily history is only about one year").

Reads : data/clean/news_headlines.csv
Writes: data/clean/news_chain_tags.csv
"""
import re
from pathlib import Path

import pandas as pd

CLEAN = Path(__file__).resolve().parents[2] / "data" / "clean"

# A headline mentioning any of these words is tagged with that factor.
FACTOR_KEYWORDS = {
    "Oil & fuel prices": ["oil", "crude", "fuel", "petrol", "diesel"],
    "Interest rates": ["interest rate", "policy rate", "repo rate", "cbsl rate", "monetary policy"],
    "Rupee / exchange rate": ["rupee", "lkr", "exchange rate", "forex", "dollar"],
    "Inflation": ["inflation", "ccpi", "cost of living"],
    "Tourism": ["tourist", "tourism", "arrivals"],
    "Tax policy": ["tax", "vat", "levy", "duty", "customs"],
}

# Words that say the thing named above is going UP vs DOWN. Generic on
# purpose - good enough for headline-level tagging, not perfect; a headline
# with no such word gets "unclear" rather than a guessed direction.
UP_WORDS = [
    "rise", "rises", "rising", "risen", "surge", "surges", "hike", "hikes", "hiked",
    "increase", "increases", "increased", "jump", "jumps", "soar", "soars", "gain",
    "gains", "higher", "record high", "strengthens", "strengthen", "appreciates",
]
DOWN_WORDS = [
    "fall", "falls", "falling", "fallen", "drop", "drops", "dropped", "cut", "cuts",
    "decline", "declines", "declined", "decrease", "decreases", "decreased", "plunge",
    "plunges", "slump", "lower", "slash", "slashes", "weakens", "weaken", "depreciates",
]

# factor -> direction -> list of (sector, effect, reason). "up" means the
# thing named by the factor is rising (oil price rising, rates rising, the
# rupee strengthening, more tourists, higher taxes).
CHAIN_RULES = {
    "Oil & fuel prices": {
        "up": [
            ("Transport & aviation", "negative", "higher fuel costs squeeze operating margins"),
            ("Manufacturing", "negative", "higher input and energy costs"),
            ("Oil & energy distribution", "positive", "higher margins on existing inventory/volumes"),
            ("Inflation (economy-wide)", "upward pressure", "fuel feeds into transport and goods prices"),
        ],
        "down": [
            ("Transport & aviation", "positive", "lower fuel costs"),
            ("Manufacturing", "positive", "lower input and energy costs"),
            ("Oil & energy distribution", "negative", "lower margins on existing inventory"),
            ("Inflation (economy-wide)", "downward pressure", "cheaper fuel eases transport and goods prices"),
        ],
    },
    "Interest rates": {
        "up": [
            ("Banks", "mixed", "wider lending margins, but bond holdings lose value and loan demand slows"),
            ("Property & construction", "negative", "higher borrowing costs discourage investment"),
            ("Savers in FDs / T-bills", "positive", "higher deposit and bill rates"),
        ],
        "down": [
            ("Banks", "mixed", "narrower lending margins, but bond holdings gain value and loan demand rises"),
            ("Property & construction", "positive", "cheaper borrowing encourages investment"),
            ("Savers in FDs / T-bills", "negative", "lower deposit and bill rates"),
        ],
    },
    "Rupee / exchange rate": {
        "up": [  # rupee strengthening
            ("Importers", "positive", "imports cost less in rupees"),
            ("Exporters (apparel, tea)", "negative", "export earnings worth less in rupees"),
            ("Inflation (economy-wide)", "downward pressure", "cheaper imported goods and fuel"),
        ],
        "down": [  # rupee weakening
            ("Importers", "negative", "imports cost more in rupees"),
            ("Exporters (apparel, tea)", "positive", "export earnings worth more in rupees"),
            ("Inflation (economy-wide)", "upward pressure", "costlier imported goods and fuel"),
        ],
    },
    "Inflation": {
        "up": [
            ("Fixed-income savers (FDs/bonds)", "negative", "real (after-inflation) returns erode faster"),
            ("CBSL policy", "pressure to raise rates", "central banks typically respond to rising inflation"),
        ],
        "down": [
            ("Fixed-income savers (FDs/bonds)", "positive", "real returns hold up better"),
            ("CBSL policy", "room to cut rates", "lower inflation gives room to ease policy"),
        ],
    },
    "Tourism": {
        "up": [
            ("Hotels & leisure", "positive", "more visitor spending"),
            ("Rupee / forex reserves", "positive", "more foreign currency inflow"),
        ],
        "down": [
            ("Hotels & leisure", "negative", "less visitor spending"),
            ("Rupee / forex reserves", "negative", "less foreign currency inflow"),
        ],
    },
    "Tax policy": {
        "up": [
            ("Consumer goods & retail", "negative", "higher costs passed to consumers, demand may fall"),
            ("Government revenue", "positive", "more tax collected"),
        ],
        "down": [
            ("Consumer goods & retail", "positive", "lower costs to consumers, demand may rise"),
            ("Government revenue", "negative", "less tax collected"),
        ],
    },
}


def _contains_word(text, phrase):
    """Whole-word/phrase match, so "vat" doesn't match inside "private" and
    "oil" doesn't match inside "turmoil" - a plain substring check got this
    wrong when we first tested it (caught on a real headline), so every
    keyword and direction word is checked this way."""
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern, text) is not None


def detect_direction(title_lower):
    has_up = any(_contains_word(title_lower, w) for w in UP_WORDS)
    has_down = any(_contains_word(title_lower, w) for w in DOWN_WORDS)
    if has_up and not has_down:
        return "up"
    if has_down and not has_up:
        return "down"
    return None  # unclear - headline doesn't give a clean direction either way


def classify_headline(title):
    """One tag per economic factor the headline mentions:
    {factor, direction, effects: [(sector, effect, reason), ...], confidence}.
    Empty list if the headline mentions none of our tracked factors."""
    title_lower = title.lower()
    direction = detect_direction(title_lower)
    tags = []
    for factor, keywords in FACTOR_KEYWORDS.items():
        if any(_contains_word(title_lower, kw) for kw in keywords):
            effects = CHAIN_RULES[factor].get(direction, []) if direction else []
            tags.append(dict(
                factor=factor,
                direction=direction or "unclear",
                effects=effects,
                confidence="low" if direction else "very low (no clear direction word)",
            ))
    return tags


def tag_all(news_df):
    rows = []
    for _, r in news_df.iterrows():
        for t in classify_headline(r["title"]):
            effects_text = "; ".join(f"{s}: {e} ({why})" for s, e, why in t["effects"])
            rows.append(dict(
                published=r["published"], title=r["title"], link=r["link"],
                factor=t["factor"], direction=t["direction"],
                effects=effects_text, confidence=t["confidence"],
            ))
    return pd.DataFrame(rows)


def main():
    news = pd.read_csv(CLEAN / "news_headlines.csv")
    tagged = tag_all(news)
    out = CLEAN / "news_chain_tags.csv"
    tagged.to_csv(out, index=False)
    n_distinct = tagged["title"].nunique() if len(tagged) else 0
    print(f"{len(news)} headlines read, {len(tagged)} factor tags found "
          f"across {n_distinct} distinct headlines.")
    if len(tagged):
        print("\nSample:")
        for _, r in tagged.head(5).iterrows():
            print(f"- [{r['factor']} {r['direction']}] {r['title']}")
            print(f"    -> {r['effects']}")


if __name__ == "__main__":
    main()
