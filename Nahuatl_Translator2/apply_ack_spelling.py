#!/usr/bin/env /data/data/com.termux/files/usr/bin/python3
"""
Standardise all Nahuatl forms in the Morpheme Mapping sheet to
ACK (Andrews-Campbell-Karttunen) Classical orthography.

ACK rules applied:
  ts   → tz          (IDIEZ ts = classical tz)
  k+a/o/u → c+vowel  (IDIEZ k = classical c before a/o/u)
  k+e/i → qu+vowel   (IDIEZ k = classical qu before e/i)
  k (final/before consonant) → c
  w+vowel → hu+vowel  (IDIEZ w = classical hu)
  vowel+w → vowel+uh  (IDIEZ w = classical uh in coda)
  se- (morpheme ONE) → ce-

Also corrects wrong word forms:
  tikatl/tikayotl → tlacatl/tlacayotl  (tlacatl is the correct Nahuatl word for "person")
  siuatl/siuayotl → cihuatl/cihuayotl  (cihuatl is the ACK word for "woman")
  pilyotl → pillotl  (Lockhart -otl allomorph after vowel-final stem)
"""
import re
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SA_PATH  = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
SHEET_ID = '1TYw3gvcSGmCTQEKchEKlNDUm1BOL-i66jfhsNA1og-k'
MD_PATH  = '/storage/self/primary/PY_Projects/Macehualtlahtol/Nahuatl_Translator2/morpheme_mapping_table.md'
SCOPES   = ['https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive']

creds      = Credentials.from_service_account_file(SA_PATH, scopes=SCOPES)
gc         = gspread.authorize(creds)
sheets_svc = build('sheets', 'v4', credentials=creds)
sh         = gc.open_by_key(SHEET_ID)
ws         = sh.get_worksheet(0)

# ── Ordered replacement table ─────────────────────────────────────────────────
# Longer/more specific patterns FIRST to avoid partial-match cascades.
REPLACEMENTS = [
    # ── Wrong words (must precede generic k-rules) ───────────────────────────
    ('tikatl',          'tlacatl'),
    ('tikayotl',        'tlacayotl'),
    ('tlakatl',         'tlacatl'),
    ('tlakayotl',       'tlacayotl'),
    # IDIEZ woman form: siuatl → cihuatl (s→c, iu→ihu)
    ('siuayotl',        'cihuayotl'),
    ('siuatl',          'cihuatl'),
    # -otl allomorph correction (Lockhart): pilli ends in consonant-cluster → pillotl
    ('pilyotl',         'pillotl'),

    # ── ts → tz ──────────────────────────────────────────────────────────────
    ('-tsintli',        '-tzintli'),
    ('tsintli',         'tzintli'),
    # individual pausa form
    ('-tsin',           '-tzin'),
    ('nantsin',         'nantzin'),
    ('tlahtotsintli',   'tlahtotzintli'),
    ('totoltsintli',    'totoltzintli'),

    # ── ihk- → ihc- (k before u → c) ─────────────────────────────────────────
    ('ihkuilo',         'ihcuilo'),   # covers ihkuiloa, ihkuilolli, ihkuiliztli, ihkuiloni

    # ── Specific compound forms (before generic k-rules) ─────────────────────
    # causative of cualli: kualitia → cualtia (more idiomatic than cualitia)
    ('kualitia',        'cualtia'),
    # kuali → cualli (k before u → c; double-l is absolutive)
    ('a-kuali',         'a-cualli'),
    ('kuali',           'cualli'),
    # neltic stative (k-final → c)
    ('neltik',          'neltic'),
    # chika/chikaltia (k before a → c)
    ('chikaltia',       'chicaltia'),
    ('chika',           'chica'),
    # mexikatl → mexicatl (k before a → c)
    ('mexikatl',        'mexicatl'),
    # -katl suffix → -catl (as morpheme label)
    ('-katl (Classical -catl)', '-catl'),
    ('-katl',           '-catl'),
    # teki (cut) → tequi (k before i → qu); must precede teki→ replacements
    ('tekiyan',         'tequiyan'),
    ('tekiliztli',      'tequiliztli'),
    ('tekili',          'tequili'),
    ('tekini',          'tequini'),
    ('teki',            'tequi'),
    # tlahtoka → tlahtoca (k before a → c)
    ('tlahtokayotl',    'tlahtocayotl'),
    ('tlahtokani',      'tlahtocani'),
    ('tlahtokatzintli', 'tlahtocatzintli'),
    ('tlahtoka-',       'tlahtoca-'),
    ('tlahtoka',        'tlahtoca'),
    # kokoa → cocoa (k before o → c); kokokyotl → cocolyotl
    ('kokokyotl',       'cocolyotl'),
    ('kokoa',           'cocoa'),
    # totonkayotl → totoncayotl (k before a → c)
    ('totonkayotl',     'totoncayotl'),
    ('totonki',         'totonqui'),
    # chikopil → chicopil (k before o → c)
    ('chikopil',        'chicopil'),
    # makuil → macuil (k before u → c)
    ('makuil',          'macuil'),
    # miek/miak → miec/miac (k final → c)
    ('miek-',           'miec-'),
    ('miek',            'miec'),
    ('miak-',           'miac-'),
    ('miak',            'miac'),
    # tomin- related: tominpixkayotl etc.
    ('tominpixkayotl',  'tominpixcayotl'),
    ('tominpixka',      'tominpixca'),

    # ── Numeral ONE: se → ce (morpheme only, as prefix/adverb) ───────────────
    # Be specific to Nahuatl morpheme contexts
    ('oc se ',          'oc ce '),
    ('oc se-',          'oc ce-'),
    ('oc se\n',         'oc ce\n'),
    ('oc se|',          'oc ce|'),
    ('se- (one)',       'ce- (one)'),
    ('se- + noun',      'ce- + noun'),
    ('seyotl',          'ceyotl'),
    ('seyolia',         'ceyolia'),
    # Remaining standalone se- morpheme marker (e.g. "se-" in morpheme column)
    ('se-',             'ce-'),

    # ── Orthography note updates ──────────────────────────────────────────────
    ('IDIEZ/SEP modern orthography',
     'ACK (Andrews-Campbell-Karttunen) orthography'),
    ('IDIEZ/SEP', 'ACK'),
    ('IDIEZ modern orthography', 'ACK orthography'),
    # Section 6 classifier table header note
    ('IDIEZ / Chicontepec, Veracruz',
     'ACK orthography — Modern Huasteca Nahuatl, Chicontepec, Veracruz'),
]

