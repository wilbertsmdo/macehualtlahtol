#!/usr/bin/env python3
"""
transcribe_all_docs.py — PDF-to-Sheet transcription pipeline for NAH model training.

For each untranscribed source PDF in the Drive folder:
  1. Download PDF via service account
  2. Extract + segment Nahuatl text (prose / vocab / poetry modes)
  3. Create Google Sheet in standard 11-column format
  4. Write Nahuatl text → col B, section headings → col A
  5. Load fine-tuned NLLB once, translate all sentences → col J
  6. Checkpoint after each doc (resume on crash)

Laptop run (WSL2, tmux):
  source ~/nllb-env/bin/activate
  cd <Nahuatl_Translator2>
  git pull origin main
  tmux new -s transcribe
  python3 transcribe_all_docs.py 2>&1 | tee transcribe.log

Optional flags:
  --doc LABEL_SUBSTR   process only docs whose label contains this substring
  --skip-nllb          create sheets but skip NLLB translation
  --dry-run            extract + print row counts; no sheets created

service_account.json: ~/service_account.json  (or SA_KEY_PATH env var)
Model: models/nllb-nah-es-final/ (relative to this script)
"""

import argparse
import io
import json
import os
import re
import sys
import time

# pypdf: on tablet PRoot, pypdf lives in /usr/lib/python3/dist-packages
sys.path.insert(0, '/usr/lib/python3/dist-packages')
try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        PdfReader = None

from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import gspread

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
TMPDIR = os.path.join(_HERE, 'tmp_pdfs')
PROGRESS_PATH = os.path.join(_HERE, 'transcribe_progress.json')
TARGET_FOLDER_ID = '1LW0qwgf58wUX1UhpL7K2Y_6gW5x_NAoF'
USER_EMAIL = 'ws@tcp-partners.com'
SA_EMAIL = 'ws-financial-analysis@qwen-project-492821.iam.gserviceaccount.com'
MODEL_PATH = os.path.join(_HERE, 'models', 'nllb-nah-es-final')
SRC_LANG = 'nah_Latn'
TGT_LANG = 'spa_Latn'
NLLB_BATCH = 16

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]
# Sheets-only scope — sufficient for gspread.create() via Sheets API (no Drive quota)
SHEETS_SCOPE = ['https://www.googleapis.com/auth/spreadsheets']

ROW3_HEADERS = [
    '', 'Nahuatlahtolli', 'Coyotlahtolli',
    'Tlahtlaniliztli Zo Yancuic Tlahtolli',
    'Claude Tlahtoltlanextilli', 'BLEU', 'Tlatocopa',
    'Tlahtol (Auto)', 'Tlahtol (Human)',
    'NLLB Tlahtoltlanextilli', 'NLLB BLEU',
]

STOP_MARKERS = {
    'amoxtecpantli', 'bibliografía', 'referencias',
    'bibliography', 'works cited', 'references',
}

# Simple Nahuatl presence heuristic
NAH_SEQS = ['tl', 'tz', 'huan', 'meh', 'yah', 'qui', 'huah', 'tlan']
ENG_COMMON = {'the', 'and', 'of', 'to', 'in', 'is', 'are', 'was', 'they',
              'we', 'for', 'on', 'at', 'by', 'from', 'with', 'that', 'this'}
POL_COMMON = {'nie', 'się', 'że', 'jak', 'do', 'na', 'to', 'jest', 'jako',
              'przez', 'tłumaczenie', 'języka', 'języku'}

