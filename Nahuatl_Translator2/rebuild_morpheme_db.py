#!/usr/bin/env /data/data/com.termux/files/usr/bin/python3
"""
Rebuild Morpheme DB into two consolidated tabs:
  "Morpheme DB - ENG"  —  English: MorphyNet ENG + MorphoLEX merged, one column per source
  "Morpheme DB - ESP"  —  Spanish: MorphyNet SPA
Deletes old "Morpheme DB" tab.
"""
import io
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

RAW_BASE = 'https://raw.githubusercontent.com/kbatsuren/MorphyNet/main'
MORPHOLEX_URL = ('https://raw.githubusercontent.com/hugomailhot/'
                 'MorphoLex-en/master/MorphoLEX_en.xlsx')

# ── Morphemes covered in our 35-row Morpheme Mapping table ───────────────────
COVERED = {
    'ni','oni','lli','li','yan','loyan','liztli','yotl','otl',
    'tzintli','tontli','yoh','tik','tia','ltia','lo',
    'a','mo','tla','huey',
    'cenca','achi','miac','miec',
    'ce','ome','yei','nahui','macuil',
    'achtopa','zatepan','icpac','itlan','ixpan','nohuian','tepoz',
    # English / Spanish morphemes covered
    'tion','ness','ment','er','or','able','ible',
    'ize','ify','ful','less','ship','hood','dom',
    'ism','ist','ary','ory','al','ic','ous',
    'un','re','pre','dis','non','over','under',
    'anti','inter','co','sub','super','trans',
    'auto','mono','bi','tri','multi','poly','ex',
    # Spanish
    'cion','idad','mente','ismo','ista','cion','miento',
    'des','in','sin',
}

def covered(morpheme):
    return 'Yes' if morpheme.lower().strip('-') in COVERED else '— MISSING'

# ── Download helpers ─────────────────────────────────────────────────────────
def parse_morphynet(lang_code):
    url = f'{RAW_BASE}/{lang_code}/{lang_code}.derivational.v1.tsv'
    print(f"  Downloading MorphyNet {lang_code.upper()} …", end=' ', flush=True)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    lines = r.text.splitlines()
    print(f"{len(lines)} lines")

    counter  = Counter()          # (morpheme, type) → pair count
    examples = defaultdict(list)  # morpheme → [src→tgt, ...]

    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) < 6:
            continue
        if parts[0].lower() in ('source_word', 'lemma', '#'):
            continue
        src, tgt, morpheme, mtype = parts[0], parts[1], parts[4], parts[5].lower()
        if morpheme and morpheme != 'None':
            counter[(morpheme, mtype)] += 1
            if len(examples[morpheme]) < 3:
                examples[morpheme].append(f'{src}→{tgt}')
    return counter, examples


def parse_morpholex():
    print(f"  Downloading MorphoLEX-en …", end=' ', flush=True)
    r = requests.get(MORPHOLEX_URL, timeout=120)
    r.raise_for_status()
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        wb = openpyxl.load_workbook(io.BytesIO(r.content), read_only=True, data_only=True)

    def read_sheet(shname):
        ws = wb[shname]
        results = []
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i == 0:
                continue
            morpheme_raw = str(row[0]) if row[0] else ''
            morpheme = morpheme_raw.strip('<>').strip()
            try:
                fam  = int(row[1]) if row[1] else 0
                freq = int(float(row[2])) if row[2] else 0
            except (ValueError, TypeError):
                fam, freq = 0, 0
            if morpheme and fam > 0:
                results.append((morpheme.lower(), fam, freq))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    prefixes = read_sheet('All prefixes')
    suffixes  = read_sheet('All suffixes')
    wb.close()
    print(f"{len(prefixes)} prefixes, {len(suffixes)} suffixes")
    return prefixes, suffixes


# ── Download all data ─────────────────────────────────────────────────────────
print("Fetching databases …")
eng_mn_counter, eng_mn_ex = parse_morphynet('eng')
spa_mn_counter, spa_mn_ex = parse_morphynet('spa')
ml_prefixes, ml_suffixes  = parse_morpholex()

