#!/usr/bin/env /data/data/com.termux/files/usr/bin/python3
"""
Download MorphyNet (eng + spa) and MorphoLEX-en derivational morphology data.
Extract top productive derivational affixes, cross-reference against our 35-row
morpheme mapping table, and write results to a "Morpheme DB" tab in the sheet.

Sources:
  MorphyNet  — https://github.com/kbatsuren/MorphyNet  (open license)
  MorphoLEX  — https://github.com/hugomailhot/MorphoLex-en  (open license)
"""
import io
import json
import re
import requests
import openpyxl
import gspread
from collections import Counter, defaultdict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SA_PATH  = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
SHEET_ID = '1TYw3gvcSGmCTQEKchEKlNDUm1BOL-i66jfhsNA1og-k'
SCOPES   = ['https://www.googleapis.com/auth/spreadsheets']

creds      = Credentials.from_service_account_file(SA_PATH, scopes=SCOPES)
gc         = gspread.authorize(creds)
sheets_svc = build('sheets', 'v4', credentials=creds)
sh         = gc.open_by_key(SHEET_ID)

# ── Step 1: Discover MorphyNet file paths via GitHub API ─────────────────────
GITHUB_API = 'https://api.github.com/repos/kbatsuren/MorphyNet/contents'
RAW_BASE   = 'https://raw.githubusercontent.com/kbatsuren/MorphyNet/main'

def github_ls(path):
    r = requests.get(f'{GITHUB_API}/{path}', timeout=30)
    r.raise_for_status()
    return {f['name']: f['download_url'] for f in r.json() if f['type'] == 'file'}

print("Discovering MorphyNet file structure …")
try:
    eng_files = github_ls('eng')
    spa_files = github_ls('spa')
    print(f"  eng/: {list(eng_files.keys())}")
    print(f"  spa/: {list(spa_files.keys())}")
except Exception as e:
    print(f"  GitHub API failed ({e}), falling back to known URLs.")
    eng_files = {
        'eng.derivational.v1.tsv': f'{RAW_BASE}/eng/eng.derivational.v1.tsv',
    }
    spa_files = {
        'spa.derivational.v1.tsv': f'{RAW_BASE}/spa/spa.derivational.v1.tsv',
    }

def pick_derivational(files):
    """Return URL of the derivational file."""
    for name, url in files.items():
        if 'deriv' in name.lower():
            return name, url
    return None, None

eng_fname, eng_url = pick_derivational(eng_files)
spa_fname, spa_url = pick_derivational(spa_files)
print(f"  Using ENG: {eng_fname}")
print(f"  Using SPA: {spa_fname}")

# ── Step 2: Download and parse MorphyNet derivational TSVs ───────────────────
def parse_morphynet(url, lang_label):
    """
    MorphyNet derivation columns (v1):
      source_word  target_word  source_pos  target_pos  morpheme  type
    type values: prefix | suffix | circumfix | conversion | …
    Returns Counter of (morpheme, type) pairs.
    """
    print(f"\nDownloading MorphyNet {lang_label} …")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    lines = r.text.splitlines()
    print(f"  {len(lines)} lines")

    counter  = Counter()   # (morpheme, mtype) → count
    examples = defaultdict(list)  # morpheme → [target_word, ...]

    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) < 6:
            continue
        # Try to detect column order; header may or may not be present
        if parts[0].lower() in ('source_word', 'lemma', '#'):
            continue
        # Expected: source_word target_word source_pos target_pos morpheme type
        src, tgt = parts[0], parts[1]
        morpheme  = parts[4]
        mtype     = parts[5].lower() if len(parts) > 5 else 'unknown'
        if morpheme and morpheme != 'None':
            counter[(morpheme, mtype)] += 1
            if len(examples[morpheme]) < 3:
                examples[morpheme].append(f'{src}→{tgt}')

    return counter, examples

eng_morphynet_counter, eng_morphynet_ex = parse_morphynet(eng_url, 'ENG')
spa_morphynet_counter, spa_morphynet_ex = parse_morphynet(spa_url, 'SPA')

# ── Step 3: Download and parse MorphoLEX-en (.xlsx) ─────────────────────────
# The xlsx has dedicated summary sheets: "All prefixes" and "All suffixes"
# Columns: morpheme | family_size | HAL_freq | P | P* | length
# Prefix morphemes are encoded as <word<, suffixes as >word>

MORPHOLEX_URL = ('https://raw.githubusercontent.com/hugomailhot/'
                 'MorphoLex-en/master/MorphoLEX_en.xlsx')

