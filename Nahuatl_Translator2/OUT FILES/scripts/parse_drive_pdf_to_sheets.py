"""
Download a PDF from Google Drive, parse its text, and write it to Google Sheets.

Drive file ID  : 1d64U8NF-AKugpaVwUB8T2EyYxdg3rCza
Spreadsheet ID : 12ebNz0hxWwoXEpDcXITuRN1q9Q2dlVXwiaJd2YQWUP4
"""

import io
import json
import PyPDF2

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import gspread

TOKEN_PATH      = "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json"
CREDS_PATH      = "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/credentials.json"
DRIVE_FILE_ID   = "1d64U8NF-AKugpaVwUB8T2EyYxdg3rCza"
SPREADSHEET_ID  = "12ebNz0hxWwoXEpDcXITuRN1q9Q2dlVXwiaJd2YQWUP4"
SHEET_NAME      = "Sheet1"
PDF_LOCAL_PATH  = "/tmp/drive_parsed.pdf"

# ── 1. Load & refresh OAuth credentials ──────────────────────────────────────
with open(TOKEN_PATH) as f:
    tok = json.load(f)
with open(CREDS_PATH) as f:
    cred_info = json.load(f)["installed"]

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
    print("Token refreshed.")

# ── 2. Download PDF from Drive ────────────────────────────────────────────────
drive = build("drive", "v3", credentials=creds)
request = drive.files().get_media(fileId=DRIVE_FILE_ID)

with io.FileIO(PDF_LOCAL_PATH, "wb") as fh:
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"  Download: {int(status.progress() * 100)}%")

print(f"PDF saved to {PDF_LOCAL_PATH}")

# ── 3. Parse PDF text ─────────────────────────────────────────────────────────
rows = []  # [page_label, line_text]

with open(PDF_LOCAL_PATH, "rb") as f:
    reader = PyPDF2.PdfReader(f)
    total_pages = len(reader.pages)
    print(f"PDF pages: {total_pages}")

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for line in lines:
            rows.append([f"p{page_num}", line])

print(f"Extracted {len(rows)} lines across {total_pages} pages.")
if rows:
    print("First 5 lines:")
    for r in rows[:5]:
        print(" ", r)

# ── 4. Write to Google Sheets ─────────────────────────────────────────────────
gc = gspread.authorize(creds)
sh = gc.open_by_key(SPREADSHEET_ID)

try:
    ws = sh.worksheet(SHEET_NAME)
except gspread.exceptions.WorksheetNotFound:
    ws = sh.add_worksheet(title=SHEET_NAME, rows=len(rows) + 10, cols=2)

ws.clear()
ws.update("A1", [["Page", "Text"]] + rows)
print(f"Written {len(rows)} rows to '{SHEET_NAME}' in spreadsheet {SPREADSHEET_ID}.")