# ── Build English merged table ────────────────────────────────────────────────
# Key: (morpheme_str, 'prefix'|'suffix')
# Value: dict with per-source data
print("\nMerging English morpheme data …")
eng = {}   # (morpheme, type) → {mn_count, mn_ex, ml_fam, ml_freq}

def eng_add(morpheme, mtype, mn_count=0, mn_ex=None, ml_fam=0, ml_freq=0):
    key = (morpheme.lower(), mtype)
    if key not in eng:
        eng[key] = {'mn_count': 0, 'mn_ex': [], 'ml_fam': 0, 'ml_freq': 0}
    if mn_count:
        eng[key]['mn_count'] = mn_count
    if mn_ex:
        eng[key]['mn_ex'] = mn_ex
    if ml_fam:
        eng[key]['ml_fam'] = ml_fam
    if ml_freq:
        eng[key]['ml_freq'] = ml_freq

# MorphyNet ENG — include prefix/suffix with count >= 3
for (morpheme, mtype), count in eng_mn_counter.items():
    if mtype in ('prefix', 'suffix') and count >= 3:
        eng_add(morpheme, mtype, mn_count=count, mn_ex=eng_mn_ex[morpheme][:3])

# MorphoLEX prefixes — include all with family_size >= 2
for morpheme, fam, freq in ml_prefixes:
    if fam >= 2:
        eng_add(morpheme, 'prefix', ml_fam=fam, ml_freq=freq)

# MorphoLEX suffixes
for morpheme, fam, freq in ml_suffixes:
    if fam >= 2:
        eng_add(morpheme, 'suffix', ml_fam=fam, ml_freq=freq)

# Sort: prefixes first, then suffixes; within each, by best available count desc
def eng_sort_key(item):
    (morpheme, mtype), d = item
    importance = max(d['mn_count'], d['ml_fam'])
    return (0 if mtype == 'prefix' else 1, -importance)

eng_sorted = sorted(eng.items(), key=eng_sort_key)
print(f"  Total unique English morphemes: {len(eng_sorted)}")
print(f"  In both MorphyNet + MorphoLEX: "
      f"{sum(1 for _,d in eng_sorted if d['mn_count']>0 and d['ml_fam']>0)}")
print(f"  MorphyNet only: "
      f"{sum(1 for _,d in eng_sorted if d['mn_count']>0 and d['ml_fam']==0)}")
print(f"  MorphoLEX only: "
      f"{sum(1 for _,d in eng_sorted if d['mn_count']==0 and d['ml_fam']>0)}")

# ── Build Spanish merged table ────────────────────────────────────────────────
spa_sorted = sorted(
    [((m, t), c) for (m, t), c in spa_mn_counter.items()
     if t in ('prefix', 'suffix') and c >= 3],
    key=lambda x: (0 if x[0][1]=='prefix' else 1, -x[1])
)
print(f"  Total Spanish morphemes: {len(spa_sorted)}")

# ── Sheet helpers ─────────────────────────────────────────────────────────────
def get_or_create_tab(sh, title, rows, cols):
    try:
        ws = sh.worksheet(title)
        ws.clear()
        print(f"  Cleared '{title}'")
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=rows, cols=cols)
        print(f"  Created '{title}'")
    return ws

def fmt_n(n):
    return f'{n:,}' if n else ''

# ── ENG tab ───────────────────────────────────────────────────────────────────
print("\nBuilding ENG tab …")
ws_eng = get_or_create_tab(sh, 'Morpheme DB - ENG', rows=len(eng_sorted)+5, cols=9)
sid_eng = ws_eng.id

ENG_HEADER = [
    '#', 'Type', 'Morpheme',
    'MorphyNet ENG\n(pair count)',
    'MorphoLEX\n(family size)',
    'MorphoLEX\n(HAL freq)',
    'Example Words\n(MorphyNet)',
    'In Morpheme\nMapping Table?',
    'Notes',
]
eng_rows = [ENG_HEADER]
for i, ((morpheme, mtype), d) in enumerate(eng_sorted, start=1):
    # Flag overlapping (in both sources)
    in_mn  = d['mn_count'] > 0
    in_ml  = d['ml_fam'] > 0
    overlap = '⬤ both' if (in_mn and in_ml) else ('MorphyNet' if in_mn else 'MorphoLEX')
    notes = overlap

    eng_rows.append([
        str(i),
        mtype.capitalize(),
        f'{morpheme}-' if mtype == 'prefix' else f'-{morpheme}',
        fmt_n(d['mn_count']),
        fmt_n(d['ml_fam']),
        fmt_n(d['ml_freq']),
        ' | '.join(d['mn_ex']),
        covered(morpheme),
        notes,
    ])

