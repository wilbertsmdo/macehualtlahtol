#!/usr/bin/env /data/data/com.termux/files/usr/bin/python3
"""
Rebuild "Morpheme DB - ESP" tab with English equivalent columns:
  F: ENG Equivalent(s)
  G: ENG MorphyNet (pair count)
  H: ENG MorphoLEX (family size)
  I: In Morpheme Mapping Table?
  J: Semantic note (SPA↔ENG relationship)

Data re-fetched from MorphyNet + MorphoLEX to populate ENG lookup.
"""
import io, warnings
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

RAW_BASE      = 'https://raw.githubusercontent.com/kbatsuren/MorphyNet/main'
MORPHOLEX_URL = ('https://raw.githubusercontent.com/hugomailhot/'
                 'MorphoLex-en/master/MorphoLEX_en.xlsx')

# ── SPA → ENG morpheme equivalence map ───────────────────────────────────────
# (spa_morpheme, type) → (eng_equivalents_list, semantic_note)
SPA_TO_ENG = {
    # ── Nominalizing suffixes ─────────────────────────────────────────────────
    ('ción',    'suffix'): (['tion', 'ation'],  'Action/result nominalization'),
    ('sión',    'suffix'): (['sion', 'tion'],   'Action/result nominalization'),
    ('miento',  'suffix'): (['ment'],            'Process/result noun'),
    ('ura',     'suffix'): (['ure', 'ness'],     'State / condition noun'),
    ('eza',     'suffix'): (['ness', 'ity'],     'Abstract quality noun'),
    ('idad',    'suffix'): (['ity', 'ness'],     'Abstract quality/state'),
    ('ismo',    'suffix'): (['ism'],             'Doctrine / movement'),
    ('anza',    'suffix'): (['ance', 'ness'],    'State / result noun'),
    ('encia',   'suffix'): (['ence', 'ance'],    'State / property noun'),
    ('ancia',   'suffix'): (['ance'],            'State / property noun'),
    ('aje',     'suffix'): (['age'],             'Collection / process noun'),
    ('ada',     'suffix'): (['ful', 'ade'],      'Set / action noun'),
    # ── Agentive / instrumental suffixes ─────────────────────────────────────
    ('dor',     'suffix'): (['er', 'or'],        'Agent / instrument'),
    ('ista',    'suffix'): (['ist'],             'Practitioner / adherent'),
    ('ero',     'suffix'): (['er', 'or'],        'Agent / trade / place'),
    ('ante',    'suffix'): (['ant', 'er'],       'Active agent'),
    ('ente',    'suffix'): (['ent', 'er'],       'Active agent / state adj.'),
    ('dora',    'suffix'): (['er', 'or'],        'Agent (fem.) / machine'),
    # ── Adjectival suffixes ───────────────────────────────────────────────────
    ('ico',     'suffix'): (['ic', 'ical'],      'Relating to X'),
    ('oso',     'suffix'): (['ous', 'ful'],      'Full of / characterized by X'),
    ('ivo',     'suffix'): (['ive'],             'Tending to / capable of X'),
    ('al',      'suffix'): (['al'],              'Relating to X'),
    ('ario',    'suffix'): (['ary', 'ory'],      'Relating to / place of X'),
    ('able',    'suffix'): (['able'],            'Capable of being X-ed'),
    ('ible',    'suffix'): (['ible'],            'Capable of being X-ed'),
    ('ado',     'suffix'): (['ed', 'ate'],       'Participial / result adj.'),
    ('ado',     'suffix'): (['ed'],              'Past participle / result'),
    ('eño',     'suffix'): (['an', 'ese'],       'Demonym / inhabitant'),
    ('ano',     'suffix'): (['an'],              'Demonym / inhabitant'),
    ('és',      'suffix'): (['ese', 'ish'],      'Demonym'),
    # ── Verbal suffixes ───────────────────────────────────────────────────────
    ('ear',     'suffix'): (['ize', 'ify'],      'Denominative verb formation'),
    ('izar',    'suffix'): (['ize'],             'Causative / inchoative verb'),
    ('ificar',  'suffix'): (['ify'],             'Causative verb'),
    ('ar',      'suffix'): (['ate', 'ize'],      'Infinitive → derivational verb'),
    # ── Diminutive / augmentative ─────────────────────────────────────────────
    ('ito',     'suffix'): (['let', 'ling'],     'Diminutive (affective)'),
    ('ita',     'suffix'): (['let', 'ling'],     'Diminutive fem. (affective)'),
    ('illo',    'suffix'): (['let'],             'Diminutive'),
    ('ón',      'suffix'): (['er', 'big'],       'Augmentative / pejorative'),
    ('ote',     'suffix'): (['big'],             'Augmentative pejorative'),
    ('ín',      'suffix'): (['let', 'ling'],     'Diminutive (regional)'),
    # ── Adverbial suffix ──────────────────────────────────────────────────────
    ('mente',   'suffix'): (['ly'],              'Manner adverb (most productive Spanish suffix)'),
    # ── Prefixes ─────────────────────────────────────────────────────────────
    ('des',     'prefix'): (['dis', 'un', 'de'], 'Reversal / privation / negation'),
    ('re',      'prefix'): (['re'],              'Repetition / again / back'),
    ('anti',    'prefix'): (['anti'],            'Against / opposition'),
    ('in',      'prefix'): (['in', 'un'],        'Negation (before consonant)'),
    ('im',      'prefix'): (['im'],              'Negation (before b/p)'),
    ('ir',      'prefix'): (['ir'],              'Negation (before r)'),
    ('il',      'prefix'): (['il'],              'Negation (before l)'),
    ('pre',     'prefix'): (['pre'],             'Before / prior'),
    ('pos',     'prefix'): (['post'],            'After / following'),
    ('post',    'prefix'): (['post'],            'After / following'),
    ('sub',     'prefix'): (['sub'],             'Under / below / subordinate'),
    ('sobre',   'prefix'): (['over', 'super'],   'Above / over / excess'),
    ('super',   'prefix'): (['super'],           'Above / beyond / excess'),
    ('hiper',   'prefix'): (['hyper'],           'Excessive / above normal'),
    ('hipo',    'prefix'): (['hypo'],            'Under / below normal'),
    ('inter',   'prefix'): (['inter'],           'Between / among'),
    ('intra',   'prefix'): (['intra'],           'Within'),
    ('co',      'prefix'): (['co'],              'Together / jointly'),
    ('con',     'prefix'): (['con', 'co'],       'Together / jointly'),
    ('pro',     'prefix'): (['pro'],             'In favor of / forward / professional'),
    ('auto',    'prefix'): (['auto'],            'Self / automatic'),
    ('ex',      'prefix'): (['ex'],              'Former / outside / out of'),
    ('multi',   'prefix'): (['multi'],           'Many / multiple'),
    ('poli',    'prefix'): (['poly'],            'Many (Greek-origin)'),
    ('bi',      'prefix'): (['bi'],              'Two / double'),
    ('mono',    'prefix'): (['mono'],            'One / single'),
    ('uni',     'prefix'): (['uni'],             'One / single (Latin-origin)'),
    ('trans',   'prefix'): (['trans'],           'Across / beyond / through'),
    ('tras',    'prefix'): (['trans'],           'Across (variant of trans-)'),
    ('semi',    'prefix'): (['semi'],            'Half / partial'),
    ('neo',     'prefix'): (['neo'],             'New / recent form of X'),
    ('pseudo',  'prefix'): (['pseudo'],          'False / apparent / imitation'),
    ('macro',   'prefix'): (['macro'],           'Large-scale / big'),
    ('micro',   'prefix'): (['micro'],           'Small-scale / tiny'),
    ('tri',     'prefix'): (['tri'],             'Three'),
    ('ab',      'prefix'): (['ab'],              'Away from'),
    ('a',       'prefix'): (['a', 'un'],         'Privative / without (Greek-origin)'),
    ('vice',    'prefix'): (['vice'],            'Deputy / in place of'),
    ('entre',   'prefix'): (['inter', 'entre'],  'Between / among'),
    ('contra',  'prefix'): (['counter', 'anti'], 'Against / counter'),
    ('circun',  'prefix'): (['circum'],          'Around / surrounding'),
    ('extra',   'prefix'): (['extra'],           'Outside / beyond / additional'),
    ('para',    'prefix'): (['para'],            'Beside / beyond / parallel'),
    ('eco',     'prefix'): (['eco'],             'Ecological / environmental'),
    ('tele',    'prefix'): (['tele'],            'Distance / remote'),
    ('foto',    'prefix'): (['photo'],           'Light / photography'),
}

