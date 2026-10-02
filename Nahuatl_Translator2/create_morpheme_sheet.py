#!/usr/bin/env /data/data/com.termux/files/usr/bin/python3
"""
Parse morpheme_mapping_table.md and write it to a Google Sheet
in Drive folder 15HBoSkLT0dKjlxQquAv9zbmpQxjFaArH.

Columns:
  A: #  B: Section  C: Category
  D: EN Morpheme(s)  E: EN Word Examples
  F: ES Morpheme(s)  G: ES Word Examples
  H: NAH Morpheme(s) I: NAH Word Examples
  J: Productivity (MHN)  K: Generator Rule
"""
import re
import time
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SA_PATH   = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
FOLDER_ID = '15HBoSkLT0dKjlxQquAv9zbmpQxjFaArH'
MD_PATH   = '/storage/self/primary/PY_Projects/Macehualtlahtol/Nahuatl_Translator2/morpheme_mapping_table.md'
SCOPES    = ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']

# ── Auth ─────────────────────────────────────────────────────────────────────
creds      = Credentials.from_service_account_file(SA_PATH, scopes=SCOPES)
gc         = gspread.authorize(creds)
drive_svc  = build('drive',  'v3', credentials=creds)
sheets_svc = build('sheets', 'v4', credentials=creds)

# ── Markdown parser ───────────────────────────────────────────────────────────
def clean(text):
    text = re.sub(r'\*\*\*([^*]+)\*\*\*', r'\1', text)  # ***bold italic***
    text = re.sub(r'\*\*([^*]+)\*\*',     r'\1', text)  # **bold**
    text = re.sub(r'\*([^*\n]+)\*',       r'\1', text)  # *italic*
    text = re.sub(r'`([^`]+)`',           r'\1', text)  # `code`
    text = re.sub(r'  +', ' ', text)
    return text.strip()

def split_cell(raw):
    """Split 'morpheme<br>examples' into two strings."""
    parts = raw.split('<br>', 1)
    morpheme = clean(parts[0])
    if len(parts) > 1:
        examples = clean(parts[1].replace('<br>', ' | '))
    else:
        examples = ''
    return morpheme, examples

rows_data = []
current_section = 'General'

with open(MD_PATH) as f:
    for line in f:
        ls = line.strip()

        # Section header
        m = re.match(r'^## (SECTION \d+.*?)$', ls)
        if m:
            label = m.group(1)
            current_section = label.split(' — ', 1)[-1] if ' — ' in label else label
            continue

        if not ls.startswith('|'):
            continue

        cells = ls.strip('|').split('|')
        cells = [c.strip() for c in cells]

        # Skip separator and header rows
        if all(re.match(r'^:?-+:?$', c) for c in cells if c):
            continue
        if not cells or not re.match(r'^\d+$', cells[0]):
            continue
        if len(cells) < 6:
            continue

        en_morph,  en_ex  = split_cell(cells[2]) if len(cells) > 2 else ('', '')
        es_morph,  es_ex  = split_cell(cells[3]) if len(cells) > 3 else ('', '')
        nah_morph, nah_ex = split_cell(cells[4]) if len(cells) > 4 else ('', '')

        rows_data.append([
            cells[0],                               # A  #
            current_section,                        # B  Section
            clean(cells[1]),                        # C  Category
            en_morph,                               # D  EN Morpheme(s)
            en_ex,                                  # E  EN Word Examples
            es_morph,                               # F  ES Morpheme(s)
            es_ex,                                  # G  ES Word Examples
            nah_morph,                              # H  NAH Morpheme(s)
            nah_ex,                                 # I  NAH Word Examples
            clean(cells[5]) if len(cells) > 5 else '',  # J  Productivity
            clean(cells[6]) if len(cells) > 6 else '',  # K  Generator Rule
        ])

print(f"Parsed {len(rows_data)} rows")

# ── Spreadsheet already created via OAuth; SA has writer access ───────────────
SHEET_ID = '1TYw3gvcSGmCTQEKchEKlNDUm1BOL-i66jfhsNA1og-k'
print(f"Using existing sheet ID={SHEET_ID}")

# ── Write data ────────────────────────────────────────────────────────────────
sh = gc.open_by_key(SHEET_ID)
ws = sh.get_worksheet(0)
ws.update_title('Morpheme Mapping')

HEADER = [
    '#', 'Section', 'Category',
    'EN Morpheme(s)', 'EN Word Examples',
    'ES Morpheme(s)', 'ES Word Examples',
    'NAH Morpheme(s)', 'NAH Word Examples',
    'Productivity (MHN)', 'Generator Rule',
]
ws.update('A1', [HEADER] + rows_data, value_input_option='RAW')
print("Data written.")

