# ModelX 2.0 – handover for Chanula and Thisara (18 Oct 2026)

Team **Fushiguro** · Proposal due **Mon 19 Oct 2026** · Repo: https://github.com/AmayaDevindi/ModelX

## What's already done
- Proposal written and built on the official template: `ModelX-Proposal.docx` (edit this) and `ModelX-Proposal.pdf` (upload this). 18 pages, all 12 sections filled.
- Data sources tested on 16–18 Oct: CSE, CBSL Data Library, UTASL unit prices, EconomyNext news. Screenshots are in the proposal (section 5.1) and in `evidence/`.
- Team cards filled: Chanula (Member 1, data), Amaya (Member 2, ML/models), Thisara (Member 3, UI/UX/website). Chanula's and Amaya's photos added.
- Every decision so far is in `docs/decisions.md` in the repo (D1–D41).

## What's left – do these in order

### 1. Add Thisara's photo (Thisara)
1. Open `ModelX-Proposal.docx` in Word.
2. Go to the last page (12. Team details). In the third card, click the yellow **[photo]** text and delete it.
3. Insert → Pictures → choose a clear, roughly square photo. Resize it to about the same size as the other two (3 cm wide).
4. Save.

### 2. Read it through (both)
- Read the whole document once. Check your own name, email and role.
- Fix small typos straight in Word. For anything bigger, message Amaya first.
- **Don't add numbers that aren't from a real source.** Every figure in it is cited.

### 3. Make the PDF (whoever did the last edit)
- In Word: File → Save As → PDF → name it `ModelX-Proposal.pdf`.
- Open the PDF and check: the cover says Fushiguro, the domain 01 box is ticked, all three photos show, and the screenshots show in section 5.

### 4. Submit on Monday 19 Oct (one person only – agree who in the group chat)
1. Open the form: https://forms.gle/G1w4HEiBAWyf8prGA (it asks you to sign in with Google).
2. Fill in the team details exactly as registered. Team name: **Fushiguro**.
3. Upload `ModelX-Proposal.pdf`.
   - If the form asks for a **Google Doc link** instead of a file: open the template (booklet site → "Copy template from here"), File → Make a copy, paste our content in section by section, set sharing to "Anyone with the link can view", and paste that link.
4. Submit **early in the day**, not at the last minute. Take a screenshot of the confirmation and post it in the group chat.

### 5. GitHub (after the submission)
- **Amaya** needs to run `git push` in the ModelX folder on her laptop. Four commits there aren't on GitHub yet: the latest proposal, the PDF, the team photos and decisions D40–D41.
- To join the repo, each of you:
  1. Make a free account at https://github.com/signup if you don't have one.
  2. Send your GitHub username to Amaya. She adds you under Settings → Collaborators → Add people.
  3. Accept the invite from your email or github.com/notifications.
  4. Get the code: `git clone https://github.com/AmayaDevindi/ModelX.git`
  5. Each time you work: `git pull` first. When you're done: `git add .` → `git commit -m "what you changed"` → `git push`.
- If you change the proposal after the photo is added, also save a copy into `docs/team/member3.jpg` in the repo so the build script keeps it.

## After the proposal (implementation, due Sun 1 Nov)
| Who | First job (from 20 Oct) |
|---|---|
| Chanula (data) | Turn on the daily data pipeline (`.github/workflows/daily_refresh.yml`, scripts in `src/data/`), then download the S&P SL20 annual and quarterly reports from the CSE |
| Amaya (ML) | Model 2 health grade for 5 companies, then the news chain and the questionnaire |
| Thisara (UI/UX) | Wireframes for the terminal layout: dark theme with a light switch; tabs MKTS, QUOTE, FA, RISK, NEWS, ECO, PLAN; command bar; login screen |

Read `docs/team-pack/README.md` first. It explains the whole plan in plain English.

## Key facts if someone asks
- **What it does:** a saver answers a short questionnaire and gets a personal split across savings, FDs, T-bills/bonds, unit trusts and S&P SL20 shares. It shows a range, the chance of loss, and the same money in an FD after inflation. Three models: customer identification, fundamental analysis (A–E health grade), and the news chain reaction.
- **The insight:** banks' average rate on new FDs (6.5–7.0% in early 2026) is below inflation (8.0% in Aug–Sep 2026), so a new FD is losing about 0.9% a year in real terms.
- **The data weak point:** the CSE gives only about 1 year of daily prices. We archive daily from now and use CBSL's longer monthly series.
- **The expert:** "a former stockbroker we consulted". Don't name him.
- **AI use** is disclosed in the proposal and in `docs/ai_use_log.md`. The rules allow it.
