"""List files in the shared Drive folder and show their IDs/mime types."""
import sys
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
FOLDER_ID = '0B7kFxJCGZsqqTWpManBGb1hvLUE'
RESOURCE_KEY = '0-fWQ9Tl_HMjdlK6vvuPA5Hg'

SCOPES = ['https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
drive = build('drive', 'v3', credentials=creds)

# Resource key header is required for legacy/restricted files
resource_keys = f'{FOLDER_ID}/{RESOURCE_KEY}'

try:
    resp = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed = false",
        fields='files(id, name, mimeType, resourceKey, size)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute(num_retries=2)
    for f in resp.get('files', []):
        print(f)
except Exception as e:
    print('ERROR listing folder:', e, file=sys.stderr)
    # Try fetching the folder itself to see if the service account can see it
    try:
        meta = drive.files().get(
            fileId=FOLDER_ID,
            fields='id, name, mimeType, owners, permissions',
            supportsAllDrives=True,
        ).execute()
        print('FOLDER META:', meta)
    except Exception as e2:
        print('ERROR getting folder meta:', e2, file=sys.stderr)