# ── Formatting via Sheets API batchUpdate ────────────────────────────────────
sid = ws.id   # numeric sheet tab id (integer, e.g. 0)

# Section colours (one per section group)
SECTION_COLORS = {
    'NOMINALIZERS':                     {'red': 0.91, 'green': 0.96, 'blue': 0.87},
    'MODIFIERS / CLASSIFIERS':          {'red': 0.95, 'green': 0.91, 'blue': 0.98},
    'DEGREE / QUANTITY':                {'red': 0.98, 'green': 0.96, 'blue': 0.87},
    'RELATIONAL / STRUCTURAL PREFIXES': {'red': 0.87, 'green': 0.95, 'blue': 0.98},
    'SCIENTIFIC / TECHNICAL STEMS (Greek-Latin, no direct Nahuatl equivalent)':
                                        {'red': 0.99, 'green': 0.91, 'blue': 0.87},
}
DEFAULT_COLOR = {'red': 1.0, 'green': 1.0, 'blue': 1.0}

def col_color(section):
    for k, v in SECTION_COLORS.items():
        if k in section:
            return v
    return DEFAULT_COLOR

requests = []

# 1. Freeze row 1
requests.append({'updateSheetProperties': {
    'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': 1}},
    'fields': 'gridProperties.frozenRowCount',
}})

# 2. Bold + background header row
requests.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1},
    'cell': {
        'userEnteredFormat': {
            'textFormat': {'bold': True, 'fontSize': 10},
            'backgroundColor': {'red': 0.20, 'green': 0.40, 'blue': 0.65},
            'horizontalAlignment': 'CENTER',
        }
    },
    'fields': 'userEnteredFormat(textFormat,backgroundColor,horizontalAlignment)',
}})

# Header text colour white
requests.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1},
    'cell': {'userEnteredFormat': {'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}}},
    'fields': 'userEnteredFormat.textFormat.foregroundColor',
}})

# 3. Wrap text for all data rows
requests.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 1},
    'cell': {'userEnteredFormat': {'wrapStrategy': 'WRAP', 'verticalAlignment': 'TOP'}},
    'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment)',
}})

# 4. Row background colours by section
for i, row in enumerate(rows_data):
    color = col_color(row[1])  # row[1] is Section
    requests.append({'repeatCell': {
        'range': {'sheetId': sid, 'startRowIndex': i+1, 'endRowIndex': i+2},
        'cell': {'userEnteredFormat': {'backgroundColor': color}},
        'fields': 'userEnteredFormat.backgroundColor',
    }})

# 5. Bold the category column (C)
requests.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 1, 'startColumnIndex': 2, 'endColumnIndex': 3},
    'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}},
    'fields': 'userEnteredFormat.textFormat.bold',
}})

# 6. Column widths (pixels)
COL_WIDTHS = {
    0: 35,   # #
    1: 120,  # Section
    2: 200,  # Category
    3: 160,  # EN Morpheme
    4: 200,  # EN Examples
    5: 160,  # ES Morpheme
    6: 200,  # ES Examples
    7: 200,  # NAH Morpheme
    8: 280,  # NAH Examples
    9: 180,  # Productivity
    10: 320, # Generator Rule
}
for col_idx, px in COL_WIDTHS.items():
    requests.append({'updateDimensionProperties': {
        'range': {'sheetId': sid, 'dimension': 'COLUMNS',
                  'startIndex': col_idx, 'endIndex': col_idx + 1},
        'properties': {'pixelSize': px},
        'fields': 'pixelSize',
    }})

# 7. Morpheme columns (D, F, H) in monospace + bold
for col in [3, 5, 7]:
    requests.append({'repeatCell': {
        'range': {'sheetId': sid, 'startRowIndex': 1,
                  'startColumnIndex': col, 'endColumnIndex': col+1},
        'cell': {'userEnteredFormat': {
            'textFormat': {'fontFamily': 'Courier New', 'bold': True, 'fontSize': 9}
        }},
        'fields': 'userEnteredFormat.textFormat',
    }})

# 8. Rule column (K) smaller font
requests.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 1, 'startColumnIndex': 10, 'endColumnIndex': 11},
    'cell': {'userEnteredFormat': {'textFormat': {'fontSize': 8}}},
    'fields': 'userEnteredFormat.textFormat.fontSize',
}})

# Execute formatting
sheets_svc.spreadsheets().batchUpdate(
    spreadsheetId=SHEET_ID,
    body={'requests': requests}
).execute()
print("Formatting applied.")

print(f"\nDone! Sheet URL:")
print(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
