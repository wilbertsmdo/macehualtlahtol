"""
update_doc_urls.py — fill in real document URLs for all blank/TBD entries in column E.
Column E is "Direct Document URL", inserted after the original URL column (D).
"""
import gspread
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request

TOKEN_FILE = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json'
SHEET_ID   = '11AEpdpY4cYNPoPn5ymZAP3SHygDoNzVPQpITQHxPrXM'

creds = OAuthCredentials.from_authorized_user_file(TOKEN_FILE)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

gc = gspread.authorize(creds)
ws = gc.open_by_key(SHEET_ID).get_worksheet(0)

# Updates: {row_number (1-based): new_direct_doc_url}
# Only rows that were blank / TBD / profile-only
UPDATES = {
    # Row 6 — INALI main portal → INALI publications studies index
    6:  'https://site.inali.gob.mx/INALIDhuchlab/estudios.html',

    # Row 8 — UNAM IIFL Johansson publications → his Dialnet page (many free full-text papers)
    8:  'https://dialnet.unirioja.es/servlet/autor?codigo=1082647',

    # Row 9 — UNAM IIH Nahuatl sources → Estudios de Cultura Náhuatl journal (IIH flagship)
    9:  'https://nahuatl.historicas.unam.mx/',

    # Row 11 — CIESAS fieldwork publications → Flores Farfán free PDF (language revitalization)
    11: 'https://linguapax.org/wp-content/uploads/2015/09/CMPL2002_T2_FloresFarfan.pdf',

    # Row 16 — INPI portal → INPI "Libros en lenguas indígenas" collection (includes Nahuatl PDFs)
    16: 'https://www.gob.mx/inpi/documentos/libros-en-lenguas-indigenas',

    # Row 18 — ELAR portal → specific ELAR Nahuatl collection (Natural History / Material Culture)
    18: 'https://www.elararchive.org/dk0292',

    # Row 20 — HathiTrust portal → open-access Nahuatl search in HathiTrust catalog
    20: 'https://catalog.hathitrust.org/Search/Home?lookfor=nahuatl&type=all&filter%5B%5D=language%3Anah&filter%5B%5D=access%3Aopen',

    # Row 22 — ResearchGate search query → specific paper: "The Hispanisation of modern Nahuatl varieties"
    22: 'https://www.researchgate.net/publication/370848239_The_Hispanisation_of_modern_Nahuatl_varieties',

    # Row 23 — Google Scholar UV search → specific paper: "Huasteca Nahuatl Relational Nouns and Prepositions"
    23: 'https://www.researchgate.net/publication/382997068_Huasteca_Nahuatl_Relational_Nouns_and_Prepositions_A_Cartography_of_Language_Contact',

    # Row 28 — JSTOR search → specific paper: Language Encounters / contact-induced lexical change
    28: 'https://www.researchgate.net/publication/313852771_Language_Encounters_A_systematic_study_of_contact-induced_change_in_colonial_Nahuatl',

    # Row 29 — Google Scholar Huasteca search → Toward a Comprehensive Model for Nahuatl Research
    29: 'https://www.researchgate.net/publication/284951356_Toward_a_Comprehensive_Model_for_Nahuatl_Language_Research_and_Revitalization',

    # Row 34 — Nava Vite Academia profile → paper written IN Nahuatl (Tlaneltoquilli, Chicontepec corn rituals)
    34: 'https://www.researchgate.net/publication/376352365_Tlaneltoquilli_tlen_mochihua_ica_cintli_ipan_tlalli_Chicontepec_tlamantli_chicahualiztli_ipan_tochinanco',

    # Row 35 — Nava Vite RG lab → paper written IN Nahuatl (Ma tihchikawakah tonawatlahtol…)
    35: 'https://www.researchgate.net/publication/371756268_Ma_tihchikawakah_tonawatlahtol_kemah_titemachtiah_sekinok_keh_ompa_tlahtolli_en_La_praxis_de_la_documentacion_del_legado_linguistico_y_cultural',

    # Row 37 — Figueroa-Saavedra profile → "Traducción de elementos eucarísticos al náhuatl" (2022) — neologism-rich!
    37: 'https://www.researchgate.net/publication/364118312_Traduccion_de_elementos_eucaristicos_al_nahuatl_activacion_modernizadora_e_intercultural',

    # Row 38 — Hasler CIESAS profile (profile IS the source; links to publication list)
    38: 'https://ciesas.edu.mx/hasler-hangert-andres-teyolotzin/',

    # Row 40 — Hasler Manual de gramática 1995 → Google Books (no free PDF found; WorldCat for library access)
    40: 'https://books.google.com/books/about/Manual_de_gram%C3%A1tica_del_n%C3%A1huatl_modern.html?id=7-2RtAEACAAJ',

    # Row 42 — Johansson Google Scholar profile → Dialnet (free full-text papers available)
    42: 'https://dialnet.unirioja.es/servlet/autor?codigo=1082647',

    # Row 63 — UNAM repository portal → ENALLT thesis repo (Nahuatl linguistics theses)
    63: 'https://ru.enallt.unam.mx/jspui/handle/ENALLT.UNAM/5',
}

# Write each update individually using the cell address
for row, url in sorted(UPDATES.items()):
    cell = f'E{row}'
    ws.update([[url]], cell)
    print(f"  Row {row:2d} → {url[:80]}")

print(f"\nDone — {len(UPDATES)} cells updated.")
print(f"Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
