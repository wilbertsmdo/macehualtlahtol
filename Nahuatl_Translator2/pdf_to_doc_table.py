import io, json, re
from google.oauth2.service_account import Credentials as SACredentials
from google.oauth2.credentials import Credentials as OAuthCreds
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from pypdf import PdfReader

SA_KEY     = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
TOKEN_PATH = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json'
SA_EMAIL   = 'ws-financial-analysis@qwen-project-492821.iam.gserviceaccount.com'
SOURCE_FILE_ID = '1rE-3Xcgx099HcJvc4lvi_r2dnTlw5A8a'
DOC_ID     = '1i66XN3qKwxM7KliQLqtwKm4EH6sMvVQTPR65MUD5HYI'  # reuse existing doc
PAGE_START = 108   # 1-indexed, inclusive
PAGE_END   = 123   # 1-indexed, inclusive

# ── credentials ────────────────────────────────────────────────────────────────

SA_SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
sa_creds  = SACredentials.from_service_account_file(SA_KEY, scopes=SA_SCOPES)
sa_drive  = build('drive', 'v3', credentials=sa_creds)
sa_docs   = build('docs',  'v1', credentials=sa_creds)

with open(TOKEN_PATH) as f:
    tok = json.load(f)
oauth_creds = OAuthCreds(
    token=tok['token'], refresh_token=tok['refresh_token'],
    token_uri=tok['token_uri'], client_id=tok['client_id'],
    client_secret=tok['client_secret'], scopes=tok['scopes'],
)
if oauth_creds.expired and oauth_creds.refresh_token:
    oauth_creds.refresh(Request())
user_drive = build('drive', 'v3', credentials=oauth_creds)

# ── step 1: download PDF ───────────────────────────────────────────────────────

print('Downloading PDF...')
buf = io.BytesIO()
req = sa_drive.files().get_media(fileId=SOURCE_FILE_ID)
dl  = MediaIoBaseDownload(buf, req)
done = False
while not done:
    status, done = dl.next_chunk()
    if status:
        print(f'  {int(status.progress()*100)}%', end='\r')
buf.seek(0)
print('\nDownload complete.')

# ── step 2: extract + parse paragraphs ────────────────────────────────────────

reader    = PdfReader(buf)
total     = len(reader.pages)
print(f'PDF has {total} pages. Extracting pages {PAGE_START}–{PAGE_END}...')

all_text = ''
for page_idx in range(PAGE_START - 1, PAGE_END):
    if page_idx >= total:
        continue
    page_text = reader.pages[page_idx].extract_text() or ''
    all_text += page_text + '\n \n'

# Remove running headers: lines like "108 Valentín Peralta Ramírez"
all_text = re.sub(r'^\d{1,3} [A-ZÁÉÍÓÚ].+\n', '', all_text, flags=re.MULTILINE)
# Remove standalone page numbers
all_text = re.sub(r'^\d{1,3}\s*\n', '', all_text, flags=re.MULTILINE)
# Normalise paragraph breaks: \n \n and \n\n → double-newline marker
all_text = re.sub(r'\n[ \t]*\n', '\n\n', all_text)
all_text = re.sub(r'\n{3,}', '\n\n', all_text)

# Split into raw paragraph blocks
blocks = all_text.split('\n\n')

# Within each block, join wrapped lines (single \n → space)
paragraphs = []
for block in blocks:
    p = re.sub(r'\n', ' ', block).strip()
    p = re.sub(r' {2,}', ' ', p)
    if len(p) > 10:          # discard noise fragments
        paragraphs.append(p)

print(f'Parsed {len(paragraphs)} paragraphs.')
for i, p in enumerate(paragraphs):
    print(f'  [{i+1:02d}] {p[:80]}...' if len(p)>80 else f'  [{i+1:02d}] {p}')

# ── step 3: clear existing doc and rewrite ────────────────────────────────────

print(f'\nUpdating doc: https://docs.google.com/document/d/{DOC_ID}/edit')

doc       = sa_docs.documents().get(documentId=DOC_ID).execute()
body_els  = doc['body']['content']
end_idx   = body_els[-1]['endIndex'] if body_els else 1

reqs = []
if end_idx > 2:
    reqs.append({'deleteContentRange': {'range': {'startIndex': 1, 'endIndex': end_idx - 1}}})
