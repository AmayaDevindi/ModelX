# ModelX 2.0 – team pack (read this first)

Last updated: Thu 15 Oct 2026, by Amaya

This folder has everything you need to know about what we're building, how it fits together and what's due when. No chat history – just the plan.

## The project in one paragraph
A website for Sri Lankans who have money to invest but don't know where to put it. You enter how much you have, answer a short risk quiz, pick your goal (growth or monthly income) and how long you can leave the money. The site suggests how to split it across savings accounts, FDs, T-bills, T-bonds, unit trusts and S&P SL20 stocks, and shows a likely / bad / good range, the chance of ending up with less than you started, and what the same money would do in an FD after inflation. Market data refreshes automatically through the day. It's educational, never advice, and it says clearly when the data isn't good enough.

## Deadlines (firm – miss one and we're out)
| Date | What |
|---|---|
| **Mon 19 Oct** | Proposal submitted |
| **Sun 1 Nov** | Working system + public GitHub repo + report + 2-page summary + 3-min video |
| Mon 9 Nov | Top 15 announced |
| **Sat 14 Nov** | Live pitch |

## Read in this order
1. `01-project-brief.md` – goal, user, what the site shows
2. `02-decisions.md` – every decision so far (D1–D30). Don't change one without telling the team
3. `03-system-design.md` – how data flows from sources to the website, and what "real time" means for us
4. `04-models.md` – the three models (investor profile, fundamental analysis, news) and how they connect to the forecast + split
5. `05-pdf-extraction.md` – how we get numbers out of PDFs
6. `06-news-linking.md` – how a headline gets tied to a stock, sector or instrument
7. `07-data-sources.md` – where each piece of data comes from and what still needs checking
8. `08-timeline-and-tasks.md` – buckets, dates, who does what
9. `09-competition-rules.md` – booklet summary: judging, rules, what to submit
10. `10-glossary.md` – terms if you're new to finance or ML

## Three rules we don't break
- **No invented numbers.** Every figure comes from a real source or a real pull. If we don't have it, write `[NEED: …]`.
- **Never promise profit.** Ranges and chance of loss, always with "data as of".
- **Log AI use.** Anything Claude (or any AI) helped with goes in `docs/ai_use_log.md` in the repo. We must be able to explain every line ourselves.

## Where things live
- Repo: currently only on Amaya's laptop – will be pushed to a **public** GitHub repo (private repo = no submission). Link: [NEED: repo URL]
- Decisions log in the repo: `docs/decisions.md` (the repo copy wins if it differs from this pack)
- Competition booklet: https://modelx2.pages.dev/