# ---------------------------------------------------------------------------
# Source documents — 10 untranscribed PDFs
# skip_pages: 0-indexed pages to skip (front matter)
# mode: prose | vocab | poetry
# ---------------------------------------------------------------------------
DOCS = [
    dict(
        file_id='11U7Rz6lz8s5yJn1OxVkRQ68p_9BCV7b8',
        label='De la Cruz 2015 Tototatahhuan Ininixtlamatiliz',
        sheet_name='Tototatahhuan - De la Cruz 2015',
        source_tag='Tototatahhuan',
        mode='prose',
        skip_pages=10,   # skip cover, copyright, foreword, ToC; stories start ~p.17
    ),
    dict(
        file_id='1GezP71T5y2A3Cn1i9-P6p_GBlwIIaL4r',
        label='Bueno Nava 2015 Nahui Tonatiuh',
        sheet_name='Nahui Tonatiuh - Bueno Nava 2015',
        source_tag='NahuiTonatiuh',
        mode='prose',
        skip_pages=4,
    ),
    dict(
        file_id='1AwlEPx3XKihwyW9K2QeHGQH28L9d9s8n',
        label='Burkhart 2017 Citlalmachiyotl',
        sheet_name='Citlalmachiyotl - Burkhart 2017',
        source_tag='Citlalmachiyotl',
        mode='prose',
        skip_pages=7,
    ),
    dict(
        file_id='1yb1R7-GCDJTzyD4UAGoo2zZaYkI41ubg',
        label='Nava 2013 Malintzin Itlahtol',
        sheet_name='Malintzin - Nava 2013',
        source_tag='Malintzin',
        mode='prose',
        skip_pages=8,
    ),
    dict(
        file_id='1vXIQcYCzXs_O4zvjXNAqrLoiBxbz0kLM',
        label='Nava Cuahutle 2015 Tlahtolcozcatl',
        sheet_name='Tlahtolcozcatl - Nava Cuahutle 2015',
        source_tag='Tlahtolcozcatl',
        mode='prose',
        skip_pages=11,   # ToC at p.10, first story at p.13
    ),
    dict(
        file_id='1xPHUd7nV6ISfWg0wVWAb4kwItlZ6dePs',
        label='De la Cruz 2016 Tlahtolixcopincayotl Chicontepec',
        sheet_name='Tlahtolixcopincayotl Chicontepec 2016',
        source_tag='Chicontepec2016',
        mode='prose',
        skip_pages=5,
    ),
    dict(
        file_id='1-j9K85h8uC8Gw1kHbCn0lWI1dfbMwIvg',
        label='Iglesias Maryniak 2020 Tlahtolixcopincayotl Atliaca',
        sheet_name='Tlahtolixcopincayotl Atliaca 2020',
        source_tag='Atliaca2020',
        mode='prose',
        skip_pages=8,    # captures history prose (Olmec/Teotihuacan/Mexica) + vocab items
    ),
    dict(
        file_id='1u74R_e83Npqq46BuzNomeUTGbc9DAn6a',
        label='Xochitiotzin 2020 Tlaoxticah in tlahtolli',
        sheet_name='Tlaoxticah - Xochitiotzin 2020',
        source_tag='Tlaoxticah',
        mode='poetry',
        skip_pages=9,
    ),
    dict(
        file_id='16lpKYeb-H-Sk1xRQjlr8CJHb1IDRsVS5',
        label='Zapoteco 2019 Tlitzonpitentzin',
        sheet_name='Tlitzonpitentzin - Zapoteco 2019',
        source_tag='Tlitzonpitentzin',
        mode='poetry',
        skip_pages=22,   # skip English + Polish forewords
        # NOTE: book has facing-page English translations — future enhancement
        # to pair them: detect language per page and zip Nahuatl/English runs
    ),
    dict(
        file_id='1P6-Ll8kvU8hb-_ixPCMCJ4XWHP-6ztjo',
        label='Zapoteco 2014 Chalchihuicozcatl',
        sheet_name='Chalchihuicozcatl - Zapoteco 2014',
        source_tag='Chalchihuicozcatl',
        mode='poetry',
        skip_pages=12,
    ),
]


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
def _sa_path():
    env = os.environ.get('SA_KEY_PATH')
    if env and os.path.isfile(env):
        return env
    candidates = [
        os.path.expanduser('~/service_account.json'),
        os.path.join(_HERE, 'service_account.json'),
        '/home/wslinux/WS_Qwen_Projects_Windows/Financial_Analysis_App/python/service_account.json',
        '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json',
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    raise FileNotFoundError(
        'service_account.json not found.\n'
        'Copy it to ~/service_account.json or set SA_KEY_PATH=/path/to/key.json'
    )


def _user_oauth_creds():
    """Load user OAuth from token.json using the same pattern as transcribe_pdf_to_sheet.py."""
    token_candidates = [
        os.path.expanduser('~/token.json'),
        '/home/wslinux/WS_Qwen_Projects_Windows/Financial_Analysis_App/python/token.json',
        '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json',
        os.path.join(_HERE, 'token.json'),
    ]
    token_path = next((p for p in token_candidates if os.path.isfile(p)), None)
    if not token_path:
        return None, None

    with open(token_path) as f:
        tok = json.load(f)

    creds = OAuthCredentials(
        token=tok.get('token'),
        refresh_token=tok.get('refresh_token'),
        token_uri=tok.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=tok.get('client_id'),
        client_secret=tok.get('client_secret'),
        scopes=tok.get('scopes'),
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        tok['token'] = creds.token
        tok['expiry'] = creds.expiry.isoformat() if creds.expiry else tok.get('expiry')
        with open(token_path, 'w') as f:
            json.dump(tok, f, indent=2)
        print('[auth] OAuth token refreshed')

    print(f'[auth] User OAuth loaded: {token_path}')
    return creds, token_path


def connect():
    sa_path = _sa_path()
    sa_creds = Credentials.from_service_account_file(sa_path, scopes=SCOPES)

    # User OAuth for gspread + Drive (same pattern as transcribe_pdf_to_sheet.py on tablet)
    user_creds, token_path = _user_oauth_creds()
    if user_creds:
        gc = gspread.authorize(user_creds)
        user_drive_svc = build('drive', 'v3', credentials=user_creds)
        print('[auth] gspread + Drive: user OAuth — sheets owned by user, no SA quota hit')
    else:
        gc = gspread.authorize(sa_creds)
        user_drive_svc = build('drive', 'v3', credentials=sa_creds)
        print('[auth] WARNING: token.json not found — falling back to SA (quota may hit)')

    # SA drive service kept for PDF downloads
    sa_drive_svc = build('drive', 'v3', credentials=sa_creds)
    print(f'[auth] SA: {sa_path}')
    return gc, user_drive_svc, sa_drive_svc


# ---------------------------------------------------------------------------
# PDF download
# ---------------------------------------------------------------------------
def download_pdf(drive_svc, file_id, dest_path):
    req = drive_svc.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, req, chunksize=4 * 1024 * 1024)
    done = False
    while not done:
        status, done = dl.next_chunk()
        if status:
            print(f'    {int(status.progress() * 100)}%', end='\r')
    with open(dest_path, 'wb') as f:
        f.write(buf.getvalue())
    print(f'    Downloaded: {os.path.getsize(dest_path) // 1024} KB')


# ---------------------------------------------------------------------------
# Language detection (for poetry docs with mixed-language pages)
# ---------------------------------------------------------------------------
def is_nahuatl_page(text):
    if not text or len(text.split()) < 4:
        return True   # too short to classify — include by default
    words = {w.strip('.,;:!?()[]"\'').lower() for w in text.split()}
    eng_hits = len(words & ENG_COMMON)
    pol_hits = len(words & POL_COMMON)
    if eng_hits >= 4 or pol_hits >= 3:
        return False
    nah_hits = sum(1 for seq in NAH_SEQS if seq in text.lower())
    return nah_hits >= 1


# ---------------------------------------------------------------------------
# Stop-page detection
# ---------------------------------------------------------------------------
def is_stop_page(text):
    first_line = text.strip().split('\n')[0].strip().lower()
    return (first_line in STOP_MARKERS or
            any(m in first_line for m in STOP_MARKERS))


# ---------------------------------------------------------------------------
# Nahuatl page-number line detection (Atliaca uses Nahuatl numerals)
# ---------------------------------------------------------------------------
_NAH_NUM = re.compile(
    r'^(\d+\s+)?(ce|ome|yei|nahui|macuilli|chicuace|chicome|chicueyi|chiucnahui|'
    r'mahtlactli|caxtolli|pohualli|ompohualli|yeipohualli|nauhpohualli)\b',
    re.IGNORECASE,
)

def is_page_num_line(line):
    s = line.strip()
    return bool(re.match(r'^\d+\s*$', s)) or bool(_NAH_NUM.match(s))


# ---------------------------------------------------------------------------
# Row extraction — prose mode
# Splits prose text into (heading, sentence) rows.
# ---------------------------------------------------------------------------
def extract_rows_prose(reader, skip_pages):
    rows = []
    current_section = ''

    for page_idx, page in enumerate(reader.pages):
        if page_idx < skip_pages:
            continue
        text = page.extract_text() or ''
        if is_stop_page(text):
            break

        # Replace isolated newlines (mid-sentence line breaks) with spaces,
        # but preserve paragraph breaks (two or more consecutive newlines).
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        paragraphs = re.split(r'\n{2,}', text)

        for para in paragraphs:
            para = ' '.join(para.split())   # normalise whitespace
            if not para or len(para) < 5:
                continue

            words = para.split()
            n_words = len(words)

            # Heading: short, no terminal punctuation, not a bare number
            is_heading = (
                n_words <= 7
                and not para.rstrip().endswith(('.', '?', '!', ','))
                and len(para) < 70
                and not re.match(r'^[\d\s]+$', para)
            )
            if is_heading:
                current_section = para
                continue

            # Split paragraph into sentences on ". " / "? " / "! "
            raw_sentences = re.split(r'(?<=[.?!])\s+', para)
            for sent in raw_sentences:
                sent = sent.strip()
                # Strip leading page numbers merged by pypdf (e.g. "13 In Zohuacoatl...")
                sent = re.sub(r'^\d{1,3}\s+', '', sent).strip()
                if len(sent) < 15:
                    continue
                # Require at least one Nahuatl sequence to filter out pure Spanish/English
                if not any(seq in sent.lower() for seq in NAH_SEQS):
                    continue
                # Clamp runaway sentences (PDF occasionally joins two paragraphs)
                if len(sent) > 500:
                    # split on '. ' one more time
                    for sub in sent.split('. '):
                        sub = sub.strip()
                        if len(sub) >= 15:
                            rows.append({'type': 'data', 'text': sub,
                                         'section': current_section})
                            current_section = ''
                    continue
                rows.append({'type': 'data', 'text': sent,
                             'section': current_section})
                current_section = ''

    # Convert section markers into proper heading rows interspersed with data
    return _interleave_headings(rows)


def _interleave_headings(rows):
    """Convert 'section' field into explicit heading rows before the first
    data row of each new section."""
    out = []
    last_section = None
    for r in rows:
        sec = r.get('section', '')
        if sec and sec != last_section:
            out.append({'type': 'heading', 'text': sec})
            last_section = sec
        out.append({'type': 'data', 'text': r['text']})
    return out


# ---------------------------------------------------------------------------
# Row extraction — vocab mode (Atliaca picture dictionary)
# Each page: optional page-number line, then category heading, then word list.
# ---------------------------------------------------------------------------
def extract_rows_vocab(reader, skip_pages):
    rows = []

    for page_idx, page in enumerate(reader.pages):
        if page_idx < skip_pages:
            continue
        text = page.extract_text() or ''
        if is_stop_page(text):
            break
        if not is_nahuatl_page(text):
            continue

        lines = [l.strip() for l in text.split('\n') if l.strip()]
        # Strip page-number lines
        lines = [l for l in lines if not is_page_num_line(l)]
        if not lines:
            continue

        # First remaining line = category heading
        category = lines[0]
        if len(category) > 60:
            # Probably grabbed prose, not a vocab page — treat as prose snippet
            rows.append({'type': 'data', 'text': category})
            for word in lines[1:]:
                if 3 < len(word) < 80:
                    rows.append({'type': 'data', 'text': word})
            continue

        rows.append({'type': 'heading', 'text': category})
        for word in lines[1:]:
            word = word.strip()
            if 2 < len(word) < 80 and not is_page_num_line(word):
                rows.append({'type': 'data', 'text': word})

    return rows


# ---------------------------------------------------------------------------
# Row extraction — poetry mode
# Groups lines into stanzas; stanza separator = blank line in the PDF.
# ---------------------------------------------------------------------------
def extract_rows_poetry(reader, skip_pages):
    rows = []

    for page_idx, page in enumerate(reader.pages):
        if page_idx < skip_pages:
            continue
        text = page.extract_text() or ''
        if is_stop_page(text):
            break
        if not is_nahuatl_page(text):
            continue   # skip English/Polish foreword and translation pages

        # Split into stanzas on blank lines
        raw_lines = text.split('\n')
        stanzas = []
        buf = []
        for line in raw_lines:
            stripped = line.strip()
            if stripped:
                buf.append(stripped)
            elif buf:
                stanzas.append(buf)
                buf = []
        if buf:
            stanzas.append(buf)

        if not stanzas:
            continue

        # First stanza is a heading if it's very short (poem title or number)
        if len(stanzas[0]) <= 2 and len(' '.join(stanzas[0])) < 50:
            rows.append({'type': 'heading', 'text': ' '.join(stanzas[0])})
            stanzas = stanzas[1:]

        for stanza in stanzas:
            # Join stanza lines with ' / ' so each stanza is one sheet row
            text_joined = ' / '.join(stanza)
            if len(text_joined) >= 8:
                rows.append({'type': 'data', 'text': text_joined})

    return rows


# ---------------------------------------------------------------------------
# Sheet creation
# ---------------------------------------------------------------------------
def create_sheet(gc, user_drive_svc, sheet_name, source_tag, label):
    """Create a new Google Sheet via Sheets API then move to TARGET_FOLDER_ID."""
    sh = gc.create(sheet_name)
    sheet_id = sh.id
    time.sleep(1.0)

    # Move into target folder (Drive API with user OAuth — no quota issue, just a metadata update)
    try:
        user_drive_svc.files().update(
            fileId=sheet_id,
            addParents=TARGET_FOLDER_ID,
            removeParents='root',
            fields='id, parents',
        ).execute()
    except Exception as e:
        print(f'  [warn] Could not move to folder: {e} — sheet stays in Drive root')

    # Rename default worksheet
    ws = sh.get_worksheet(0)
    ws.update_title(source_tag)

    # Write 3-row header
    ws.update([['Nahuatl Tequitl']], 'A1')
    ws.update([[label]], 'A2')
    ws.update([ROW3_HEADERS], 'A3:K3')
    ws.format('A3:K3', {'textFormat': {'bold': True}})
    ws.freeze(rows=3)
    time.sleep(0.5)

    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit'
    print(f'  Sheet created: {url}')
    return sheet_id, ws


# ---------------------------------------------------------------------------
# Write rows (cols A-B only; NLLB fills col J separately)
# Returns list of sheet row numbers that have data (for NLLB batch).
# ---------------------------------------------------------------------------
def write_rows_to_sheet(ws, rows, start_row=4):
    if not rows:
        return []

    data_row_numbers = []
    sheet_data = []
    blank11 = [''] * 11

    current_sheet_row = start_row
    for row in rows:
        if row['type'] == 'heading':
            r = blank11[:]
            r[0] = row['text']
            sheet_data.append(r)
        else:
            r = blank11[:]
            r[1] = row['text']   # col B
            sheet_data.append(r)
            data_row_numbers.append(current_sheet_row)
        current_sheet_row += 1

    chunk = 500
    for i in range(0, len(sheet_data), chunk):
        ws.update(sheet_data[i:i + chunk], f'A{start_row + i}')
        print(f'    rows {start_row + i}–{start_row + i + len(sheet_data[i:i+chunk]) - 1}')
        time.sleep(1.2)

    return data_row_numbers


# ---------------------------------------------------------------------------
# NLLB model
# ---------------------------------------------------------------------------
def load_nllb():
    if not os.path.isdir(MODEL_PATH):
        print(f'[NLLB] Model not found at {MODEL_PATH}')
        print('  Sheets will be created without col J translations.')
        return None, None, None, None

    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    except ImportError:
        print('[NLLB] torch/transformers not available — skipping translation')
        return None, None, None, None

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'[NLLB] Loading model... device={device}')
    if device == 'cuda':
        print(f'  GPU: {torch.cuda.get_device_name(0)}')

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
    ).to(device)
    model.eval()
    tgt_lang_id = tokenizer.convert_tokens_to_ids(TGT_LANG)
    n_params = sum(p.numel() for p in model.parameters()) / 1e6
    print(f'[NLLB] Ready ({n_params:.0f}M params)')
    return tokenizer, model, device, tgt_lang_id