def apply_replacements(text):
    if not isinstance(text, str) or not text:
        return text
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text

# ── Read full sheet ───────────────────────────────────────────────────────────
print("Reading sheet …")
all_vals = ws.get_all_values()
n_rows   = len(all_vals)
n_cols   = len(all_vals[0]) if all_vals else 0
print(f"  {n_rows} rows × {n_cols} cols")

# ── Apply replacements, track changes ─────────────────────────────────────────
changed = []  # (row_i, col_i, old, new)

new_vals = []
for r_i, row in enumerate(all_vals):
    new_row = []
    for c_i, cell in enumerate(row):
        new_cell = apply_replacements(cell)
        if new_cell != cell:
            changed.append((r_i + 1, c_i + 1, cell[:60], new_cell[:60]))
        new_row.append(new_cell)
    new_vals.append(new_row)

print(f"\nCells to update: {len(changed)}")
for r, c, old, new in changed:
    col_letter = chr(64 + c)
    print(f"  {col_letter}{r}: {repr(old[:50])} → {repr(new[:50])}")

# ── Write back ────────────────────────────────────────────────────────────────
if changed:
    ws.update(values=new_vals, range_name='A1', value_input_option='RAW')
    print(f"\nSheet updated — {len(changed)} cells corrected.")
else:
    print("\nNo changes needed.")

# ── Update morpheme_mapping_table.md ─────────────────────────────────────────
print("\nUpdating morpheme_mapping_table.md …")
with open(MD_PATH) as f:
    md_text = f.read()

md_new = md_text
for old, new in REPLACEMENTS:
    md_new = md_new.replace(old, new)

# Update the orthography note line specifically
md_new = md_new.replace(
    'All Nahuatl forms use IDIEZ/SEP modern orthography '
    '(k not qu/c, w not hu, s not z/c before e/i, ts not tz). '
    'Classical orthography equivalents given in parentheses where helpful.',
    'All Nahuatl forms use **ACK (Andrews-Campbell-Karttunen) orthography**: '
    'qu/c (not k), hu/uh (not w), tz (not ts). '
    'Source: Andrews 2003, Karttunen 1992, Sullivan/IDIEZ 2016 aligned to classical standard.'
)
# Update last-updated note
md_new = md_new.replace(
    '*Last updated: 2026-09-27. Primary reference: IDIEZ Modern Huasteca Nahuatl',
    '*Last updated: 2026-09-27. Orthography: ACK (Andrews-Campbell-Karttunen). Primary reference: Modern Huasteca Nahuatl'
)

if md_new != md_text:
    with open(MD_PATH, 'w') as f:
        f.write(md_new)
    print("  morpheme_mapping_table.md updated.")
else:
    print("  No changes to .md file.")

print("\nDone.")
