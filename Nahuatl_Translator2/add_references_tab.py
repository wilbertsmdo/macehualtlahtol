#!/usr/bin/env /data/data/com.termux/files/usr/bin/python3
"""
Add a "References" tab to the Morpheme Mapping spreadsheet.
All sources used in or relevant to this morpheme mapping project.
"""
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SA_PATH  = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
SHEET_ID = '1TYw3gvcSGmCTQEKchEKlNDUm1BOL-i66jfhsNA1og-k'
SCOPES   = ['https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive']

creds      = Credentials.from_service_account_file(SA_PATH, scopes=SCOPES)
gc         = gspread.authorize(creds)
sheets_svc = build('sheets', 'v4', credentials=creds)
sh         = gc.open_by_key(SHEET_ID)

# ── Create or clear the References tab ───────────────────────────────────────
try:
    ws = sh.worksheet('References')
    ws.clear()
    print("Cleared existing References tab.")
except gspread.exceptions.WorksheetNotFound:
    ws = sh.add_worksheet(title='References', rows=60, cols=7)
    print("Created References tab.")

sid = ws.id

# ── Reference data ────────────────────────────────────────────────────────────
HEADER = ['#', 'Category', 'Author(s)', 'Year', 'Title', 'Publisher / Journal', 'URL / DOI / Notes']