print(f"\nDownloading MorphoLEX-en …")
r = requests.get(MORPHOLEX_URL, timeout=120)
r.raise_for_status()
wb = openpyxl.load_workbook(io.BytesIO(r.content), read_only=True, data_only=True)

def read_morpholex_sheet(wb, shname):
    """Read an 'All prefixes' or 'All suffixes' summary sheet.
    Returns list of (clean_morpheme, family_size, hal_freq).
    """
    ws = wb[shname]
    results = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue  # skip header
        morpheme_raw = str(row[0]) if row[0] else ''
        # Clean: <un< → un,  >ness> → ness
        morpheme = morpheme_raw.strip('<>').strip()
        try:
            fam_size = int(row[1]) if row[1] else 0
            hal_freq = int(float(row[2])) if row[2] else 0
        except (ValueError, TypeError):
            fam_size, hal_freq = 0, 0
        if morpheme and fam_size > 0:
            results.append((morpheme, fam_size, hal_freq))
    # Sort by family_size descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results

prefix_data = read_morpholex_sheet(wb, 'All prefixes')
suffix_data  = read_morpholex_sheet(wb, 'All suffixes')
wb.close()

print(f"  MorphoLEX prefixes: {len(prefix_data)} | top 5: {[m for m,_,_ in prefix_data[:5]]}")
print(f"  MorphoLEX suffixes: {len(suffix_data)} | top 5: {[m for m,_,_ in suffix_data[:5]]}")

# ── Step 4: Build combined morpheme table ────────────────────────────────────
# Morphemes already covered in our 35-row table (for cross-reference)
COVERED = {
    # suffixes
    '-ni','-oni','-lli','-li','-yan','-loyan','-liztli','-yotl','-otl',
    '-tzintli','-tontli','-yoh','-tik','-tia','-ltia','-lo-',
    # prefixes
    'a-','mo-','tla-','huey-',
    # free morphemes / classifiers
    'cenca','achi','miac','miec','oc ce','oc ceppa',
    'ce-','ome-','yei-','nahui-','macuil-',
    # structural
    'achtopa','zatepan','icpac','itlan','ixpan',
    'nohuian','yaotl-','tepoz-',
    # English/Spanish covered
    '-tion','-ness','-ment','-er','-or','-oni (able/ible)',
    '-ize','-ify','-ful','-less','-ship','-hood','-dom',
    '-ism','-ist','-ary','-ory','-al','-ic','-ous',
    'un-','re-','pre-','dis-','non-','over-','under-',
    'anti-','inter-','co-','sub-','super-','trans-',
    'auto-','mono-','bi-','tri-','multi-','poly-',
    'pro- (professional)','ex-',
}

# Flag if a morpheme is NOT covered
def coverage(m):
    m_clean = m.strip('-').lower()
    for c in COVERED:
        if m_clean in c.lower() or c.lower().strip('-') == m_clean:
            return 'Yes'
    return '— MISSING'

# ── Step 5: Assemble sheet rows ───────────────────────────────────────────────
rows = []
rows.append(['SOURCE', 'LANGUAGE', 'TYPE', 'MORPHEME', 'COUNT / FREQ',
             'EXAMPLE WORDS', 'IN OUR TABLE?'])

# MorphyNet ENG top morphemes
rows.append(['', '', '', '── MorphyNet (Batsuren et al. 2021) — English ──', '', '', ''])
for (morpheme, mtype), count in eng_morphynet_counter.most_common(60):
    if mtype in ('prefix', 'suffix') and count >= 5:
        ex = ' | '.join(eng_morphynet_ex[morpheme][:3])
        label = f'{morpheme} ({mtype})'
        rows.append(['MorphyNet', 'English', mtype.capitalize(),
                     morpheme, str(count), ex, coverage(morpheme)])

# MorphyNet SPA top morphemes
rows.append(['', '', '', '── MorphyNet (Batsuren et al. 2021) — Spanish ──', '', '', ''])
for (morpheme, mtype), count in spa_morphynet_counter.most_common(60):
    if mtype in ('prefix', 'suffix') and count >= 5:
        ex = ' | '.join(spa_morphynet_ex[morpheme][:3])
        rows.append(['MorphyNet', 'Spanish', mtype.capitalize(),
                     morpheme, str(count), ex, coverage(morpheme)])

# MorphoLEX top prefixes (by family size = number of words using that prefix)
rows.append(['', '', '', '── MorphoLEX-en (Sánchez-Gutiérrez et al. 2018) — English Prefixes ──',
             '', '', ''])