# ── Coverage check ────────────────────────────────────────────────────────────
COVERED = {
    'ni','oni','lli','li','yan','loyan','liztli','yotl','otl',
    'tzintli','tontli','yoh','tik','tia','ltia','lo',
    'a','mo','tla','huey',
    'cenca','achi','miac','miec',
    'ce','ome','yei','nahui','macuil',
    'achtopa','zatepan','icpac','itlan','ixpan','nohuian','tepoz',
    'tion','ness','ment','er','or','able','ible',
    'ize','ify','ful','less','ship','hood','dom',
    'ism','ist','ary','ory','al','ic','ous',
    'un','re','pre','dis','non','over','under',
    'anti','inter','co','sub','super','trans',
    'auto','mono','bi','tri','multi','poly','ex',
    'cion','idad','mente','ismo','ista','miento',
    'des','in','sin',
}
def covered(m): return 'Yes' if m.lower().strip('-') in COVERED else '— MISSING'

# ── Download MorphyNet SPA ────────────────────────────────────────────────────
def parse_morphynet(lang_code):
    url = f'{RAW_BASE}/{lang_code}/{lang_code}.derivational.v1.tsv'
    print(f"  MorphyNet {lang_code.upper()} …", end=' ', flush=True)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    lines = r.text.splitlines()
    print(f"{len(lines)} lines")
    counter  = Counter()
    examples = defaultdict(list)
    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) < 6 or parts[0].lower() in ('source_word','lemma','#'):
            continue
        src, tgt, morpheme, mtype = parts[0], parts[1], parts[4], parts[5].lower()
        if morpheme and morpheme != 'None':
            counter[(morpheme, mtype)] += 1
            if len(examples[morpheme]) < 3:
                examples[morpheme].append(f'{src}→{tgt}')
    return counter, examples