REFS = [
    # ── Nahuatl dictionaries & grammars ──────────────────────────────────────
    ['1', 'Nahuatl — Dictionary',
     'Molina, Alonso de', '1571',
     'Vocabulario en Lengua Castellana y Mexicana y Mexicana y Castellana',
     'Antonio de Spinosa, Mexico City',
     'Facsimile reprint: Porrúa 1970. Earliest comprehensive Nahuatl–Spanish dictionary.'],
    ['2', 'Nahuatl — Dictionary',
     'Karttunen, Frances', '1992',
     'An Analytical Dictionary of Nahuatl',
     'University of Oklahoma Press',
     'Primary ACK reference. ISBN 978-0-8061-2421-6'],
    ['3', 'Nahuatl — Grammar',
     'Andrews, J. Richard', '2003',
     'Introduction to Classical Nahuatl (revised ed.)',
     'University of Oklahoma Press',
     'ISBN 978-0-8061-3452-9. A = Andrews in ACK orthography convention.'],
    ['4', 'Nahuatl — Grammar & Texts',
     'Lockhart, James', '2001',
     'Nahuatl as Written: Lessons in Older Written Nahuatl',
     'Stanford University Press / UCLA Latin American Center',
     'ISBN 978-0-8047-4282-4. Companion workbook used for delta review (col L).'],
    ['5', 'Nahuatl — Modern Dictionary',
     'Sullivan, John & IDIEZ team', '2016',
     'Nahuatl Dictionary (Modern Huasteca Nahuatl)',
     'Instituto de Docencia e Investigación Etnológica de Zacatecas (IDIEZ) / Universidad Veracruzana',
     'Chicontepec, Veracruz variety. Primary source for MHN forms in this table.'],
    ['6', 'Nahuatl — Dictionary',
     'Siméon, Rémi', '1885',
     'Dictionnaire de la Langue Nahuatl ou Mexicaine',
     'Imprimerie Nationale, Paris',
     'Facsimile: Akademische Druck, 1963. Comprehensive classical Nahuatl lexicon.'],

    # ── Nahuatl — neologism & word-formation research ─────────────────────────
    ['7', 'Nahuatl — Neologism Research',
     'Gruda, M.; Haimovich, L.; Sullivan, J.', '2023',
     'Lexical creativity in modern Nahuatl: On the interplay between internal and external factors',
     'Lingua, 295, 103607',
     'doi:10.1016/j.lingua.2023.103607. Key paper; copy at dictionaries/sources/lexical_creativity_modern_nahuatl.pdf'],
    ['8', 'Nahuatl — Word-Formation Theory',
     'Štekauer, Pavol', '2005',
     'Meaning Predictability in Word Formation: Novel, Context-Free Naming Units',
     'John Benjamins, Amsterdam',
     'ISBN 978-90-272-2370-2. Onomasiological framework applied in this project.'],

    # ── English word-formation ────────────────────────────────────────────────
    ['9', 'English — Word-Formation',
     'Plag, Ingo', '2003',
     'Word-Formation in English',
     'Cambridge University Press',
     'ISBN 978-0-521-52563-7. Best single-volume systematic treatment; includes productivity data.'],
    ['10', 'English — Word-Formation',
     'Bauer, Laurie', '1983',
     'English Word-Formation',
     'Cambridge University Press',
     'ISBN 978-0-521-28492-1. Classic reference morpheme inventory.'],
    ['11', 'English — Compounding',
     'Lieber, Rochelle; Štekauer, Pavol (eds.)', '2009',
     'The Oxford Handbook of Compounding',
     'Oxford University Press',
     'ISBN 978-0-19-921953-9. Cross-linguistic compounding including English.'],

    # ── Spanish word-formation ────────────────────────────────────────────────
    ['12', 'Spanish — Word-Formation',
     'Lang, Mervyn F.', '1990',
     'Spanish Word Formation: Productive Derivational Morphology in the Modern Spanish Lexicon',
     'Routledge, London',
     'ISBN 978-0-415-05053-0. Direct Spanish equivalent of Plag (2003).'],
    ['13', 'Spanish — Grammar (Morphology)',
     'Real Academia Española', '2009',
     'Nueva gramática de la lengua española, Vol. 1: Morfología',
     'Espasa-Calpe, Madrid',
     'ISBN 978-84-670-3002-4. Authoritative; §§1–10 cover derivation and compounding.'],
    ['14', 'Spanish — Word-Formation',
     'Varela Ortega, Soledad', '2005',
     'Morfología léxica: la formación de palabras',
     'Gredos, Madrid',
     'ISBN 978-84-249-2772-8. Standard Spanish-language textbook on derivational morphology.'],

    # ── Morpheme databases ────────────────────────────────────────────────────
    ['15', 'Database — English & Spanish',
     'Batsuren, K.; Bella, G.; Giunchiglia, F.', '2021',
     'MorphyNet: a large multilingual database of derivational and inflectional morphology',
     'Proceedings of the 18th SIGMORPHON Workshop on Computational Research in Phonetics, '
     'Phonology, and Morphology. ACL Anthology',
     'https://github.com/kbatsuren/MorphyNet | doi:10.18653/v1/2021.sigmorphon-1.5. '
     'Open. 15 languages incl. English (eng) and Spanish (spa). Used in this project.'],
    ['16', 'Database — English',
     'Sánchez-Gutiérrez, C.H.; Mailhot, H.; Deacon, S.H.; Wilson, M.A.', '2018',
     'MorphoLEX: A derivational morphological database for 70,000 English words',
     'Behavior Research Methods, 50(4), 1568–1580',
     'doi:10.3758/s13428-017-0981-8 | https://github.com/hugomailhot/MorphoLex-en. '
     'Free CELEX2-derived English morpheme database. Used in this project.'],
    ['17', 'Database — English/German/Dutch (licensed)',
     'Baayen, R.H.; Piepenbrock, R.; Gulikers, L.', '1995',
     'CELEX2: The CELEX Lexical Database (Release 2)',
     'Linguistic Data Consortium (LDC), Philadelphia',
     'LDC Catalog No. LDC96L14 | https://catalog.ldc.upenn.edu/LDC96L14. '
     'Requires LDC license — NOT freely downloadable. See MorphoLEX (ref 16) as open alternative.'],

    # ── Cross-linguistic / theoretical ───────────────────────────────────────
    ['18', 'Cross-linguistic — Morphology',
     'Lieber, Rochelle', '2009',
     'Introducing Morphology',
     'Cambridge University Press',
     'ISBN 978-0-521-67943-9. Accessible cross-linguistic intro; good for mapping EN↔ES↔NAH.'],
    ['19', 'Cross-linguistic — Database',
     'Kirov, C. et al.', '2018',
     'UniMorph 2.0: Universal Morphology',
     'Proceedings of LREC 2018',
     'https://unimorph.github.io. Cross-linguistic morphological inflection database; '
     'includes Nahuatl (limited).'],

    # ── This project ──────────────────────────────────────────────────────────
    ['20', 'This Project — Internal',
     'Macehualtlahtol / Nahuatl_Translator2', '2026',
     'Cross-Language Morpheme Mapping Table (EN ↔ ES ↔ NAH)',
     'This Google Spreadsheet',
     f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit. '
     'Local file: morpheme_mapping_table.md. ACK orthography; '
     'MHN variety (Chicontepec, Veracruz). 35 morpheme categories + Missing Morphemes analysis.'],
    ['21', 'This Project — NMT Model',
     'Macehualtlahtol / Nahuatl_Translator2', '2026',
     'NLLB fine-tuned EN→NAH translation model (D5)',
     'Internal fine-tune on NLLB-200 (Meta AI)',
     'Base model: facebook/nllb-200-distilled-600M. '
     'Training data: data/training/clean/. Eval results in project plan.'],
]

