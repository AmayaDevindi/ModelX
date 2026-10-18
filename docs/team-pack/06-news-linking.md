# 06 – Linking news to stocks and instruments (D30)

Goal: for every headline, know *what* it's about (a company, a sector, or the wider economy) and *whether* it's good or bad, then show it beside the right asset.

## Pipeline (runs about every 30 min)
1. **Collect** – RSS feeds / pages from local news sites, CSE announcements, CBSL press releases, and one global feed (oil, US rates, IMF). Only sources whose RSS/terms allow it (D23). Store: title, short summary (not full article text – copyright), URL, source, published time.
2. **De-duplicate** – the same story appears on several sites; merge near-identical titles (fuzzy match).
3. **Link to an asset** – in this order:
   - **Company match**: a lookup table `pipeline/models/entities.csv` with each SL20 company's ticker, full name and common short names (e.g. the ticker, the group name, well-known abbreviations). Match on whole words, case-insensitive. CSE announcements already name the company – link those directly. [NEED: build from the current S&P SL20 list on cse.lk – the list changes at rebalancing]
   - **Sector match**: if no company, a keyword list per sector (banking, telecom, plantations, hotels/tourism, manufacturing, construction, energy…) → every SL20 stock in that sector.
   - **Macro match**: keyword rules → instruments:
     - policy rate / interest rate / CBSL monetary board → FDs, savings, T-bills, T-bonds
     - inflation / CCPI / prices → everything (shown on the inflation tracker)
     - rupee / exchange rate / USD → FX tracker, import-heavy sectors
     - oil / fuel → energy, transport, inflation
     - IMF / debt restructuring / budget → T-bonds, whole market
   - **No match** → kept in the general news panel only.
   - If we get LLM credits, an LLM can do the linking + sentiment in one step and we compare it with the rules on the test set.
4. **Sentiment** – score each headline −1 (negative) to +1 (positive): LLM API if available, otherwise FinBERT (D21). FinBERT is trained on English financial news from elsewhere, so we test it on Sri Lankan headlines before trusting it.
5. **Aggregate per asset** – average sentiment over the last 7 days, newer articles weighted more; keep the article count.
6. **Flag** – show a warning on an asset when it has several recent articles and a clearly negative average [NEED: set the exact thresholds from the test set, not by guessing]. The flag lists the headlines with links so the user can read them.

## What it does NOT do
It doesn't change the split or the forecast numbers. We have no proof that local headline sentiment predicts returns, so using it in the maths would be false precision. If time allows after 1 Nov, we can test whether sentiment adds anything (vs a no-news baseline) and report the result.

## How we test it
- Hand-label about 100 recent headlines: which asset(s) it's about + positive/neutral/negative.
- Measure: linking accuracy (did we pick the right asset?) and sentiment accuracy (FinBERT vs LLM vs our labels).
- Report the numbers and the typical mistakes (e.g. sarcasm, Sinhala/Tamil names, "rates cut" being good for stocks but bad for FD savers).

## Output (example shape)
```json
{
  "as_of": "…",
  "assets": {
    "XXXX.N0000": { "sentiment_7d": 0.0, "articles": 0, "flag": false, "headlines": [] },
    "T-BILLS":    { "sentiment_7d": 0.0, "articles": 0, "flag": false, "headlines": [] }
  }
}
```
