# 05 – Getting data out of PDFs (D29)

Most of our data comes as PDFs: company financial statements filed on the CSE, CBSL reports (rates, inflation, weekly indicators), and possibly unit trust fact sheets and bank rate sheets. We need clean numbers from them to train and run the models.

## Step by step
1. **Download** – the fetch script saves each PDF in `data/raw/<source>/` with the URL and download date recorded in a small log (`data/raw/index.csv`). Keep the original; it's our evidence.
2. **Is it text or a scan?** – try `pdfplumber` to read text. If a page gives almost no text, it's a scanned image → OCR.
3. **Find the right page** – search page text for headings like "Statement of Profit or Loss", "Statement of Financial Position", "Income Statement". Only process those pages.
4. **Pull the table**
   - Text PDFs: `pdfplumber` table extraction first; `camelot` (lattice mode for ruled tables, stream mode for unruled) if pdfplumber struggles.
   - Scanned PDFs: `pytesseract` OCR (via `pdf2image`), then parse lines. Slower and less accurate – flag as lower confidence.
5. **Match row labels** – companies word things differently ("Revenue" / "Turnover" / "Gross revenue"). Keep a synonyms list per line item in `pipeline/extract/labels.yml` and match with lower-casing + fuzzy matching (`rapidfuzz`).
6. **Fix the numbers** – brackets mean negative `(1,234)` → −1234; strip commas; read the unit from the header ("Rs. '000", "Rs. Mn") and convert everything to rupees; pick the current-period column, not the comparative.
7. **Check** (automatic):
   - Total assets ≈ total liabilities + total equity (within a small tolerance)
   - EPS ≈ profit attributable ÷ number of shares
   - Value not wildly different from last quarter without a reason (e.g. 10× jump → flag)
   - Required fields present
8. **Save** – one row per company per period per field in `data/fundamentals.csv` with: `symbol, period_end, field, value, unit, source_url, page, extracted_on, method (text/table/ocr), confidence, check_passed`.
9. **Failed or low-confidence rows** are not used by the models. They show "not scored" on the screener and go into a short manual-review list.

## How we prove it works (data work = 30% of the score)
- Hand-check a sample: e.g. 3 companies × 4 quarters, every field, against the PDF. Report the % correct.
- Keep a screenshot or two of a PDF page next to the extracted numbers for the report/demo.
- Write down which PDFs failed and why (scanned, unusual layout) – that's honest gap reporting.

## Libraries
`pdfplumber`, `camelot-py` (needs Ghostscript), `pytesseract` + Tesseract, `pdf2image` (needs Poppler), `rapidfuzz`, `pandas`. All open source – credit them in the README.

## Rules
- Only download what the site's robots.txt and terms allow; record the check in `docs/data_sources.md`.
- Don't hammer servers – pause between downloads.
- Don't put personal data in the repo (financial statements are public company data, which is fine).

## Starter sketch (to adapt, not final code)
```python
import pdfplumber

def find_statement_pages(path, keywords=("profit or loss", "income statement")):
    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = (page.extract_text() or "").lower()
            if any(k in text for k in keywords):
                pages.append(i)
    return pages

def to_number(s):
    s = s.strip().replace(",", "")
    if s.startswith("(") and s.endswith(")"):
        return -float(s[1:-1])
    return float(s)
```