# ── Download MorphoLEX + MorphyNet ENG (for ENG lookup) ──────────────────────
def parse_morpholex():
    print(f"  MorphoLEX-en …", end=' ', flush=True)
    r = requests.get(MORPHOLEX_URL, timeout=120)
    r.raise_for_status()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        wb = openpyxl.load_workbook(io.BytesIO(r.content), read_only=True, data_only=True)
    def read_sh(name):
        rows = []
        for i, row in enumerate(wb[name].iter_rows(values_only=True)):
            if i == 0: continue
            m = str(row[0]).strip('<>').strip().lower() if row[0] else ''
            try:   fam = int(row[1]) if row[1] else 0
            except: fam = 0
            try:   freq = int(float(row[2])) if row[2] else 0
            except: freq = 0
            if m and fam > 0: rows.append((m, fam, freq))
        rows.sort(key=lambda x: x[1], reverse=True)
        return rows
    prefixes = read_sh('All prefixes')
    suffixes  = read_sh('All suffixes')
    wb.close()
    print(f"{len(prefixes)}p / {len(suffixes)}s")
    return prefixes, suffixes

print("Fetching data …")
spa_mn_counter, spa_mn_ex = parse_morphynet('spa')
eng_mn_counter, eng_mn_ex = parse_morphynet('eng')
ml_prefixes, ml_suffixes  = parse_morpholex()

# ── Build ENG lookup: morpheme → {mn_count, ml_fam, ml_freq} ─────────────────
eng_lookup = defaultdict(lambda: {'mn_count': 0, 'ml_fam': 0, 'ml_freq': 0})