title_text = 'Experiencias profesionales de lingüistas indomexicanos — pp. 108–123\n'
reqs.append({'insertText': {'location': {'index': 1}, 'text': title_text}})
sa_docs.documents().batchUpdate(documentId=DOC_ID, body={'requests': reqs}).execute()

# Apply HEADING_1 to title
doc = sa_docs.documents().get(documentId=DOC_ID).execute()
for el in doc['body']['content']:
    para = el.get('paragraph')
    if not para:
        continue
    txt = ''.join(r.get('textRun',{}).get('content','') for r in para['elements']).strip()
    if txt.startswith('Experiencias'):
        sa_docs.documents().batchUpdate(documentId=DOC_ID, body={'requests': [
            {'updateParagraphStyle': {
                'range': {'startIndex': el['startIndex'], 'endIndex': el['endIndex']},
                'paragraphStyle': {'namedStyleType': 'HEADING_1'},
                'fields': 'namedStyleType',
            }}
        ]}).execute()
        break

# ── step 4: insert empty table ────────────────────────────────────────────────

n_rows = len(paragraphs) + 1   # header + one row per paragraph
title_end = len(title_text) + 1
print(f'Inserting {n_rows}-row × 2-col table at index {title_end}...')
sa_docs.documents().batchUpdate(documentId=DOC_ID, body={'requests': [
    {'insertTable': {'rows': n_rows, 'columns': 2, 'location': {'index': title_end}}}
]}).execute()

# ── step 5: collect cell start indices ────────────────────────────────────────

doc      = sa_docs.documents().get(documentId=DOC_ID).execute()
body_els = doc['body']['content']

cell_starts = []
for el in body_els:
    table = el.get('table')
    if not table:
        continue
    for r_idx, row in enumerate(table['tableRows']):
        for c_idx, cell in enumerate(row['tableCells']):
            content = cell.get('content', [])
            if content:
                # startIndex of the first paragraph in this cell
                cell_starts.append((r_idx, c_idx, content[0]['startIndex']))

print(f'Found {len(cell_starts)} cells.')

# ── step 6: build insertion list (header + data rows) ─────────────────────────

headers = {(0,0): 'Texto original', (0,1): 'Notas / Traducción'}
insertions = []   # (doc_index, text)

for r_idx, c_idx, para_start in cell_starts:
    if r_idx == 0:
        text = headers.get((0, c_idx), '')
    else:
        p_idx = r_idx - 1
        text  = paragraphs[p_idx] if (c_idx == 0 and p_idx < len(paragraphs)) else ''
    if text:
        # Insert at para_start (the start of the empty paragraph inside the cell)
        # NOT at para_start+1 — that would land after the newline and fail bounds check
        insertions.append((para_start, text))

# Highest index first so earlier positions don't shift later ones
insertions.sort(key=lambda x: x[0], reverse=True)

# ── step 7: write cells in batches ────────────────────────────────────────────

BATCH = 20
print(f'Writing {len(insertions)} insertions in batches of {BATCH}...')
for i in range(0, len(insertions), BATCH):
    chunk = insertions[i:i+BATCH]
    reqs  = [{'insertText': {'location': {'index': idx}, 'text': txt}} for idx, txt in chunk]
    sa_docs.documents().batchUpdate(documentId=DOC_ID, body={'requests': reqs}).execute()
    print(f'  batch {i//BATCH + 1}/{-(-len(insertions)//BATCH)} done')

# ── step 8: bold header row ───────────────────────────────────────────────────

doc = sa_docs.documents().get(documentId=DOC_ID).execute()
bold_reqs = []
for el in doc['body']['content']:
    table = el.get('table')
    if not table:
        continue
    for cell in table['tableRows'][0]['tableCells']:
        for c_el in cell.get('content', []):
            for run in c_el.get('paragraph', {}).get('elements', []):
                s, e = run.get('startIndex',0), run.get('endIndex',0)
                if e > s:
                    bold_reqs.append({'updateTextStyle': {
                        'range': {'startIndex': s, 'endIndex': e},
                        'textStyle': {'bold': True},
                        'fields': 'bold',
                    }})
if bold_reqs:
    sa_docs.documents().batchUpdate(documentId=DOC_ID, body={'requests': bold_reqs}).execute()
    print('Header row bolded.')

print(f'\nDone! https://docs.google.com/document/d/{DOC_ID}/edit')
