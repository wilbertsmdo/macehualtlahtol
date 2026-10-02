"""
Transcribe remaining pages of Tlallamiquiliztli inelhuayo (pages 34-207)
into the Crispin Google Sheet, one sentence per row in col B, starting at row 660.

Conventions observed in the existing transcription:
  - One sentence per row (split at . ? ! boundaries)
  - Dialogue attribution (— quiillia…) stays on the same row as its sentence
  - Leading — → "- ", internal — → " - ", closing —. → dropped (replaced by .)
  - ¿ ¡ stripped; « → <, » → >
  - Hyphenated word-breaks from PDF are rejoined
  - Page-number prefixes (e.g. "33—¿...") are stripped
"""

import re, json, time
import PyPDF2
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import gspread

TOKEN_PATH     = "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json"
SPREADSHEET_ID = "12ebNz0hxWwoXEpDcXITuRN1q9Q2dlVXwiaJd2YQWUP4"
PDF_LOCAL_PATH = "/tmp/inspect_drive.pdf"   # already downloaded
START_PDF_PAGE = 33   # 0-indexed; PDF page 34, first content after row 659
SHEET_START_ROW = 660  # first empty row in the sheet (1-indexed)

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

# ── PDF helpers ───────────────────────────────────────────────────────────────

def clean_line(line):
    """Strip leading page-number prefix (e.g. '33—¿' → '—¿', '34T...' → 'T...')."""
    # digits immediately followed by em-dash or a letter → strip digits
    return re.sub(r'^\d+(?=[—A-ZÁÉÍÓÚÜÑa-záéíóúüñ<])', '', line).strip()

def rejoin_hyphenated(lines):
    """Merge words broken across lines by a trailing hyphen."""
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # trailing word-hyphen: last char is '-', preceded by a letter
        while (line and line[-1] == '-'
               and len(line) > 1 and line[-2].isalpha()
               and i + 1 < len(lines)):
            i += 1
            line = line[:-1] + lines[i]
        result.append(line)
        i += 1
    return result

def apply_dash_conventions(text):
    """Replace em-dashes following the sheet convention."""
    # 1. Closing attribution marker —. → just .
    text = re.sub(r'—\.', '.', text)
    # 2. Closing attribution marker —, → just ,
    text = re.sub(r'—,', ',', text)
    # 3. Leading em-dash at start of text
    text = re.sub(r'^—', '- ', text)
    # 4. All remaining em-dashes → " - "
    text = text.replace('—', ' - ')
    # 5. Clean up artefacts: " - ." → "."  and " - ," → ","
    text = re.sub(r'\s*-\s*\.', '.', text)
    text = re.sub(r'\s*-\s*,', ',', text)
    return text

def split_sentences(text):
    """
    Split text into sentences following the sheet convention.
    A sentence boundary is [.?!>] followed by whitespace, BUT only if the
    next token does NOT start with '- ' (which signals an attribution tag).
    """
    # Split at sentence-ending punctuation followed by space,
    # unless the next segment starts with '- ' (attribution).
    # re.split with a capturing group keeps delimiters.
    parts = re.split(r'(?<=[.?!>])\s+(?!-\s)', text)
    return [p.strip() for p in parts if p.strip()]

def process_page(page, skip_first_line=False):
    """Extract, clean, and sentence-split one PDF page."""
    raw = page.extract_text() or ""
    lines = [clean_line(l) for l in raw.splitlines() if clean_line(l)]

    if skip_first_line and lines:
        lines = lines[1:]   # page 34: first line is already in sheet

    lines = rejoin_hyphenated(lines)
    if not lines:
        return []

    # Join lines into running text; em-dashes already in the text act as separators
    full_text = ' '.join(lines)

    # Apply character substitutions
    full_text = full_text.replace('«', '<').replace('»', '>')
    full_text = full_text.replace('¿', '').replace('¡', '')
    full_text = apply_dash_conventions(full_text)
    full_text = re.sub(r'  +', ' ', full_text).strip()

    return split_sentences(full_text)

# ── Extract sentences from PDF ────────────────────────────────────────────────
print("Reading PDF...")
with open(PDF_LOCAL_PATH, "rb") as f:
    reader = PyPDF2.PdfReader(f)
    total = len(reader.pages)
    print(f"  Total pages: {total}")

    all_sentences = []
    for idx in range(START_PDF_PAGE, total):
        page = reader.pages[idx]
        skip = (idx == START_PDF_PAGE)   # skip "Itztoc Isidro, ahui?" on page 34
        sents = process_page(page, skip_first_line=skip)
        all_sentences.extend(sents)
        if (idx - START_PDF_PAGE) % 20 == 0:
            print(f"  Processed page {idx+1}/{total} — {len(all_sentences)} sentences so far")

print(f"\nTotal sentences extracted: {len(all_sentences)}")
print("\nFirst 10:")
for s in all_sentences[:10]:
    print(f"  {s}")
print("\nLast 10:")
for s in all_sentences[-10:]:
    print(f"  {s}")

# ── Write to Google Sheet ─────────────────────────────────────────────────────
print(f"\nWriting {len(all_sentences)} rows to sheet starting at row {SHEET_START_ROW}...")

gc = gspread.authorize(creds)
ws = gc.open_by_key(SPREADSHEET_ID).worksheet("Crispin")

# Build rows: [A=empty, B=sentence, C=empty, D=empty, E=empty]
rows = [['', s, '', '', ''] for s in all_sentences]

# Expand the sheet to fit all new rows
needed_rows = SHEET_START_ROW + len(rows) - 1
current_rows = ws.row_count
if needed_rows > current_rows:
    ws.add_rows(needed_rows - current_rows)
    print(f"  Expanded sheet from {current_rows} to {needed_rows} rows")

# First 500 rows already written in previous run; resume from row 1160
ALREADY_WRITTEN = 500
resume_from = ALREADY_WRITTEN  # index into all_sentences

# Write in batches of 500 to stay within Sheets API limits
BATCH = 500
for start in range(resume_from, len(rows), BATCH):
    batch = rows[start:start + BATCH]
    sheet_row = SHEET_START_ROW + start
    end_row = sheet_row + len(batch) - 1
    range_str = f"A{sheet_row}:E{end_row}"
    ws.update(values=batch, range_name=range_str)
    print(f"  Wrote rows {sheet_row}–{end_row}")
    if start + BATCH < len(rows):
        time.sleep(1.5)

print("\nDone.")
