# 07 – Data sources

Status as of 15 Oct: **nothing has been pulled yet.** Scripts to test the sources are ready on Amaya's laptop (Claude's cloud sandbox can't reach .lk sites, so checks run locally). Every row below must be proven with a real sample pull before it goes in the proposal.

| Data | Planned source | Format | How often | History needed | Status |
|---|---|---|---|---|---|
| SL20 + ASPI prices, S&P SL20 index | CSE website (cse.lk) | web/JSON | ~30 min | years of daily prices | to check – **how much history the CSE gives is our biggest risk** |
| Company financial statements | CSE company announcements | PDF | daily check | several years of quarters | to check |
| CSE announcements (news) | CSE | web/PDF | ~30 min | – | to check |
| T-bill / T-bond yields, policy rates, USD/LKR | CBSL | web/PDF/Excel | daily | years | to check |
| CCPI inflation | CBSL / Dept. of Census & Statistics | PDF/Excel | monthly | years | to check |
| FD and savings rates by bank | bank websites / CBSL weekly indicators | web/PDF | daily | as much as possible | to check |
| Unit trust NAVs | fund managers' sites, Unit Trust Association, or Waraka.lk if its terms allow | web/PDF | daily | years | to check – Waraka terms unknown |
| Gold price (LKR) | [NEED: free, permitted source with history] | – | daily | – | open |
| Debentures | CSE | – | – | – | only if data exists |
| Local news | local news sites' RSS | RSS | ~30 min | – | to check terms per site |
| Global news | one global RSS feed (oil, US rates, IMF) | RSS | ~30 min | – | to check |
| Market commentary | First Guardian Equities market insight (fge.lk) – cited, not scraped into models | web | weekly/monthly | – | reference |

## What to record for every source (in `docs/data_sources.md`)
- URL and what exactly we take
- robots.txt result and terms of use (screenshot) – are we allowed?
- Sample pull: date, number of rows, earliest date available
- Gaps (missing days, changed formats)
- Fallback if it breaks

## Personal data
We collect none for 1 Nov – no login. Quiz answers are used for the calculation and not stored on our side.
