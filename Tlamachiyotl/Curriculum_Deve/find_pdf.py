"""Recursively search the Guia Futuro folder tree for PDFs."""
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
ROOT = '0B7kFxJCGZsqqTWpManBGb1hvLUE'

SCOPES = ['https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
drive = build('drive', 'v3', credentials=creds)

def walk(folder_id, prefix=''):
    resp = drive.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields='files(id, name, mimeType, size, resourceKey)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        pageSize=1000,
    ).execute()
    for f in resp.get('files', []):
        kind = f['mimeType']
        if kind == 'application/vnd.google-apps.folder':
            print(f"{prefix}[DIR]  {f['name']}  id={f['id']}")
            walk(f['id'], prefix + '  ')
        else:
            marker = ''
            if 'pdf' in kind.lower() or f['name'].lower().endswith('.pdf'):
                marker = '  <-- PDF'
            if 'document' in kind.lower() or f['name'].lower().endswith(('.doc', '.docx')):
                marker = marker or '  <-- DOC'
            print(f"{prefix}       {f['name']}  mime={kind}  id={f['id']}{marker}")

walk(ROOT)