# ── Write data ────────────────────────────────────────────────────────────────
ws.update(values=[HEADER] + REFS, range_name='A1', value_input_option='RAW')
print(f"Written {len(REFS)} references.")

# ── Formatting ────────────────────────────────────────────────────────────────
requests = []

# Freeze row 1
requests.append({'updateSheetProperties': {
    'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': 1}},
    'fields': 'gridProperties.frozenRowCount',
}})

# Header: bold, dark blue bg, white text
requests.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1},
    'cell': {'userEnteredFormat': {
        'textFormat': {'bold': True, 'fontSize': 10,
                       'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
        'backgroundColor': {'red': 0.12, 'green': 0.26, 'blue': 0.49},
        'horizontalAlignment': 'CENTER',
    }},
    'fields': 'userEnteredFormat(textFormat,backgroundColor,horizontalAlignment)',
}})

# All data rows: wrap, top-align
requests.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 1},
    'cell': {'userEnteredFormat': {
        'wrapStrategy': 'WRAP', 'verticalAlignment': 'TOP',
        'textFormat': {'fontSize': 9},
    }},
    'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment,textFormat)',
}})

# Category column (B): color-code by section
CATEGORY_COLORS = {
    'Nahuatl':    {'red': 0.85, 'green': 0.93, 'blue': 0.83},
    'English':    {'red': 0.87, 'green': 0.93, 'blue': 0.98},
    'Spanish':    {'red': 0.98, 'green': 0.93, 'blue': 0.84},
    'Database':   {'red': 0.95, 'green': 0.88, 'blue': 0.98},
    'Cross':      {'red': 0.98, 'green': 0.95, 'blue': 0.87},
    'This':       {'red': 0.93, 'green': 0.93, 'blue': 0.93},
}
for i, row in enumerate(REFS):
    cat = row[1]
    color = next((v for k, v in CATEGORY_COLORS.items() if k in cat),
                 {'red': 1.0, 'green': 1.0, 'blue': 1.0})
    requests.append({'repeatCell': {
        'range': {'sheetId': sid, 'startRowIndex': i+1, 'endRowIndex': i+2},
        'cell': {'userEnteredFormat': {'backgroundColor': color}},
        'fields': 'userEnteredFormat.backgroundColor',
    }})

# Column widths
COL_WIDTHS = {0: 35, 1: 160, 2: 220, 3: 50, 4: 340, 5: 230, 6: 380}
for col, px in COL_WIDTHS.items():
    requests.append({'updateDimensionProperties': {
        'range': {'sheetId': sid, 'dimension': 'COLUMNS',
                  'startIndex': col, 'endIndex': col+1},
        'properties': {'pixelSize': px},
        'fields': 'pixelSize',
    }})

# Bold author column (C)
requests.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 1, 'startColumnIndex': 2, 'endColumnIndex': 3},
    'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}},
    'fields': 'userEnteredFormat.textFormat.bold',
}})

sheets_svc.spreadsheets().batchUpdate(
    spreadsheetId=SHEET_ID, body={'requests': requests}
).execute()
print("Formatting applied.")
print(f"\nDone. Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
