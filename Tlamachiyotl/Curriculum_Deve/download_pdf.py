"""Download ensayo.pdf from Drive."""
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
FILE_ID = '1WSOHnDleRF6kUwldWQ4nFmWF36X9y4YK'
OUT = '/storage/self/primary/PY_Projects/Piltzin_Tlamantli/Personal/Tlamachiyotl/Curriculum_Deve/ensayo.pdf'

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=['https://www.googleapis.com/auth/drive'])
drive = build('drive', 'v3', credentials=creds)

req = drive.files().get_media(fileId=FILE_ID, supportsAllDrives=True)
buf = io.BytesIO()
dl = MediaIoBaseDownload(buf, req)
done = False
while not done:
    status, done = dl.next_chunk()
    if status:
        print(f'  {int(status.progress()*100)}%')

with open(OUT, 'wb') as f:
    f.write(buf.getvalue())
print('Saved:', OUT, 'size:', len(buf.getvalue()))
