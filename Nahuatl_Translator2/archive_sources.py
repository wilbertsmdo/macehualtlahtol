"""
archive_sources.py
For every row in the Nahuatl Sources sheet:
  1. Download the Direct Document URL as a PDF (or directly if it already is one).
  2. Upload to Google Drive folder 1hfMOW4SE6gbSEffKKmX2hMqCSgf6i0qT.
  3. Write the Drive file link back to column M ("Archive (Google Drive)").

URL strategies:
  - *.pdf url            → requests GET
  - arxiv.org/abs/ID     → rewrite to arxiv.org/pdf/ID
  - aclanthology.org/X/  → try X.pdf
  - researchgate/pub/…   → requests first, fall back to Chromium
  - everything else      → Chromium headless --print-to-pdf

Run with Termux Python:
  /data/data/com.termux/files/usr/bin/python3 archive_sources.py
"""
import os, re, json, time, subprocess, requests, unicodedata
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import gspread
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request

# ── Config ────────────────────────────────────────────────────────────────
TOKEN_FILE  = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json'
SHEET_ID    = '11AEpdpY4cYNPoPn5ymZAP3SHygDoNzVPQpITQHxPrXM'
DRIVE_FOLDER= '1hfMOW4SE6gbSEffKKmX2hMqCSgf6i0qT'
SAVE_DIR    = Path('/storage/self/primary/PY_Projects/Macehualtlahtol/Nahuatl_Translator2/downloaded_sources')
PROGRESS    = Path('/storage/self/primary/PY_Projects/Macehualtlahtol/Nahuatl_Translator2/archive_progress.json')
CHROMIUM    = '/usr/bin/chromium'
COL_DOC_URL = 4   # column E (0-indexed) = Direct Document URL
COL_DRIVE   = 12  # column M (0-indexed) = Archive (Google Drive)
DRIVE_COL_LETTER = 'M'

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}

SAVE_DIR.mkdir(parents=True, exist_ok=True)

# ── Auth ──────────────────────────────────────────────────────────────────
creds = OAuthCredentials.from_authorized_user_file(TOKEN_FILE)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

gc       = gspread.authorize(creds)
ws       = gc.open_by_key(SHEET_ID).get_worksheet(0)
drive_svc = build('drive', 'v3', credentials=creds)

# ── Load progress ─────────────────────────────────────────────────────────
progress = json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {}

def save_progress():
    PROGRESS.write_text(json.dumps(progress, indent=2))

# ── Helpers ───────────────────────────────────────────────────────────────
def slugify(text, maxlen=60):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    text = re.sub(r'[^\w\s-]', '', text).strip()
    text = re.sub(r'[\s_-]+', '_', text)
    return text[:maxlen]

def pdf_url(url):
    """Rewrite URL to a direct PDF link where possible."""
    # ArXiv
    m = re.match(r'https?://arxiv\.org/abs/(.+)', url)
    if m:
        return f'https://arxiv.org/pdf/{m.group(1)}'
    # ACL Anthology  (https://aclanthology.org/L16-1666/ or /volumes/...)
    m = re.match(r'(https?://aclanthology\.org/[A-Z0-9\.\-]+)/?$', url)
    if m:
        return m.group(1) + '.pdf'
    # Already a PDF
    if url.lower().endswith('.pdf'):
        return url
    return None   # needs Chromium