for (morpheme, mtype), count in eng_mn_counter.items():
    if mtype in ('prefix', 'suffix'):
        eng_lookup[(morpheme.lower(), mtype)]['mn_count'] = count

for morpheme, fam, freq in ml_prefixes:
    eng_lookup[(morpheme.lower(), 'prefix')]['ml_fam']  = fam
    eng_lookup[(morpheme.lower(), 'prefix')]['ml_freq'] = freq

for morpheme, fam, freq in ml_suffixes:
    eng_lookup[(morpheme.lower(), 'suffix')]['ml_fam']  = fam
    eng_lookup[(morpheme.lower(), 'suffix')]['ml_freq'] = freq

def eng_stats(eng_equivalents, mtype):
    """Return (eng_label, mn_count_str, ml_fam_str) for the best ENG match."""
    best_mn, best_ml, best_freq = 0, 0, 0
    labels = []
    for eq in eng_equivalents:
        key = (eq.lower(), mtype)
        d = eng_lookup[key]
        best_mn  = max(best_mn,  d['mn_count'])
        best_ml  = max(best_ml,  d['ml_fam'])
        best_freq= max(best_freq,d['ml_freq'])
        # Format label e.g. "re-" or "-tion"
        label = f'{eq}-' if mtype == 'prefix' else f'-{eq}'
        labels.append(label)
    label_str = ' / '.join(labels)
    mn_str  = f'{best_mn:,}' if best_mn  else ''
    ml_str  = f'{best_ml:,}' if best_ml  else ''
    return label_str, mn_str, ml_str

# ── Build ESP tab rows ─────────────────────────────────────────────────────────
print("\nBuilding ESP tab rows …")

ESP_HEADER = [
    '#', 'Type', 'Morpheme\n(SPA)',
    'MorphyNet SPA\n(pair count)',
    'Example Words\n(MorphyNet SPA)',
    'ENG Equivalent(s)',
    'ENG MorphyNet\n(pair count)',
    'ENG MorphoLEX\n(family size)',
    'In Morpheme\nMapping Table?',
    'SPA ↔ ENG Relationship',
]

spa_sorted = sorted(
    [((m, t), c) for (m, t), c in spa_mn_counter.items()
     if t in ('prefix', 'suffix') and c >= 3],
    key=lambda x: (0 if x[0][1]=='prefix' else 1, -x[1])
)

esp_rows = [ESP_HEADER]
for i, ((morpheme, mtype), count) in enumerate(spa_sorted, start=1):
    key = (morpheme.lower(), mtype)
    mapping = SPA_TO_ENG.get(key)

    if mapping:
        eng_equivalents, sem_note = mapping
        eng_label, mn_str, ml_str = eng_stats(eng_equivalents, mtype)
    else:
        eng_label, mn_str, ml_str = '', '', ''
        sem_note = ''

    spa_label = f'{morpheme}-' if mtype == 'prefix' else f'-{morpheme}'
    examples  = ' | '.join(spa_mn_ex[morpheme][:3])

    esp_rows.append([
        str(i),
        mtype.capitalize(),
        spa_label,
        f'{count:,}',
        examples,
        eng_label,
        mn_str,
        ml_str,
        covered(morpheme),
        sem_note,
    ])

print(f"  {len(esp_rows)-1} morpheme rows")
mapped = sum(1 for r in esp_rows[1:] if r[5])
print(f"  Mapped to ENG equivalent: {mapped} / {len(esp_rows)-1}")

# ── Write to sheet ────────────────────────────────────────────────────────────
ws = sh.worksheet('Morpheme DB - ESP')
ws.clear()
ws.update(values=esp_rows, range_name='A1', value_input_option='RAW')
print("  Data written.")
sid = ws.id

# ── Formatting ────────────────────────────────────────────────────────────────
print("Applying formatting …")
fmts = []

# Freeze row 1
fmts.append({'updateSheetProperties': {
    'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': 1}},
    'fields': 'gridProperties.frozenRowCount',
}})

# Header: dark blue, white bold, centered, wrapped
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

