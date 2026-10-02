"""
Transcribe Eduardo de la Cruz Cruz (2017) Cenyahtoc cintli tonacayo
pages 6-78 into the Eduardo Google Sheet, one sentence per row in col B,
section headers in col A, starting at row 4.

New sheet  : Cenyahtoc Cintli Tonacayo - Eduardo
Sheet ID   : 1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw
Worksheet  : Eduardo
Drive file : 1WKOPvuEO2qh9M5q5bWWC2YL-VEbD6xtw  (PDF)
Pages      : 6-78 (0-indexed 5-77)
Start row  : 4
"""

import re, json, time, io
import PyPDF2
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import gspread

TOKEN_PATH     = "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json"
SPREADSHEET_ID = "1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw"
WORKSHEET      = "Eduardo"
DRIVE_FILE_ID  = "1WKOPvuEO2qh9M5q5bWWC2YL-VEbD6xtw"
PDF_LOCAL_PATH = "/tmp/eduardo.pdf"
SHEET_START_ROW = 4
PDF_START_IDX   = 5   # 0-indexed → PDF page 6
PDF_END_IDX     = 78  # exclusive  → PDF page 78

# ── Auth ──────────────────────────────────────────────────────────────────────
with open(TOKEN_PATH) as f:
    tok = json.load(f)
creds = Credentials(
    token=tok["token"], refresh_token=tok["refresh_token"],
    token_uri=tok["token_uri"], client_id=tok["client_id"],
    client_secret=tok["client_secret"], scopes=tok["scopes"],
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    tok["token"] = creds.token
    tok["expiry"] = creds.expiry.isoformat() if creds.expiry else tok.get("expiry")
    with open(TOKEN_PATH, "w") as f:
        json.dump(tok, f, indent=2)

# ── Download PDF (if not already cached) ─────────────────────────────────────
import os
if not os.path.exists(PDF_LOCAL_PATH):
    print("Downloading PDF from Drive...")
    drive = build("drive", "v3", credentials=creds)
    request = drive.files().get_media(fileId=DRIVE_FILE_ID)
    with io.FileIO(PDF_LOCAL_PATH, "wb") as fh:
        dl = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = dl.next_chunk()
    print("Downloaded.")
else:
    print(f"Using cached PDF: {PDF_LOCAL_PATH}")

# ── Cleaning patterns ─────────────────────────────────────────────────────────
ROMAN = r'(?:i{1,3}|iv|vi{0,3}|ix|xi{0,3}|xii)'
ARTIFACT_RE  = re.compile(r'AL01B5-Srodki\.indb')
RUNHDR_RE    = re.compile(
    r'^(Cenyahtoc cintli tonacayo|Cequin ixnezcayotl tlen campeca)'
    r'.*\s+(' + ROMAN + r'|\d{1,3})$',
    re.IGNORECASE
)
FOOTNOTE_NUM = re.compile(r'^\d+$')
FOOTNOTE_TXT = re.compile(r'^\d{1,3}\s{2,}[A-ZÁÉÍÓÚÜa-z]')
TOC_LINE     = re.compile(r'\.{5,}')
ALLCAPS_RE   = re.compile(r'^[A-ZÁÉÍÓÚÜÑ\s:¿?/,()]+$')

SKIP_PAGES = {11}   # 0-indexed; page 12 = table of contents

def is_junk(line):
    return bool(
        ARTIFACT_RE.search(line) or
        RUNHDR_RE.match(line) or
        FOOTNOTE_NUM.match(line) or
        FOOTNOTE_TXT.match(line) or
        TOC_LINE.search(line)
    )

def rejoin_hyphenated(lines):
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        while (line and line[-1] == '-' and len(line) > 1
               and line[-2].isalpha() and i + 1 < len(lines)):
            i += 1
            line = line[:-1] + lines[i]
        result.append(line)
        i += 1
    return result

def split_sentences(text):
    parts = re.split(r'(?<=[.?!])\s+', text)
    return [p.strip() for p in parts if p.strip()]

def process_page(page_text):
    raw_lines = [ln.strip() for ln in page_text.splitlines() if ln.strip()]
    clean = [ln for ln in raw_lines if not is_junk(ln)]
    clean = rejoin_hyphenated(clean)

    sections = []
    prose_lines = []

    for ln in clean:
        if ALLCAPS_RE.match(ln) and len(ln.strip()) > 2:
            if prose_lines:
                sections.append(('prose', ' '.join(prose_lines)))
                prose_lines = []
            sections.append(('header', ln.strip()))
        else:
            prose_lines.append(ln)

    if prose_lines:
        sections.append(('prose', ' '.join(prose_lines)))

    rows = []
    for kind, content in sections:
        if kind == 'header':
            rows.append(('section', content))
        else:
            content = re.sub(r'  +', ' ', content).strip()
            for sent in split_sentences(content):
                rows.append(('sentence', sent))
    return rows

# ── Extract from PDF ──────────────────────────────────────────────────────────
print("Reading PDF...")
with open(PDF_LOCAL_PATH, "rb") as f:
    reader = PyPDF2.PdfReader(f)
    total = len(reader.pages)
    print(f"  Total pages: {total}")

    all_rows = []
    for idx in range(PDF_START_IDX, PDF_END_IDX):
        if idx in SKIP_PAGES:
            print(f"  [skip p.{idx+1} — ToC]")
            continue
        page_text = reader.pages[idx].extract_text() or ""
        if not page_text.strip():
            continue
        rows = process_page(page_text)
        all_rows.extend(rows)

n_sections  = sum(1 for k, _ in all_rows if k == 'section')
n_sentences = sum(1 for k, _ in all_rows if k == 'sentence')
print(f"\nExtracted {len(all_rows)} rows: {n_sections} section headers + {n_sentences} sentences")

# ── Write to Google Sheet ─────────────────────────────────────────────────────
print(f"\nWriting to sheet '{WORKSHEET}' starting at row {SHEET_START_ROW}...")

gc = gspread.authorize(creds)
ws = gc.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET)

# col A: section label or empty; col B: sentence or empty; C/D/E: empty
sheet_rows = []
for kind, text in all_rows:
    if kind == 'section':
        sheet_rows.append([text, '', '', '', ''])
    else:
        sheet_rows.append(['', text, '', '', ''])

needed = SHEET_START_ROW + len(sheet_rows) - 1
if needed > ws.row_count:
    ws.add_rows(needed - ws.row_count)
    print(f"  Expanded sheet to {needed} rows")

BATCH = 500
for start in range(0, len(sheet_rows), BATCH):
    batch = sheet_rows[start:start + BATCH]
    r1 = SHEET_START_ROW + start
    r2 = r1 + len(batch) - 1
    ws.update(values=batch, range_name=f"A{r1}:E{r2}")
    print(f"  Wrote rows {r1}–{r2} ({len(batch)} rows)")
    if start + BATCH < len(sheet_rows):
        time.sleep(1.5)

print(f"\nDone. {len(sheet_rows)} rows written to '{WORKSHEET}' starting at row {SHEET_START_ROW}.")
