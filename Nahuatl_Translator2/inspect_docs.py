"""Read-only: preview the Drive PDF and the target Google Sheet."""

import io, json, os
import PyPDF2
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import gspread

_HERE = os.path.dirname(os.path.abspath(__file__))

def _token_path():
    env = os.environ.get("GOOGLE_TOKEN_PATH")
    if env:
        return env
    if os.path.isdir("/storage/self/primary"):
        return "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json"
    return os.path.join(_HERE, "token.json")

def _creds_path():
    env = os.environ.get("GOOGLE_CREDS_PATH")
    if env:
        return env
    if os.path.isdir("/storage/self/primary"):
        return "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/credentials.json"
    return os.path.join(_HERE, "credentials.json")

TOKEN_PATH     = _token_path()
CREDS_PATH     = _creds_path()
DRIVE_FILE_ID  = "1d64U8NF-AKugpaVwUB8T2EyYxdg3rCza"
SPREADSHEET_ID = "12ebNz0hxWwoXEpDcXITuRN1q9Q2dlVXwiaJd2YQWUP4"
PDF_LOCAL_PATH = "/tmp/inspect_drive.pdf"

# ── Auth ──────────────────────────────────────────────────────────────────────
with open(TOKEN_PATH) as f:
    tok = json.load(f)

creds = Credentials(
    token=tok["token"],
    refresh_token=tok["refresh_token"],
    token_uri=tok["token_uri"],
    client_id=tok["client_id"],
    client_secret=tok["client_secret"],
    scopes=tok["scopes"],
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    tok["token"] = creds.token
    tok["expiry"] = creds.expiry.isoformat() if creds.expiry else tok.get("expiry")
    with open(TOKEN_PATH, "w") as f:
        json.dump(tok, f, indent=2)

# ── 1. Drive PDF ──────────────────────────────────────────────────────────────
drive = build("drive", "v3", credentials=creds)

meta = drive.files().get(fileId=DRIVE_FILE_ID, fields="name,mimeType,size").execute()
print(f"=== DRIVE FILE ===")
print(f"Name    : {meta['name']}")
print(f"Type    : {meta['mimeType']}")
print(f"Size    : {meta.get('size','?')} bytes")

request = drive.files().get_media(fileId=DRIVE_FILE_ID)
with io.FileIO(PDF_LOCAL_PATH, "wb") as fh:
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

with open(PDF_LOCAL_PATH, "rb") as f:
    reader = PyPDF2.PdfReader(f)
    total_pages = len(reader.pages)
    print(f"Pages   : {total_pages}")
    print()
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        print(f"--- Page {i} ({len(lines)} lines) ---")
        for ln in lines:
            print(" ", ln)
        print()

# ── 2. Google Sheet ───────────────────────────────────────────────────────────
gc = gspread.authorize(creds)
sh = gc.open_by_key(SPREADSHEET_ID)
print(f"=== GOOGLE SHEET ===")
print(f"Title      : {sh.title}")
worksheets = sh.worksheets()
print(f"Worksheets : {[ws.title for ws in worksheets]}")
print()
for ws in worksheets:
    data = ws.get_all_values()
    print(f"--- Sheet: '{ws.title}' ({len(data)} rows x {len(data[0]) if data else 0} cols) ---")
    for row in data[:20]:
        print(" ", row)
    if len(data) > 20:
        print(f"  ... ({len(data)-20} more rows)")
    print()