# Data rows: wrap, top, font 9
fmts.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 1},
    'cell': {'userEnteredFormat': {
        'wrapStrategy': 'WRAP', 'verticalAlignment': 'TOP',
        'textFormat': {'fontSize': 9},
    }},
    'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment,textFormat)',
}})

# Morpheme column C: monospace bold
fmts.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 1,
              'startColumnIndex': 2, 'endColumnIndex': 3},
    'cell': {'userEnteredFormat': {
        'textFormat': {'bold': True, 'fontFamily': 'Courier New', 'fontSize': 9},
    }},
    'fields': 'userEnteredFormat.textFormat',
}})

# ENG Equivalent column F: monospace italic
fmts.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 1,
              'startColumnIndex': 5, 'endColumnIndex': 6},
    'cell': {'userEnteredFormat': {
        'textFormat': {'italic': True, 'fontFamily': 'Courier New', 'fontSize': 9},
    }},
    'fields': 'userEnteredFormat.textFormat',
}})

# Row-level colors + cell highlights (batch in chunks)
all_rows = esp_rows  # use in-memory data directly

for i, row in enumerate(all_rows[1:], start=2):
    if not row[0].isdigit():
        continue
    mtype = row[1]
    # Row background: prefix = blue, suffix = green
    row_color = ({'red': 0.87, 'green': 0.93, 'blue': 0.98}
                 if mtype == 'Prefix'
                 else {'red': 0.88, 'green': 0.96, 'blue': 0.88})
    fmts.append({'repeatCell': {
        'range': {'sheetId': sid, 'startRowIndex': i-1, 'endRowIndex': i},
        'cell': {'userEnteredFormat': {'backgroundColor': row_color}},
        'fields': 'userEnteredFormat.backgroundColor',
    }})

    # "— MISSING" in col I (index 8): red
    if len(row) > 8 and '— MISSING' in row[8]:
        fmts.append({'repeatCell': {
            'range': {'sheetId': sid, 'startRowIndex': i-1, 'endRowIndex': i,
                      'startColumnIndex': 8, 'endColumnIndex': 9},
            'cell': {'userEnteredFormat': {
                'backgroundColor': {'red': 0.99, 'green': 0.80, 'blue': 0.80},
                'textFormat': {'bold': True,
                               'foregroundColor': {'red': 0.72, 'green': 0.07, 'blue': 0.07}},
            }},
            'fields': 'userEnteredFormat(backgroundColor,textFormat)',
        }})

    # ENG Equivalent col F (index 5): teal tint when populated
    if len(row) > 5 and row[5].strip():
        fmts.append({'repeatCell': {
            'range': {'sheetId': sid, 'startRowIndex': i-1, 'endRowIndex': i,
                      'startColumnIndex': 5, 'endColumnIndex': 6},
            'cell': {'userEnteredFormat': {
                'backgroundColor': {'red': 0.85, 'green': 0.95, 'blue': 0.95},
            }},
            'fields': 'userEnteredFormat.backgroundColor',
        }})

# Column widths
COL_WIDTHS = {
    0: 35,   # #
    1: 70,   # Type
    2: 110,  # Morpheme SPA
    3: 110,  # MorphyNet SPA count
    4: 280,  # Example Words
    5: 140,  # ENG Equivalent
    6: 110,  # ENG MorphyNet count
    7: 110,  # ENG MorphoLEX family size
    8: 110,  # In Table?
    9: 280,  # Semantic note
}
for col, px in COL_WIDTHS.items():
    fmts.append({'updateDimensionProperties': {
        'range': {'sheetId': sid, 'dimension': 'COLUMNS',
                  'startIndex': col, 'endIndex': col+1},
        'properties': {'pixelSize': px},
        'fields': 'pixelSize',
    }})

# Send in batches of 150
BATCH = 150
for start in range(0, len(fmts), BATCH):
    sheets_svc.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={'requests': fmts[start:start+BATCH]}
    ).execute()

print(f"  {len(fmts)} formatting requests sent.")
print(f"\nDone. Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