ws_eng.update(values=eng_rows, range_name='A1', value_input_option='RAW')
print(f"  Written {len(eng_rows)-1} morpheme rows.")

# ── ESP tab ───────────────────────────────────────────────────────────────────
print("Building ESP tab …")
ws_esp = get_or_create_tab(sh, 'Morpheme DB - ESP', rows=len(spa_sorted)+5, cols=7)
sid_esp = ws_esp.id

ESP_HEADER = [
    '#', 'Type', 'Morpheme',
    'MorphyNet SPA\n(pair count)',
    'Example Words\n(MorphyNet)',
    'In Morpheme\nMapping Table?',
    'Notes',
]
esp_rows = [ESP_HEADER]
for i, ((morpheme, mtype), count) in enumerate(spa_sorted, start=1):
    esp_rows.append([
        str(i),
        mtype.capitalize(),
        f'{morpheme}-' if mtype == 'prefix' else f'-{morpheme}',
        fmt_n(count),
        ' | '.join(spa_mn_ex[morpheme][:3]),
        covered(morpheme),
        'Note: No Spanish equivalent of MorphoLEX available. MorphyNet only.',
    ])
    # Only put the note on first row
    if i == 1:
        esp_rows[-1][-1] = ('No Spanish equivalent of MorphoLEX available. '
                             'MorphyNet SPA is the sole source.')
    else:
        esp_rows[-1][-1] = ''

ws_esp.update(values=esp_rows, range_name='A1', value_input_option='RAW')
print(f"  Written {len(esp_rows)-1} morpheme rows.")

# ── Delete old "Morpheme DB" tab ──────────────────────────────────────────────
try:
    old_ws = sh.worksheet('Morpheme DB')
    sheets_svc.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={'requests': [{'deleteSheet': {'sheetId': old_ws.id}}]}
    ).execute()
    print("  Deleted old 'Morpheme DB' tab.")
except gspread.exceptions.WorksheetNotFound:
    print("  No old 'Morpheme DB' tab found.")

