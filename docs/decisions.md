# 02 – Decisions log

Mirror of `docs/decisions.md` in the repo – the repo copy wins. New decisions from 15 Oct evening are D25–D30.

| # | Decision | Why |
|---|---|---|
| D1 | ~~S&P SL20, unit trusts, T-bills, T-bonds, FDs~~ – replaced by D8 | – |
| D2 | Never promise profit; show ranges and probability of loss | Honesty is scored |
| D3 | "Data as of" on every number; local + global news as context. Refresh timing now set by D25 | Data work 30% + Best Data Vision |
| D4 | ML forecasts return and risk → optimiser builds the split → always tested vs a historical-average baseline | Proves (or honestly admits) the ML adds value |
| D5 | Data collected by scheduled scripts (GitHub Actions), not an AI agent | Reliable, free, visible git history |
| D6 | Proposal 19 Oct, product 1 Nov, final 14 Nov | Booklet |
| D7 | News scored by us, not reused from another site (method in D21) | Reuse = retrieval, not insight |
| D8 | All available options: savings, FDs, T-bills, T-bonds, unit trusts (one per fund type), S&P SL20 only; debentures/gold only if free permitted data with history exists; insurance and FX out | No local tool splits across all of these |
| D9 | Beginners first, detail on click; laptop first; clean light dashboard, Bloomberg-style panels | Most savers are beginners |
| D10 | Home = market dashboard: rates monitor, headline insight, news panel with our sentiment, inputs form → allocation panel | Shows insight before the user types anything |
| D11 | Extras: (1) news + sentiment, (2) "what changed since last visit", (3) preset question buttons – first to cut | Keeps scope buildable |
| D12 | Optional login, only to save portfolios (on hold – D17) | – |
| D13 | Extra pages: trackers, unit trust explorer, SL20 screener, economy outlook | Market context in one place |
| D14 | Investment plan = one personal split + prediction (range over time, chance of loss, FD after inflation, monthly income) | The gap LankaBizz leaves |
| D15 | Existing-portfolio tracker = stretch goal after 1 Nov | Scope |
| D16 | Next.js on Vercel; Python pipeline in GitHub Actions writes JSON into the repo; no database for 1 Nov | Team skills, free hosting, git history |
| D17 | Login decided after 1 Nov | No personal data before deadline |
| D18 | All four D13 pages are must-have for 1 Nov | Team decision |
| D19 | Return forecasts with time-series models (ARIMA / Prophet) per asset, vs historical-average baseline | Suits rate and price series |
| D20 | Monte Carlo for return range and chance of loss; TradingView-style forecast chart | Likely / bad / good + % chance of loss |
| D21 | News sentiment: LLM API if we get free credits/student plan, otherwise FinBERT | Sri Lankan context vs free |
| D22 | Risk from a 5–6 question quiz; goal and liquidity as separate inputs | Mirrors broker client profiling |
| D23 | News from local sites, CSE announcements, CBSL press releases, a global feed – only if RSS/terms allow | Local first |
| D24 | Cite FGE monthly wrap-ups; model our weekly wrap on them | Licensed broker's view |
| **D25** | **"Real time" = hybrid.** Market data refreshed on a schedule (about every 30 min during CSE trading hours for prices + news; daily for rates, NAVs, inflation; when new PDFs appear for financial statements). The user's split, range and chance of loss are computed instantly on Vercel when they press the button. No live tick feed | Feels instant to the user, stays free, no database |
| **D26** | **Three models feed the split:** (1) investor profile, (2) fundamental analysis, (3) news linking + sentiment. Plus the forecast models (D19) and Monte Carlo (D20). See 04-models.md | Agreed model structure |
| **D27** | **Investor profile ("customer identification") = scored quiz**, not ML. Points → 5 risk bands → limits on the split (e.g. max stock share, min cash). Rules written down and shown to the user | No labelled training data exists; transparent and explainable |
| **D28** | **Fundamental analysis = both:** (a) ratios from SL20 financial statement PDFs → 0–100 score per stock (used on the screener and to pick the stock basket); (b) an ML model predicting next-period return from ratios, tested against the baseline and reported honestly even if it loses | Score is reliable; ML attempt shows rigour |
| **D29** | **Data from PDFs** extracted by Python (pdfplumber / camelot, OCR only if scanned), every number saved with source URL, page and date, checked by simple accounting rules; low-confidence numbers flagged, not used silently | Most of our data is PDF; data work is 30% |
| **D30** | **News effect = context + flag.** Each headline is linked to a stock, sector or instrument and scored. Shown beside that asset; strongly negative news raises a warning flag. News does **not** change the split's numbers | Sentiment-to-return link is unproven; avoids fake precision |

| **D31** | 18 Oct (stock market professional): **Model 1 adds age.** Quiz → 5 risk bands → the user picks from the instruments their band allows → age and horizon set the weights (glide path from growth to safer products). Fund menu modelled on fund managers like JB Vantage (money market, gilt, credit, equity) | Matches how advisers profile clients; refines D27 |
| **D32** | 18 Oct: **Model 2 output = A–E health grade**, not a league table. Five pillars: profitability & growth, financial strength, earnings quality (Piotroski tests), valuation, management & governance (fixed checklist from the annual report). Scored against the company's own sector; banks get bank ratios. The ML return model from D28 stays, tested vs baseline | Explainable "how good is this company"; refines D28 |
| **D33** | 18 Oct: **News = chain reaction**: headline → economic factor → sector → company, combined with the Model 2 grade into a positive / neutral / negative outlook (1–3 months) with a confidence level, for companies, sectors and the market. Outlooks feed the share part of the split but never break the risk-band limits. FastBull's 24/7 news-flash + economic calendar is the layout reference | Expert advice; **replaces D30** |
| **D34** | 18 Oct: **Login for 1 Nov** – greets the user by title and name ("Welcome back, Mrs Perera"), saves plans. Supabase Auth free tier; store only title, first name, email, quiz answers, saved plans; guest mode; delete on request | Personal feel; **replaces D17** |
| **D35** | 18 Oct: **Only Sri Lankan official / authorised data sources**: CBSL, CSE, Department of Census and Statistics, UTASL, Sri Lankan news outlets. Unit trust prices from UTASL (not Waraka). Global factors (oil, USD) from CBSL weekly indicators | Credibility; closes the Waraka question |
| **D36** | 18 Oct: **UI mimics the Bloomberg Terminal** (from the reel): dense panels, ticker strip, command bar ("JKH", "FD", "PLAN"). Light theme kept (D9). Charts with TradingView Lightweight Charts. Hosted on Vercel | Design reference |
| **D37** | 18 Oct: **Roles** – Member 1: data collection + pipeline, helps with the website. Member 2 (Amaya): ML and the three models. Member 3: UI/UX design + website | Team decision |

## Still open
- CSE gives only ~1 year of daily prices (checked 16 Oct) – archive daily from now; longer series from CBSL
- Written confirmation of CSE terms for its data endpoints – email CSE
- Free, permitted LKR gold price with history
- RSS terms for news sources other than EconomyNext
- LLM API credits (D21)
- Team name and team cards for the proposal
