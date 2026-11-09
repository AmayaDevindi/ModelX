# Notes for Claude (read before working in this repo)

## What this project is
ModelX 2.0 competition entry (IEEE CIS Student Chapter, IIT). Team of 3 ML beginners.
Domain: economy & livelihoods.

Goal: for Sri Lankans who have money to invest but don't know where, show how to split
it across FDs, T-bills/bonds, unit trusts and S&P SL20 stocks, with a return range,
chance of loss, and a comparison against an FD after inflation. Built on daily-refreshed
data plus ML forecasts, and it must say clearly when the data isn't strong enough.
Educational only, not advice.

Core decision it drives: "How should I split my money right now, given my risk and time horizon?"

## Deadlines
- Proposal: Mon 19 Oct 2026
- Implementation (report, public repo, 2-page summary, 3-min video): **Mon 10 Nov 2026** (confirmed - see D49)
- Final live pitch: Sat 14 Nov 2026

## Agreed decisions – do not drift from these without asking
See docs/decisions.md. Short version:
- Instruments: savings, FDs, T-bills, T-bonds, unit trusts, S&P SL20 stocks (D8)
- Three models: customer identification, fundamental analysis, news chain (D26, D31–D33)
- Sri Lankan official/authorised data sources only (D35)
- Never promise profit. Show ranges + probability of loss.
- Daily refresh, every number shows "data as of" date
- ML forecasts return + risk -> optimiser builds the split -> always compared to a simple baseline
- Data collected by a scheduled script (GitHub Actions), not an AI agent
- News feeds the outlook via a factor → sector → company chain (D33); we score it ourselves, we don't copy another site's predictions

## How the judges score (keep this in mind for every choice)
Implementation: data work 30%, insight 25%, engineering 25%, demo 20%.
Final: working live 35%, insight value 25%, problem size 20%, defending choices 20%.
"Retrieval is not insight" – showing prices is not enough.
Handling what the system doesn't know is scored.

## Rules for working here
- Small, runnable steps. After each step say how to check it worked.
- Keep code simple – the team must be able to explain every line when questioned.
- Never invent data or results. If a number isn't from a real pull, say so.
- Every data source needs: URL, method, history length, refresh rate, terms/robots.txt note.
- Add a line to docs/ai_use_log.md for any significant AI-written piece.
- Commit often with clear messages (git history is judged).
- Check every change against docs/decisions.md and flag anything that drifts.