# ── Formatting for both tabs ──────────────────────────────────────────────────
def format_tab(sid, ws, n_rows, has_overlap_col=True):
    fmts = []

    # Freeze row 1
    fmts.append({'updateSheetProperties': {
        'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': 1}},
        'fields': 'gridProperties.frozenRowCount',
    }})

    # Header row: dark blue bg, white bold text, centered
    fmts.append({'repeatCell': {
        'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1},
        'cell': {'userEnteredFormat': {
            'textFormat': {'bold': True, 'fontSize': 9,
                           'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
            'backgroundColor': {'red': 0.12, 'green': 0.26, 'blue': 0.49},
            'horizontalAlignment': 'CENTER',
            'wrapStrategy': 'WRAP',
            'verticalAlignment': 'MIDDLE',
        }},
        'fields': 'userEnteredFormat(textFormat,backgroundColor,horizontalAlignment,'
                  'wrapStrategy,verticalAlignment)',
    }})

    # Data rows: wrap, top, small font
    fmts.append({'repeatCell': {
        'range': {'sheetId': sid, 'startRowIndex': 1},
        'cell': {'userEnteredFormat': {
            'wrapStrategy': 'WRAP', 'verticalAlignment': 'TOP',
            'textFormat': {'fontSize': 9},
        }},
        'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment,textFormat)',
    }})

    # Prefix rows: light blue tint (col B = 'Prefix')
    # Suffix rows: light green tint
    all_rows = ws.get_all_values()
    for i, row in enumerate(all_rows[1:], start=2):
        if not row[0].isdigit():
            continue
        mtype = row[1]
        if mtype == 'Prefix':
            color = {'red': 0.87, 'green': 0.93, 'blue': 0.98}
        else:
            color = {'red': 0.88, 'green': 0.96, 'blue': 0.88}
        fmts.append({'repeatCell': {
            'range': {'sheetId': sid, 'startRowIndex': i-1, 'endRowIndex': i},
            'cell': {'userEnteredFormat': {'backgroundColor': color}},
            'fields': 'userEnteredFormat.backgroundColor',
        }})

    # "— MISSING" cells: red highlight in "In Table?" column
    cov_col = 7 if has_overlap_col else 5  # 0-indexed col H or F
    for i, row in enumerate(all_rows[1:], start=2):
        if len(row) > cov_col and '— MISSING' in row[cov_col]:
            fmts.append({'repeatCell': {
                'range': {'sheetId': sid, 'startRowIndex': i-1, 'endRowIndex': i,
                          'startColumnIndex': cov_col, 'endColumnIndex': cov_col+1},
                'cell': {'userEnteredFormat': {
                    'backgroundColor': {'red': 0.99, 'green': 0.80, 'blue': 0.80},
                    'textFormat': {'bold': True,
                                   'foregroundColor': {'red': 0.72, 'green': 0.07, 'blue': 0.07}},
                }},
                'fields': 'userEnteredFormat(backgroundColor,textFormat)',
            }})

    # "⬤ both" (overlap) cells in Notes col: green highlight
    if has_overlap_col:
        notes_col = 8  # col I (0-indexed)
        for i, row in enumerate(all_rows[1:], start=2):
            if len(row) > notes_col and '⬤ both' in row[notes_col]:
                fmts.append({'repeatCell': {
                    'range': {'sheetId': sid, 'startRowIndex': i-1, 'endRowIndex': i,
                              'startColumnIndex': notes_col, 'endColumnIndex': notes_col+1},
                    'cell': {'userEnteredFormat': {
                        'backgroundColor': {'red': 0.84, 'green': 0.96, 'blue': 0.84},
                        'textFormat': {'bold': True},
                    }},
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)',
                }})

    # Bold morpheme column (C = index 2)
    fmts.append({'repeatCell': {
        'range': {'sheetId': sid, 'startRowIndex': 1, 'startColumnIndex': 2, 'endColumnIndex': 3},
        'cell': {'userEnteredFormat': {
            'textFormat': {'bold': True, 'fontFamily': 'Courier New', 'fontSize': 9},
        }},
        'fields': 'userEnteredFormat.textFormat',
    }})

    return fmts

print("\nApplying formatting …")
eng_fmts = format_tab(sid_eng, ws_eng, len(eng_rows), has_overlap_col=True)
esp_fmts = format_tab(sid_esp, ws_esp, len(esp_rows), has_overlap_col=False)

# Column widths — ENG
eng_widths = {0:35, 1:70, 2:110, 3:110, 4:100, 5:110, 6:280, 7:110, 8:90}
for col, px in eng_widths.items():
    eng_fmts.append({'updateDimensionProperties': {
        'range': {'sheetId': sid_eng, 'dimension': 'COLUMNS',
                  'startIndex': col, 'endIndex': col+1},
        'properties': {'pixelSize': px},
        'fields': 'pixelSize',
    }})

# Column widths — ESP
esp_widths = {0:35, 1:70, 2:110, 3:110, 4:280, 5:110, 6:200}
for col, px in esp_widths.items():
    esp_fmts.append({'updateDimensionProperties': {
        'range': {'sheetId': sid_esp, 'dimension': 'COLUMNS',
                  'startIndex': col, 'endIndex': col+1},
        'properties': {'pixelSize': px},
        'fields': 'pixelSize',
    }})

# Send formatting in batches (Sheets API limit: 200 requests per call)
def batch_fmt(requests_list):
    BATCH = 150
    for start in range(0, len(requests_list), BATCH):
        sheets_svc.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={'requests': requests_list[start:start+BATCH]}
        ).execute()

batch_fmt(eng_fmts)
print(f"  ENG formatting: {len(eng_fmts)} requests")
batch_fmt(esp_fmts)
print(f"  ESP formatting: {len(esp_fmts)} requests")

print(f"\nDone. Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
