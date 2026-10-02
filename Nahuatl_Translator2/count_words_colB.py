import gspread
import json
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

_HERE = os.path.dirname(os.path.abspath(__file__))

def _token_path():
    env = os.environ.get("GOOGLE_TOKEN_PATH")
    if env:
        return env
    if os.path.isdir("/storage/self/primary"):
        return "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json"
    return os.path.join(_HERE, "token.json")

TOKEN_PATH = _token_path()

with open(TOKEN_PATH) as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data.get('token'),
    refresh_token=token_data.get('refresh_token'),
    token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
    client_id=token_data.get('client_id'),
    client_secret=token_data.get('client_secret'),
    scopes=token_data.get('scopes'),
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

gc = gspread.authorize(creds)

sh = gc.open_by_key('12ebNz0hxWwoXEpDcXITuRN1q9Q2dlVXwiaJd2YQWUP4')
ws = sh.worksheet('Crispin')

# Get all values in col B (index 1), then slice from row 555 onward (0-indexed = 554)
col_b = ws.col_values(2)  # 1-indexed column number
total_rows = len(col_b)

# Rows 555 to end (sheet row 555 = index 554)
rows_from_555 = col_b[554:]

word_count = 0
non_empty = 0
for cell in rows_from_555:
    if cell.strip():
        non_empty += 1
        word_count += len(cell.split())

print(f"Total rows in col B: {total_rows}")
print(f"Rows 555 to {total_rows}: {len(rows_from_555)} rows")
print(f"Non-empty rows: {non_empty}")
print(f"Total word count (col B, rows 555–{total_rows}): {word_count:,}")
