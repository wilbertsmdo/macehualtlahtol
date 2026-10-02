"""Show rows 118-145 to confirm sentence/dash pattern."""
import json, os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import gspread

_HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = (
    os.environ.get("GOOGLE_TOKEN_PATH") or
    ("/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json"
     if os.path.isdir("/storage/self/primary")
     else os.path.join(_HERE, "token.json"))
)
SPREADSHEET_ID = "12ebNz0hxWwoXEpDcXITuRN1q9Q2dlVXwiaJd2YQWUP4"

with open(TOKEN_PATH) as f:
    tok = json.load(f)
creds = Credentials(
    token=tok["token"], refresh_token=tok["refresh_token"],
    token_uri=tok["token_uri"], client_id=tok["client_id"],
    client_secret=tok["client_secret"], scopes=tok["scopes"],
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

gc = gspread.authorize(creds)
ws = gc.open_by_key(SPREADSHEET_ID).worksheet("Crispin")
data = ws.get_all_values()

print("=== ROWS 118-145 ===")
for i in range(117, 145):
    b = data[i][1] if data[i][1] else ''
    print(f"Row {i+1:3d}: {b}")

print("\n=== ROWS 620-640 ===")
for i in range(619, 640):
    b = data[i][1] if data[i][1] else ''
    print(f"Row {i+1:3d}: {b}")
