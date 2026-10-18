# 01 – Project brief

## Problem
Many Sri Lankans who save keep their money in savings accounts and FDs. When inflation is higher than the FD rate, that money quietly loses value. Other options exist (T-bills, T-bonds, unit trusts, shares) but there's no simple local tool that tells a normal person how to split *their* money across all of them, with an honest picture of the risk.

[NEED: real figures for the proposal – share of savings in FDs/savings accounts, number of CDS accounts, CCPI inflation vs FD rates over recent years. Sources to check: CBSL annual report, CSE/CDS reports, SEC reports.]

## Who it's for
Beginners first (people with savings who have never invested), with more detail on click for people who already invest. Laptop first.

Persona for the proposal: [NEED: one named persona, e.g. a 28-year-old salaried worker in Colombo with Rs 500k saved – team to agree]

## The decision it helps with
"How should I split my money right now, given my risk and time horizon?"

## Inputs
- Amount
- Risk appetite – from a 5–6 question quiz
- Goal – growth or monthly income
- Liquidity – might I need to withdraw early?
- Horizon – how long the money can stay invested

## Outputs
- A personal split across: savings account, FDs, T-bills, T-bonds, unit trusts (one per fund type), S&P SL20 stocks (debentures and gold only if we find free, permitted data with history)
- Value over time as a range: likely / bad / good case (Monte Carlo)
- Chance of ending below the starting amount
- Same money in an FD after inflation, side by side
- Expected monthly income
- "Data as of" on every number, and a clear message when the data is too thin to trust

## What the site has
- **Home = market dashboard** (light, multi-panel, Bloomberg-style layout): rates monitor (FD + savings by bank, T-bill/T-bond yields, ASPI, S&P SL20, unit trust NAVs, CCPI inflation, USD/LKR), a headline insight (e.g. "your FD is losing X% a year after inflation"), news panel with our own sentiment score, inputs form on the side → allocation panel
- **Tracker pages** with history charts: interest rates, inflation, FX, gold
- **Unit trust explorer**: NAV, returns, risk; filter and compare
- **S&P SL20 screener**: now also shows our fundamental score (see 04-models.md)
- **Economy / sector outlook** + our own weekly market wrap (modelled on First Guardian Equities' wrap-ups)
- Extras in priority order: (1) news + sentiment, (2) "what changed since your last visit", (3) preset question buttons ("Why this split?") – first to cut if short on time

## How we're different
- LankaBizz (https://lankabizz.net/) shows market data, a screener, a unit trust explorer and AI picks – but never tells a person how to split *their own* money.
- Waraka.lk tracks a portfolio you already hold.
- Bloomberg Terminal is the layout reference, not the complexity.
We combine market context + a personal split + an honest risk range + FD-after-inflation comparison, for beginners.

## Not doing for 1 Nov
Login (decided after 1 Nov), entering an existing portfolio (stretch goal), insurance and FX products, email alerts, LLM chat.
