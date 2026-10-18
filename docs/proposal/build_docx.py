import re, copy, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TPL, MD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
d = Document(TPL)
body = d.element.body

# ---------- parse markdown into sections ----------
md = open(MD, encoding='utf8').read().splitlines()
sections, key = {}, None
for line in md:
    m = re.match(r'^(#{1,2}) (\d+(?:\.\d+)?)\.? ', line)
    if m:
        key = m.group(2); sections[key] = []; continue
    if key: sections[key].append(line)

GREY = '7a7a7a'
def is_grey(p):
    runs = [r for r in p.runs if r.text.strip()]
    return runs and all(r.font.color is not None and r.font.color.rgb is not None and str(r.font.color.rgb).lower() == GREY for r in runs)

# ---------- cover + domain ----------
t0 = d.tables[0]
c = t0.cell(0, 1)
c.paragraphs[0].text = ''
r = c.paragraphs[0].add_run('Fushiguro')
dom = d.tables[1].cell(0, 0)
for p in dom.paragraphs:
    for rr in p.runs:
        if '☐' in rr.text: rr.text = rr.text.replace('☐', '☒')

# ---------- helpers ----------
def add_inline(p, text, size=None, bold_all=False):
    for tok in re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)', text):
        if not tok: continue
        b = i = False; mono = False
        if tok.startswith('**'): tok, b = tok[2:-2], True
        elif tok.startswith('*') and len(tok) > 1: tok, i = tok[1:-1], True
        elif tok.startswith('`'): tok = tok[1:-1]
        run = p.add_run(tok)
        run.bold = b or bold_all or None
        run.italic = i or None
        if size: run.font.size = Pt(size)
    return p

class Cursor:
    def __init__(self, el): self.el = el
    def put(self, el): self.el.addnext(el); self.el = el

def new_par(cur, text='', indent=None, hang=None, size=None, after=6, align_just=True, bold=False):
    p = d.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(after); pf.space_before = Pt(0); pf.line_spacing = 1.15
    if align_just: p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent is not None: pf.left_indent = Cm(indent)
    if hang is not None: pf.first_line_indent = Cm(-hang)
    add_inline(p, text, size, bold)
    cur.put(p._p)
    return p

def set_cell_bg(cell, hexcol):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcol)
    tcPr.append(shd)

def borders(tbl):
    tblPr = tbl._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '4'); e.set(qn('w:space'), '0'); e.set(qn('w:color'), 'BFBFBF')
        b.append(e)
    tblPr.append(b)

TEXT_W = d.sections[-1].page_width - d.sections[-1].left_margin - d.sections[-1].right_margin
WIDTHS = {3: [0.22, 0.40, 0.38], 4: [0.19, 0.22, 0.37, 0.22], 2: [0.5, 0.5]}

def new_table(cur, rows):
    ncol = len(rows[0])
    t = d.add_table(rows=len(rows), cols=ncol)
    borders(t); t.autofit = False
    fr = WIDTHS.get(ncol, [1/ncol]*ncol)
    if ncol == 3 and rows[0][0] in ('Part', 'Dates', 'Risk'): fr = [0.2, 0.45, 0.35] if rows[0][0] != 'Risk' else [0.33, 0.15, 0.52]
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = t.cell(ri, ci)
            cell.width = Emu(int(TEXT_W * fr[ci]))
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2); p.paragraph_format.space_before = Pt(2)
            add_inline(p, val, 9, bold_all=(ri == 0))
            if ri == 0: set_cell_bg(cell, 'E3EFEB')
    cur.put(t._tbl)
    # small gap after table
    gap = d.add_paragraph(); gap.paragraph_format.space_after = Pt(4); cur.put(gap._p)