def translate_texts(tokenizer, model, device, tgt_lang_id, texts):
    import torch
    tokenizer.src_lang = SRC_LANG
    translations = []
    n = len(texts)

    for i in range(0, n, NLLB_BATCH):
        batch = texts[i:i + NLLB_BATCH]
        inputs = tokenizer(
            batch, return_tensors='pt', padding=True,
            truncation=True, max_length=256,
        ).to(device)
        with torch.no_grad():
            generated = model.generate(
                **inputs,
                forced_bos_token_id=tgt_lang_id,
                max_length=256,
            )
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        translations.extend(decoded)

        done = min(i + NLLB_BATCH, n)
        if (i // NLLB_BATCH) % 20 == 0 or done == n:
            print(f'    {done}/{n} ({done/n*100:.0f}%)')

    return translations


def write_nllb_col(ws, data_row_numbers, translations):
    updates = [
        {'range': f'J{row}', 'values': [[trans]]}
        for row, trans in zip(data_row_numbers, translations)
    ]
    for i in range(0, len(updates), 500):
        ws.batch_update(updates[i:i + 500])
        time.sleep(1.2)
    print(f'  col J: {len(updates)} NLLB translations written')


# ---------------------------------------------------------------------------
# Progress checkpoint
# ---------------------------------------------------------------------------
def load_progress():
    if os.path.isfile(PROGRESS_PATH):
        with open(PROGRESS_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_progress(progress):
    with open(PROGRESS_PATH, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='PDF → Google Sheet transcription')
    parser.add_argument('--doc', metavar='SUBSTR',
                        help='process only docs whose label contains this substring')
    parser.add_argument('--skip-nllb', action='store_true',
                        help='create sheets but skip NLLB translation')
    parser.add_argument('--dry-run', action='store_true',
                        help='extract rows and print stats; no sheets created')
    args = parser.parse_args()

    if PdfReader is None:
        sys.exit('ERROR: pypdf not found. Run: pip install pypdf')

    os.makedirs(TMPDIR, exist_ok=True)
    progress = load_progress()

    if progress:
        print(f'[progress] {len(progress)} docs already done:')
        for fid, info in progress.items():
            print(f'  {info["label"]} — {info["data_rows"]} rows — {info["sheet_id"]}')

    # Filter docs
    docs = DOCS
    if args.doc:
        docs = [d for d in DOCS if args.doc.lower() in d['label'].lower()]
        if not docs:
            sys.exit(f'No docs matched --doc "{args.doc}"')
        print(f'[filter] {len(docs)} doc(s) match "{args.doc}"')

    # Connect (skip if dry-run)
    if not args.dry_run:
        gc, user_drive_svc, sa_drive_svc = connect()
    else:
        gc = user_drive_svc = sa_drive_svc = None

    # Load NLLB (skip if --skip-nllb or --dry-run)
    if not args.skip_nllb and not args.dry_run:
        tokenizer, model, device, tgt_lang_id = load_nllb()
    else:
        tokenizer = model = device = tgt_lang_id = None

    # Process each doc
    for doc in docs:
        fid = doc['file_id']
        label = doc['label']

        if fid in progress and not args.dry_run:
            print(f'\n[skip] {label} (done)')
            continue

        print(f'\n{"="*65}')
        print(f'[doc] {label}')
        print(f'{"="*65}')

        try:
            # Download PDF
            pdf_path = os.path.join(TMPDIR, f'{fid}.pdf')
            if not os.path.isfile(pdf_path):
                if args.dry_run:
                    print('  [dry-run] PDF not cached — skipping')
                    continue
                print('  Downloading...')
                download_pdf(sa_drive_svc, fid, pdf_path)
            else:
                print(f'  PDF cached: {os.path.getsize(pdf_path)//1024} KB')

            # Extract rows
            reader = PdfReader(pdf_path)
            n_pages = len(reader.pages)
            skip = doc['skip_pages']
            mode = doc.get('mode', 'prose')
            print(f'  {n_pages} pages, skip={skip}, mode={mode}')

            if mode == 'prose':
                rows = extract_rows_prose(reader, skip)
            elif mode == 'vocab':
                rows = extract_rows_vocab(reader, skip)
            else:   # poetry / poetry_parallel
                rows = extract_rows_poetry(reader, skip)

            heading_rows = [r for r in rows if r['type'] == 'heading']
            data_rows = [r for r in rows if r['type'] == 'data']
            print(f'  Extracted: {len(data_rows)} sentences, {len(heading_rows)} headings')

            if args.dry_run:
                print(f'  Sample (first 5 data rows):')
                for r in data_rows[:5]:
                    print(f'    {r["text"][:90]}')
                continue

            if not data_rows:
                print('  WARNING: 0 data rows — check skip_pages or mode setting')
                continue

            # Create sheet
            sheet_id, ws = create_sheet(
                gc, user_drive_svc,
                doc['sheet_name'], doc['source_tag'], label,
            )
            time.sleep(1.0)

            # Write rows to sheet
            print(f'  Writing {len(rows)} rows...')
            data_row_numbers = write_rows_to_sheet(ws, rows, start_row=4)

            # NLLB translate
            if tokenizer is not None and data_row_numbers:
                nahuatl_texts = [r['text'] for r in data_rows]
                print(f'  Translating {len(nahuatl_texts)} sentences (NLLB)...')
                translations = translate_texts(
                    tokenizer, model, device, tgt_lang_id, nahuatl_texts,
                )
                write_nllb_col(ws, data_row_numbers, translations)

                # Free GPU memory between docs
                try:
                    import torch
                    if device == 'cuda':
                        torch.cuda.empty_cache()
                except Exception:
                    pass

            # Save checkpoint
            progress[fid] = {
                'label': label,
                'sheet_id': sheet_id,
                'sheet_name': doc['sheet_name'],
                'data_rows': len(data_rows),
            }
            save_progress(progress)
            url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit'
            print(f'  Done. {url}')

        except KeyboardInterrupt:
            print('\n[interrupted] Progress saved.')
            break
        except Exception as exc:
            import traceback
            print(f'  ERROR: {exc}')
            traceback.print_exc()
            print('  Continuing to next doc...')

    # Summary
    print(f'\n{"="*65}')
    print('Summary:')
    for fid, info in progress.items():
        url = f'https://docs.google.com/spreadsheets/d/{info["sheet_id"]}/edit'
        print(f'  {info["label"]}')
        print(f'    {info["data_rows"]} rows — {url}')


if __name__ == '__main__':
    main()
