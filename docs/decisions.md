# Decisions log

Add a row whenever we agree something. If we change a decision, don't delete the old row –
mark it "replaced by Dx" so we can explain our thinking to the judges.

| # | Date | Decision | Why |
|---|---|---|---|
| Goal | 12 Oct | Show how to split money across FDs, T-bills/bonds, unit trusts and S&P SL20 stocks, with return range, chance of loss, and FD-after-inflation comparison. Educational, not advice. | Most Sri Lankans who want to invest don't know the options; an allocation across instrument types is more defensible than picking single stocks |
| D1 | 12 Oct | ~~Instruments: S&P SL20 stocks first, plus unit trusts (Waraka.lk or fund sites), T-bills and T-bonds (CBSL / govt sites), FDs~~ – replaced by D8 | Covers all the main options a normal investor has, while keeping stocks manageable |
| D2 | 12 Oct | No promise of profit – show ranges and probability of loss | No model can guarantee returns; judges reward honesty |
| D3 | 12 Oct | Daily refresh, "data as of" date on every number. Track local + global news as context | Data currency is 30% of marks + Best Data Vision award; rates/inflation don't move faster anyway |
| D4 | 12 Oct | ML forecasts return and risk per instrument; optimiser builds the split; always tested against a historical-average baseline | Lets us prove (or honestly admit) the ML adds value |
| D5 | 12 Oct | Data collected by a scheduled script, not an AI agent | More reliable, free, and builds a visible git history |
| D6 | 12 Oct | Work to official deadlines: proposal 19 Oct, product 1 Nov | From the ModelX 2.0 booklet |
| D7 | open | News layer: which site inspired it, and do we score headlines ourselves (e.g. FinBERT) instead of reusing another site's predictions? | Reusing their prediction = retrieval, not our insight; many news sites forbid scraping |
| D8 | 15 Oct | Cover all investment options a Sri Lankan retail investor can realistically use: savings account, FDs, T-bills, T-bonds, unit trusts (one per fund type), and only part of the CSE (S&P SL20). Listed debentures and gold only if we find free, permitted data with history. Insurance plans and foreign-currency products are out. | Research (15 Oct) found no local tool that splits money across all of these; waraka.lk covers unit trusts only and CAL/Tukki sell their own products |

## Questions still open
- Name of the forex news site (link needed)
- How much price history the CSE API gives (Bucket 1 will tell us)
- Waraka.lk terms of use and data feed