def code_block(cur, lines):
    for ln in lines:
        p = d.add_paragraph()
        pf = p.paragraph_format; pf.space_after = Pt(0); pf.space_before = Pt(0); pf.line_spacing = 1.0
        run = p.add_run(ln if ln else ' '); run.font.name = 'Consolas'; run.font.size = Pt(8)
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Consolas')
        pPr = p._p.get_or_add_pPr(); shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), 'F2F2F2'); pPr.append(shd)
        cur.put(p._p)
    gap = d.add_paragraph(); gap.paragraph_format.space_after = Pt(2); cur.put(gap._p)

def render(cur, lines, is_refs=False):
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip(): i += 1; continue
        if ln.startswith('```'):
            j = i + 1; block = []
            while not lines[j].startswith('```'): block.append(lines[j]); j += 1
            code_block(cur, block); i = j + 1; continue
        mi = re.match(r'^!\[(.*)\]\((.*)\)$', ln)
        if mi:
            import os
            p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(2); p.paragraph_format.keep_with_next = True
            ip=os.path.join(os.path.dirname(os.path.abspath(MD)), mi.group(2))
            from PIL import Image as _I
            _w,_h=_I.open(ip).size
            p.add_run().add_picture(ip, width=Cm(7.5 if _h/_w>0.9 else 11.5))
            cur.put(p._p)
            cp = new_par(cur, mi.group(1), size=9, after=10, align_just=False)
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in cp.runs: r.italic = True
            i += 1; continue
        if ln.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'-+', c) for c in cells): rows.append(cells)
                i += 1
            new_table(cur, rows); continue
        if is_refs and ln.startswith('['):
            new_par(cur, ln, indent=0.9, hang=0.9, size=9.5, after=3, align_just=False); i += 1; continue
        m = re.match(r'^- (.*)', ln)
        if m: new_par(cur, '–\t' + m.group(1), indent=0.6, hang=0.45, after=3); i += 1; continue
        m = re.match(r'^(\d+)\. (.*)', ln)
        if m: new_par(cur, m.group(1) + '.\t' + m.group(2), indent=0.6, hang=0.45, after=3); i += 1; continue
        new_par(cur, ln); i += 1

# ---------- walk body: delete guidance, insert content after headings ----------
heads = []
for p in list(d.paragraphs):
    st = p.style.name
    if st in ('Heading 1', 'Heading 2'):
        m = re.match(r'^(\d+(?:\.\d+)?)\.?\s', p.text.strip())
        if m: heads.append((p, m.group(1)))
    elif is_grey(p):
        p._p.getparent().remove(p._p)

for p, k in heads:
    if k in sections:
        render(Cursor(p._p), sections[k], is_refs=(k == '11'))

# ---------- team cards ----------
TEAM = [
    {'name': 'Chanula Ramanayaka', 'email': 'unichanula@gmail.com', 'university': 'University of Moratuwa'},
    {'name': 'Amaya Devindi Walikatiyage', 'email': 'amayadevindiuni@gmail.com', 'university': 'University of Moratuwa'},
    {'name': 'Thisara Dewdunu Rajapaksha', 'email': 'thisaradewdunu174@gmail.com', 'university': 'University of Moratuwa'},
]
tt = d.tables[-1]
cells = [tt.cell(0, 0), tt.cell(0, 1), tt.cell(1, 0), tt.cell(1, 1)]
for idx, cell in enumerate(cells):
    for p in cell.paragraphs:
        t = p.text.strip().lower()
        if t in ('photo', 'name', 'email', 'university'):
            for rr in p.runs: rr.text = ''
            if idx < len(TEAM):
                if t == 'photo':
                    import os
                    ph = os.path.join(os.path.dirname(os.path.abspath(MD)), '..', 'team', f'member{idx+1}.jpg')
                    if os.path.exists(ph):
                        p.add_run().add_picture(ph, width=Cm(3))
                    else:
                        r = p.add_run('[photo]'); r.font.highlight_color = WD_COLOR_INDEX.YELLOW
                else:
                    r = p.add_run(TEAM[idx][t]); r.bold = (t == 'name') or None
d.save(OUT)
print('saved', OUT, 'sections', sorted(sections), 'heads', [k for _, k in heads])