def download_direct(url, dest):
    """Try to download url as a file. Returns True on success."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        if r.status_code == 200 and len(r.content) > 2000:
            dest.write_bytes(r.content)
            return True
    except Exception as e:
        print(f"    direct download error: {e}")
    return False

def chromium_pdf(url, dest):
    """Render url to PDF with Chromium headless. Returns True on success."""
    try:
        result = subprocess.run(
            [CHROMIUM, '--headless', '--no-sandbox', '--disable-gpu',
             '--disable-dev-shm-usage',
             f'--print-to-pdf={dest}', url],
            capture_output=True, timeout=60
        )
        return dest.exists() and dest.stat().st_size > 5000
    except Exception as e:
        print(f"    chromium error: {e}")
        return False

def upload_to_drive(filepath, name):
    """Upload file to Drive folder. Returns (file_id, webViewLink)."""
    meta  = {'name': name, 'parents': [DRIVE_FOLDER]}
    media = MediaFileUpload(str(filepath), mimetype='application/pdf', resumable=False)
    f = drive_svc.files().create(body=meta, media_body=media, fields='id,webViewLink').execute()
    return f['id'], f['webViewLink']

def update_sheet_cell(row_1based, col_0based, value):
    from gspread.utils import rowcol_to_a1
    cell = rowcol_to_a1(row_1based, col_0based + 1)
    ws.update([[value]], cell)

# ── Write header for column M if missing ─────────────────────────────────
headers_row = ws.row_values(1)
if len(headers_row) < COL_DRIVE + 1 or not headers_row[COL_DRIVE].strip():
    update_sheet_cell(1, COL_DRIVE, 'Archive (Google Drive)')
    ws.format(f'{DRIVE_COL_LETTER}1', {
        'textFormat': {'bold': True,
                       'foregroundColorStyle': {'rgbColor': {'red': 1, 'green': 1, 'blue': 1}}},
        'backgroundColorStyle': {'rgbColor': {'red': 0.2, 'green': 0.4, 'blue': 0.7}},
    })
    print("Header written to column M.")

# ── Main loop ─────────────────────────────────────────────────────────────
all_rows = ws.get_all_values()

for i, row in enumerate(all_rows[1:], start=2):   # row index 1-based, skip header
    # Get URL from column E; fall back to D if E is empty
    url = row[COL_DOC_URL].strip() if len(row) > COL_DOC_URL else ''
    if not url:
        url = row[3].strip() if len(row) > 3 else ''
    if not url:
        print(f"Row {i:2d}: no URL — skip")
        continue

    # Skip if already done
    if str(i) in progress:
        drive_link = progress[str(i)]
        print(f"Row {i:2d}: already done → {drive_link[:60]}")
        # Make sure it's written to the sheet
        cur = row[COL_DRIVE].strip() if len(row) > COL_DRIVE else ''
        if not cur:
            update_sheet_cell(i, COL_DRIVE, drive_link)
            time.sleep(0.5)
        continue

    title = row[2][:50] if len(row) > 2 else f'row{i}'
    fname = f"row{i:02d}_{slugify(title)}.pdf"
    dest  = SAVE_DIR / fname

    print(f"\nRow {i:2d}: {title[:50]}")
    print(f"         URL: {url[:80]}")

    # ── Determine & execute download strategy ────────────────────────────
    ok = False

    direct = pdf_url(url)
    if direct:
        print(f"    strategy: direct PDF → {direct[:70]}")
        ok = download_direct(direct, dest)
        if not ok:
            print("    direct failed → falling back to Chromium")
            ok = chromium_pdf(url, dest)
    elif 'researchgate.net/publication' in url:
        # Try direct first (some RG papers serve PDF); fall back to Chromium
        print("    strategy: ResearchGate → try requests then Chromium")
        ok = download_direct(url, dest)
        if not ok:
            ok = chromium_pdf(url, dest)
    else:
        print("    strategy: Chromium headless PDF")
        ok = chromium_pdf(url, dest)

    if not ok:
        print(f"    FAILED — skipping row {i}")
        progress[str(i)] = 'FAILED'
        save_progress()
        continue

    size_kb = dest.stat().st_size // 1024
    print(f"    saved: {fname} ({size_kb} KB)")

    # ── Upload to Drive ──────────────────────────────────────────────────
    try:
        fid, link = upload_to_drive(dest, fname)
        print(f"    uploaded → {link}")
    except Exception as e:
        print(f"    upload error: {e}")
        progress[str(i)] = 'UPLOAD_FAILED'
        save_progress()
        time.sleep(2)
        continue

    # ── Update sheet ─────────────────────────────────────────────────────
    try:
        update_sheet_cell(i, COL_DRIVE, link)
        time.sleep(0.5)
    except Exception as e:
        print(f"    sheet update error: {e}")

    progress[str(i)] = link
    save_progress()
    time.sleep(1)   # be polite between requests

print("\n\nAll rows processed.")
print(f"Progress saved to: {PROGRESS}")
print(f"Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