for morpheme, fam_size, hal_freq in prefix_data[:40]:
    rows.append(['MorphoLEX', 'English', 'Prefix',
                 f'{morpheme}-', f'{fam_size} words / HAL {hal_freq:,}',
                 '', coverage(morpheme)])

# MorphoLEX top suffixes
rows.append(['', '', '', '── MorphoLEX-en (Sánchez-Gutiérrez et al. 2018) — English Suffixes ──',
             '', '', ''])
for morpheme, fam_size, hal_freq in suffix_data[:40]:
    rows.append(['MorphoLEX', 'English', 'Suffix',
                 f'-{morpheme}', f'{fam_size} words / HAL {hal_freq:,}',
                 '', coverage(morpheme)])

print(f"\nTotal rows to write: {len(rows)}")

# ── Step 6: Create / clear Morpheme DB tab ────────────────────────────────────
try:
    ws_db = sh.worksheet('Morpheme DB')
    ws_db.clear()
    print("Cleared existing Morpheme DB tab.")
except gspread.exceptions.WorksheetNotFound:
    ws_db = sh.add_worksheet(title='Morpheme DB', rows=len(rows)+5, cols=7)
    print("Created Morpheme DB tab.")

sid_db = ws_db.id
ws_db.update(values=rows, range_name='A1', value_input_option='RAW')
print("Data written.")

# ── Step 7: Formatting ────────────────────────────────────────────────────────
fmt_requests = []

# Freeze row 1
fmt_requests.append({'updateSheetProperties': {
    'properties': {'sheetId': sid_db, 'gridProperties': {'frozenRowCount': 1}},
    'fields': 'gridProperties.frozenRowCount',
}})

# Header
fmt_requests.append({'repeatCell': {
    'range': {'sheetId': sid_db, 'startRowIndex': 0, 'endRowIndex': 1},
    'cell': {'userEnteredFormat': {
        'textFormat': {'bold': True, 'fontSize': 10,
                       'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
        'backgroundColor': {'red': 0.12, 'green': 0.26, 'blue': 0.49},
        'horizontalAlignment': 'CENTER',
    }},
    'fields': 'userEnteredFormat(textFormat,backgroundColor,horizontalAlignment)',
}})

# All data: wrap, top, small font
fmt_requests.append({'repeatCell': {
    'range': {'sheetId': sid_db, 'startRowIndex': 1},
    'cell': {'userEnteredFormat': {
        'wrapStrategy': 'WRAP', 'verticalAlignment': 'TOP',
        'textFormat': {'fontSize': 9},
    }},
    'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment,textFormat)',
}})

# "MISSING" rows: highlight red tint in col G
for i, row in enumerate(rows[1:], start=2):
    if len(row) >= 7 and '— MISSING' in str(row[6]):
        fmt_requests.append({'repeatCell': {
            'range': {'sheetId': sid_db, 'startRowIndex': i-1, 'endRowIndex': i,
                      'startColumnIndex': 6, 'endColumnIndex': 7},
            'cell': {'userEnteredFormat': {
                'backgroundColor': {'red': 0.99, 'green': 0.80, 'blue': 0.80},
                'textFormat': {'bold': True, 'foregroundColor':
                               {'red': 0.72, 'green': 0.07, 'blue': 0.07}},
            }},
            'fields': 'userEnteredFormat(backgroundColor,textFormat)',
        }})

# Section header rows (source col empty, morpheme col has ──)
for i, row in enumerate(rows[1:], start=2):
    if len(row) >= 4 and '──' in str(row[3]):
        fmt_requests.append({'repeatCell': {
            'range': {'sheetId': sid_db, 'startRowIndex': i-1, 'endRowIndex': i},
            'cell': {'userEnteredFormat': {
                'backgroundColor': {'red': 0.22, 'green': 0.38, 'blue': 0.60},
                'textFormat': {'bold': True, 'italic': True, 'fontSize': 9,
                               'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
            }},
            'fields': 'userEnteredFormat(backgroundColor,textFormat)',
        }})

# Column widths
for col, px in {0:100, 1:80, 2:70, 3:130, 4:80, 5:280, 6:110}.items():
    fmt_requests.append({'updateDimensionProperties': {
        'range': {'sheetId': sid_db, 'dimension': 'COLUMNS',
                  'startIndex': col, 'endIndex': col+1},
        'properties': {'pixelSize': px},
        'fields': 'pixelSize',
    }})

sheets_svc.spreadsheets().batchUpdate(
    spreadsheetId=SHEET_ID, body={'requests': fmt_requests}
).execute()
print("Formatting applied.")
print(f"\nDone. Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
