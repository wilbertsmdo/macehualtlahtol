from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

DOC_ID = "1VVrd_fxaE_O5N_6p8OSiqTaOcYfApDSmn8zDcKQREiY"
SA_KEY = "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file(SA_KEY, scopes=SCOPES)
drive = build("drive", "v3", credentials=creds)

# Page through ALL revisions
all_revs = []
token = None
while True:
    kwargs = dict(fileId=DOC_ID, fields="nextPageToken,revisions(id,modifiedTime)")
    if token:
        kwargs["pageToken"] = token
    resp = drive.revisions().list(**kwargs).execute()
    all_revs.extend(resp.get("revisions", []))
    token = resp.get("nextPageToken")
    if not token:
        break

print(f"Total revisions found: {len(all_revs)}")
for r in all_revs:
    print(f"  id={r['id']:5}  modifiedTime={r['modifiedTime']}")
