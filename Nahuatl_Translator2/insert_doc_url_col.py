"""
insert_doc_url_col.py
Inserts a "Direct Document URL" column at position E (after the existing URL column D).
Fills in direct document links; leaves blank where the existing URL is already correct
or where no direct link is known.
"""
import gspread
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request

TOKEN_FILE = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json'
SHEET_ID   = '11AEpdpY4cYNPoPn5ymZAP3SHygDoNzVPQpITQHxPrXM'

creds = OAuthCredentials.from_authorized_user_file(TOKEN_FILE)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

gc   = gspread.authorize(creds)
sh   = gc.open_by_key(SHEET_ID)
ws   = sh.get_worksheet(0)

# ── 1. Insert a blank column at index 4 (column E, 0-based) ──────────────
sh.batch_update({'requests': [{
    'insertDimension': {
        'range': {
            'sheetId': ws.id,
            'dimension': 'COLUMNS',
            'startIndex': 4,   # after column D (URL)
            'endIndex': 5,
        },
        'inheritFromBefore': False,
    }
}]})
print("Column inserted at E.")

# Reload worksheet after structural change
ws = sh.get_worksheet(0)

# ── 2. Write header ──────────────────────────────────────────────────────
ws.update([[' Direct Document URL']], 'E1')
ws.format('E1', {
    'textFormat': {'bold': True, 'foregroundColorStyle': {'rgbColor': {'red': 1, 'green': 1, 'blue': 1}}},
    'backgroundColorStyle': {'rgbColor': {'red': 0.2, 'green': 0.4, 'blue': 0.7}},
})

# ── 3. Direct document URLs keyed by row number (1-based, row 1 = header)
# Rules:
#   - If current URL already IS the direct document → copy it
#   - If current URL is a profile/portal/search → provide the real doc URL or leave ""
#   - "TBD" = known to exist but direct link not yet found

doc_urls = {
    # row: direct_document_url
    2:  'https://www.uv.mx/mlcn/',                          # program page IS the source
    3:  'https://www.academia.edu/resource/work/83874914',  # direct paper
    4:  'https://dumps.wikimedia.org/nahwiki/latest/',       # direct dump
    5:  'https://nah.wikipedia.org/',                        # live site
    6:  '',   # INALI portal — no single doc
    7:  'https://www.inali.gob.mx/clin-inali/',             # catalog page
    8:  '',   # UNAM IIFL portal
    9:  '',   # UNAM IIH portal
    10: 'https://tesiunam.dgb.unam.mx/',                    # search portal (no single doc)
    11: '',   # CIESAS portal
    12: 'https://www.idiez.org.mx/',
    13: 'https://ailla.utexas.org/islandora/object/ailla:119393',
    14: 'https://www.sil.org/resources/search/language/nah',
    15: 'https://bold.bible/',
    16: '',   # INPI portal
    17: 'https://libros.conaliteg.gob.mx/',
    18: '',   # ELAR portal
    19: 'https://www.endangeredlanguages.com/',
    20: '',   # HathiTrust portal
    21: 'https://archive.org/search?query=nahuatl',
    22: '',   # ResearchGate search query
    23: '',   # Google Scholar search query
    24: 'https://www.gob.mx/inpi/acciones-y-programas/sistema-de-radiodifusoras-culturales-indigenistas',
    25: 'https://nah.wiktionary.org/',
    26: 'https://www.tlahtoa.org/',
    27: 'https://nahuatlnation.org/',
    28: '',   # JSTOR search query
    29: '',   # Google Scholar search query
    30: 'https://huggingface.co/tachiwin',
    31: 'https://huggingface.co/tachiwin/tokenizer_64k',
    32: 'https://nah.wikisource.org/',
    33: 'https://www.opensubtitles.org/en/search/sublanguageid-nah',
    # ── Appended rows ────────────────────────────────────────────────────
    34: '',   # Nava Vite Academia profile (not a doc)
    35: '',   # Nava Vite RG lab page (not a doc)
    36: 'https://www.researchgate.net/publication/361947721_In_tlahkuilolyotl_ken_se_nawatlahtolchikawalistli_ipan_weyitlamachtiloyan_se_tlachiwalistli_tlen_moneki_axkan_mochiwa',
    37: '',   # Figueroa-Saavedra profile
    38: '',   # Hasler CIESAS profile
    39: 'https://librosciesas.com/producto/el-nahua-de-la-huasteca/',    # CIESAS official store
    40: 'TBD',  # Hasler Manual — no direct link found yet
    41: 'https://www.researchgate.net/publication/272507462_Nahuatl_in_the_Plural_Dialectology_and_Activism_in_Mexico',
    42: '',   # Johansson Google Scholar profile
    43: 'https://ru.historicas.unam.mx/handle/20.500.12525/6327',
    44: 'https://nahuatl.historicas.unam.mx/',
    45: 'https://aclanthology.org/L16-1666/',
    46: 'https://huggingface.co/datasets/somosnlp-hackathon-2022/Axolotl-Spanish-Nahuatl',
    47: 'https://huggingface.co/datasets/Danielbrdz/BarcenasNahuatl',
    48: 'https://aclanthology.org/volumes/2021.americasnlp-1/',
    49: 'https://github.com/AmericasNLP/americasnlp2021',
    50: 'https://aclanthology.org/volumes/2023.americasnlp-1/',
    51: 'https://dumps.wikimedia.org/nahwiki/20260901/',
    52: 'https://www.sciencedirect.com/science/article/abs/pii/S0024384123000128',
    53: 'https://www.researchgate.net/publication/365690985_Continuity_and_Change_in_Modern_Nahuatl_Word_Formation',
    54: 'https://arxiv.org/abs/2512.14239',
    55: 'https://arxiv.org/abs/2511.19118',
    56: 'https://sunypress.edu/Blog/2025/Making-the-Word-Flourish-A-Conversation-on-Nahua-Literature-Activism-and-Living-Knowledge',
    57: 'https://www.amazon.com/dp/607867434X',
    58: 'https://latinamericanliteraturetoday.org/2025/11/two-poems-in-nahuatl/',
    59: 'https://www.tupeloquarterly.com/editors-feature/fire-is-a-breath-of-sparks-interview-with-nahua-poet-martin-tonalmeyotl-curated-by-ming-di/',
    60: 'https://site.inali.gob.mx/publicaciones/libro_lectura_nahuatl/pdf/lectura_del_nahuatl.pdf',
    61: 'https://www.inali.gob.mx/detalle/lengua-nawatlahtolli-nahuatl',
    62: 'https://www.inali.gob.mx/detalle/concluye-primera-etapa-del-proyecto-de-dialectologia-nahuatl-coordinado-por-el-inali',
    63: '',   # UNAM repository portal
    64: 'https://www.iifilologicas.unam.mx/pnovohispano/index.php?page=tesis-unam&l=13',
    65: 'https://www.researchgate.net/publication/236701172_The_IDIEZ_Project_A_Model_for_Indigenous_Language_Revitalization_in_Higher_Education',
    66: 'https://www.mexicolore.co.uk/aztecs/language/modern-nahua-poem',
}

# Build column E values as a list of [value] lists (rows 2–66)
total_rows = ws.row_count  # use actual row count
values = [[doc_urls.get(r, '')] for r in range(2, 67)]

ws.update(values, 'E2:E66')
print(f"Wrote {len(values)} direct document URLs to column E.")
print(f"Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
