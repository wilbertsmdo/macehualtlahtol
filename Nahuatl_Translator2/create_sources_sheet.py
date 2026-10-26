"""
create_sources_sheet.py
Creates a Google Sheet "Nahuatl Sources — Research Links" in the specified Drive folder,
sets up headers, and populates with known sources.
"""
import gspread
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_FILE = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json'
FOLDER_ID = '1fK7iz3pbq4Xrrp2yKczYOEg5AAUClwjY'
SHEET_NAME = 'Nahuatl Sources — Research Links'

from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request

creds = OAuthCredentials.from_authorized_user_file(TOKEN_FILE)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

# Sheet already created — use existing ID
sheet_id = '11AEpdpY4cYNPoPn5ymZAP3SHygDoNzVPQpITQHxPrXM'
print(f'Using existing sheet: https://docs.google.com/spreadsheets/d/{sheet_id}')

# --- Open with gspread and write headers + data ---
gc = gspread.authorize(creds)
sh = gc.open_by_key(sheet_id)
ws = sh.get_worksheet(0)
ws.update_title('Sources')

HEADERS = [
    'Institution / Source',
    'Author(s)',
    'Title / Document Name',
    'URL',
    'Nahuatl Variant',
    'Document Type',
    'Language Format',
    'Freely Accessible?',
    'Neologism-Rich?',
    'Notes',
]

# ── Data rows ──────────────────────────────────────────────────────────────
# Each tuple: (institution, authors, title, url, variant, doc_type,
#              lang_format, freely_accessible, neologism_rich, notes)
ROWS = [
    # ── UV / MLCN ────────────────────────────────────────────────────────
    (
        'Universidad Veracruzana — MLCN',
        'Various (faculty & students)',
        'Maestría en Lingüística e Interculturalidad — program page',
        'https://www.uv.mx/mlcn/',
        'Multiple variants',
        'Program / institutional page',
        'Spanish (metadata); program produces NAH theses',
        'Yes',
        'Yes',
        'Landing page — find faculty names and thesis repository links here',
    ),
    (
        'Academia.edu — Prof. Nava (UV/MLCN)',
        'Nava (first name TBD)',
        'Paper on Nahuatl (title TBD — see URL)',
        'https://www.academia.edu/resource/work/83874914',
        'TBD',
        'Academic paper',
        'TBD (likely Spanish + Nahuatl)',
        'Yes (Academia.edu)',
        'Likely',
        'Starting node — harvest coauthor list from this paper',
    ),
    # ── Nahuatl Wikipedia ────────────────────────────────────────────────
    (
        'Wikimedia Foundation',
        'Community contributors',
        'Nahuatl Wikipedia (nah.wikipedia.org) — full dump',
        'https://dumps.wikimedia.org/nahwiki/latest/',
        'Mixed (Classical + modern variants)',
        'Online encyclopedia / XML corpus dump',
        'Monolingual Nahuatl',
        'Yes (CC BY-SA)',
        'Yes',
        '~12,000 articles; modern topics (tech, science, geography) force neologisms; downloadable XML',
    ),
    (
        'Wikimedia Foundation',
        'Community contributors',
        'Nahuatl Wikipedia — live site',
        'https://nah.wikipedia.org/',
        'Mixed',
        'Online encyclopedia',
        'Monolingual Nahuatl',
        'Yes (CC BY-SA)',
        'Yes',
        'Browse individual articles; good source for modern coined vocabulary',
    ),
    # ── INALI ────────────────────────────────────────────────────────────
    (
        'INALI — Instituto Nacional de Lenguas Indígenas',
        'Government / institutional',
        'INALI main portal (Nahuatl resources)',
        'https://www.inali.gob.mx/',
        'Multiple official variants',
        'Government portal',
        'Spanish + Nahuatl',
        'Yes',
        'Yes',
        'Publishes normalization norms, technical glossaries, and parallel legal texts',
    ),
    (
        'INALI',
        'Government / institutional',
        'Catálogo de las Lenguas Indígenas Nacionales — Nahuatl variants',
        'https://www.inali.gob.mx/clin-inali/',
        'All Nahuatl variants',
        'Reference catalog',
        'Spanish + Nahuatl',
        'Yes',
        'No',
        'Documents 30+ Nahuatl variants; useful for dialect metadata',
    ),
    # ── UNAM ─────────────────────────────────────────────────────────────
    (
        'UNAM — Instituto de Investigaciones Filológicas',
        'Patrick Johansson K.',
        'Publications on Nahuatl literature and language (multiple)',
        'https://www.iifilologicas.unam.mx/',
        'Classical + Modern',
        'Academic papers / books',
        'Spanish + Nahuatl excerpts',
        'Partial (institutional site)',
        'Moderate',
        'Johansson is prolific on Nahuatl poetics and modern usage; search his profile',
    ),
    (
        'UNAM — Instituto de Investigaciones Históricas',
        'Various',
        'Nahuatl sources and publications',
        'https://www.historicas.unam.mx/',
        'Classical + Early Modern',
        'Academic papers / edited volumes',
        'Spanish + Nahuatl',
        'Partial',
        'Low–Moderate',
        'Lockhart school; more colonial than modern but foundational for grammar',
    ),
    (
        'TESIUNAM — UNAM thesis repository',
        'Various (UNAM graduates)',
        'Theses on / in Nahuatl',
        'https://tesiunam.dgb.unam.mx/',
        'Various',
        'Graduate theses',
        'Spanish (+ Nahuatl sections)',
        'Yes',
        'Moderate',
        'Search "náhuatl" — filter for linguistics; some theses include extended Nahuatl texts',
    ),
    # ── CIESAS ───────────────────────────────────────────────────────────
    (
        'CIESAS — Centro de Investigaciones y Estudios Superiores en Antropología Social',
        'Various',
        'Nahuatl linguistics fieldwork publications',
        'https://www.ciesas.edu.mx/',
        'Various',
        'Academic papers / fieldwork reports',
        'Spanish + Nahuatl',
        'Partial',
        'Moderate',
        'Fieldwork transcriptions often include extended Nahuatl passages',
    ),
    # ── IDIEZ ────────────────────────────────────────────────────────────
    (
        'IDIEZ — Instituto de Docencia e Investigación Etnológica de Zacatecas',
        'Rufino Ramírez Celestino, Victoriano de la Cruz Cruz, et al.',
        'IDIEZ Nahuatl-English dictionary and linguistic resources',
        'https://www.idiez.org.mx/',
        'Huasteca Nahuatl',
        'Dictionary / linguistic resources',
        'Bilingual NAH-EN + Spanish',
        'Yes',
        'No (descriptive, not technical)',
        'Already in our pipeline — 6,345 EN→NAH entries; Huasteca dialect (Chicontepec)',
    ),
    # ── AILLA ────────────────────────────────────────────────────────────
    (
        'AILLA — Archive of the Indigenous Languages of Latin America (UT Austin)',
        'Various researchers',
        'Nahuatl language archive collections',
        'https://ailla.utexas.org/islandora/object/ailla:119393',
        'Multiple variants',
        'Audio recordings + transcriptions',
        'Nahuatl (+ Spanish metadata)',
        'Partial (registration required)',
        'Low–Moderate',
        'Archived field recordings with transcripts; oral/natural speech register',
    ),
    # ── SIL International ────────────────────────────────────────────────
    (
        'SIL International',
        'Various SIL linguists',
        'SIL Nahuatl language resources',
        'https://www.sil.org/resources/search/language/nah',
        'Multiple variants',
        'Grammars, wordlists, Bible translations',
        'Bilingual (various)',
        'Yes',
        'No',
        'Bible parallel text is clean bilingual data; grammars useful for rule extraction',
    ),
    (
        'SIL International — BOLD (Bible)',
        'SIL translators',
        'Nahuatl Bible translations (various dialect versions)',
        'https://bold.bible/',
        'Huasteca + other variants',
        'Parallel Bible text',
        'Bilingual NAH-ES + EN',
        'Yes',
        'No (religious register)',
        'High-quality parallel text; ~31K verse pairs per version; consistent register',
    ),
    # ── INPI / CDI ───────────────────────────────────────────────────────
    (
        'INPI — Instituto Nacional de los Pueblos Indígenas (formerly CDI)',
        'Government / institutional',
        'INPI digital library — indigenous language materials',
        'https://www.inpi.gob.mx/',
        'Multiple',
        'Government documents / bilingual materials',
        'Spanish + Nahuatl',
        'Yes',
        'Low',
        'Policy docs, cultural materials; search for Nahuatl section',
    ),
    # ── SEP ──────────────────────────────────────────────────────────────
    (
        'SEP — Secretaría de Educación Pública',
        'Government / institutional',
        'Bilingual intercultural education textbooks in Nahuatl',
        'https://libros.conaliteg.gob.mx/',
        'Multiple variants',
        'Textbooks (bilingual)',
        'Bilingual NAH-ES',
        'Yes',
        'No (educational register)',
        'K-12 bilingual textbooks; useful for basic parallel sentences',
    ),
    # ── Endangered Languages Archive ─────────────────────────────────────
    (
        'ELAR — Endangered Languages Archive (SOAS University of London)',
        'Various researchers',
        'Nahuatl collections at ELAR',
        'https://www.elararchive.org/',
        'Multiple',
        'Audio + transcriptions',
        'Nahuatl (oral)',
        'Partial',
        'Low',
        'Search "Nahuatl" in their catalog; some collections have transcribed texts',
    ),
    # ── Endangered Languages Project ─────────────────────────────────────
    (
        'Endangered Languages Project (Google-supported)',
        'Various',
        'Nahuatl resources catalog',
        'https://www.endangeredlanguages.com/',
        'Multiple',
        'Resource catalog',
        'Various',
        'Yes (catalog; resources vary)',
        'Low–Moderate',
        'Aggregates links to other Nahuatl resources; good discovery tool',
    ),
    # ── HathiTrust / Internet Archive ────────────────────────────────────
    (
        'HathiTrust Digital Library',
        'Various (historical + 20th c.)',
        'Nahuatl texts collection',
        'https://www.hathitrust.org/',
        'Classical + Early Modern',
        'Digitized books',
        'Nahuatl + Spanish/Latin',
        'Partial (public domain)',
        'Low (historical)',
        'Search "nahuatl" — mostly pre-1927 public domain; Colonial-era texts',
    ),
    (
        'Internet Archive',
        'Various',
        'Nahuatl language materials',
        'https://archive.org/search?query=nahuatl',
        'Multiple',
        'Digitized books / audio',
        'Various',
        'Yes (public domain)',
        'Low–Moderate',
        'Mix of historical and modern; filter by date for post-1950 materials',
    ),
    # ── ResearchGate ─────────────────────────────────────────────────────
    (
        'ResearchGate',
        'Various',
        'Nahuatl linguistics papers (search)',
        'https://www.researchgate.net/search?q=nahuatl+linguistics',
        'Various',
        'Academic papers (search index)',
        'Spanish + Nahuatl sections',
        'Partial (ResearchGate access)',
        'Moderate',
        'Good for finding researchers; many papers available as PDFs via request',
    ),
    # ── Google Scholar queries ────────────────────────────────────────────
    (
        'Google Scholar',
        'Various',
        'Search: "en náhuatl" site:uv.mx — UV papers with Nahuatl content',
        'https://scholar.google.com/scholar?q=%22en+n%C3%A1huatl%22+site%3Auv.mx',
        'Various',
        'Search query (academic papers)',
        'Spanish + Nahuatl',
        'Varies',
        'Moderate',
        'Targeted UV query; adapt to other institutional domains',
    ),
    # ── Radio XEZV ───────────────────────────────────────────────────────
    (
        'CDI / INPI — Radio XEZV "La Voz de la Huasteca"',
        'Radio staff / community speakers',
        'XEZV radio station — Nahuatl broadcasts (Huasteca)',
        'https://www.gob.mx/inpi/acciones-y-programas/sistema-de-radiodifusoras-culturales-indigenistas',
        'Huasteca Nahuatl',
        'Radio broadcasts (oral)',
        'Monolingual Nahuatl (oral)',
        'Partial (live stream; no transcript archive found)',
        'Low–Moderate',
        'Broadcasts in Huasteca Nahuatl — our target dialect; no public transcript archive; potential future contact',
    ),
    # ── Wiktionary ───────────────────────────────────────────────────────
    (
        'Wiktionary (Nahuatl entries)',
        'Community contributors',
        'Wiktionary Nahuatl entries (Classical)',
        'https://nah.wiktionary.org/',
        'Classical Nahuatl',
        'Dictionary / wiktionary',
        'Monolingual Nahuatl definitions',
        'Yes (CC BY-SA)',
        'Low',
        'Classical definitions written in Nahuatl; small but linguistically consistent',
    ),
    # ── Tlahtoa (Modern Nahuatl news) ────────────────────────────────────
    (
        'Tlahtoa (online Nahuatl media)',
        'Editorial team',
        'Tlahtoa — contemporary Nahuatl-language content',
        'https://www.tlahtoa.org/',
        'Modern / Mixed',
        'Online media (articles)',
        'Monolingual Nahuatl',
        'Yes',
        'Yes',
        'Contemporary journalism and cultural articles in Nahuatl; modern register',
    ),
    # ── Mexica Movement / community sources ──────────────────────────────
    (
        'Nahuatl Nation (nahuatlnation.org)',
        'Community',
        'Nahuatl Nation — modern Nahuatl learning resources',
        'https://nahuatlnation.org/',
        'Modern / Unified',
        'Learning site / articles',
        'Bilingual EN-NAH',
        'Yes',
        'Yes',
        'Community-produced modern Nahuatl texts; useful for EN-NAH parallel pairs',
    ),
    # ── JSTOR ────────────────────────────────────────────────────────────
    (
        'JSTOR',
        'Various',
        'Nahuatl linguistics papers (search)',
        'https://www.jstor.org/action/doBasicSearch?Query=nahuatl',
        'Various',
        'Academic papers',
        'Spanish + English (with Nahuatl excerpts)',
        'Partial (JSTOR access)',
        'Moderate',
        'Good for formal linguistics papers; filter by language studies journals',
    ),
    # ── Chicontepec / Huasteca specific ──────────────────────────────────
    (
        'Various (Huasteca Nahuatl community)',
        'Community speakers / researchers',
        'Huasteca Nahuatl resources — search query',
        'https://scholar.google.com/scholar?q=huasteca+nahuatl',
        'Huasteca Nahuatl',
        'Academic papers (search)',
        'Spanish + Nahuatl',
        'Varies',
        'Moderate',
        'Targeted search for our primary dialect; prioritize results from IDIEZ-affiliated researchers',
    ),
    # ── Tachiwin / Tiyat ─────────────────────────────────────────────────
    (
        'Tachiwin — HuggingFace organization',
        'Tachiwin team (ljcamargo et al.)',
        'Tachiwin datasets (multilingual indigenous language corpora)',
        'https://huggingface.co/tachiwin',
        'Multiple (including Nahuatl)',
        'ML dataset / corpus',
        'Monolingual + parallel',
        'Yes (open)',
        'Yes',
        'Their training data may include Nahuatl; check individual dataset cards for Nahuatl content',
    ),
    (
        'Tachiwin / UNAM',
        'ljcamargo et al.',
        'Tiyat tokenizer_64k — trained on 70% indigenous language data',
        'https://huggingface.co/tachiwin/tokenizer_64k',
        'Multiple (70% indigenous)',
        'ML tokenizer model',
        'N/A (tokenizer)',
        'Yes (open)',
        'N/A',
        'Custom tokenizer for indigenous languages; our tokenizer comparison target (see tokenizer_compare.py)',
    ),
    # ── Wikisource ───────────────────────────────────────────────────────
    (
        'Wikisource',
        'Various',
        'Nahuatl texts on Wikisource',
        'https://nah.wikisource.org/',
        'Classical + Modern',
        'Digitized literary/historical texts',
        'Monolingual Nahuatl',
        'Yes (public domain / CC)',
        'Low–Moderate',
        'Transcribed Nahuatl primary sources; smaller than Wikipedia but higher editorial quality',
    ),
    # ── OpenSubtitles / film in Nahuatl ──────────────────────────────────
    (
        'OpenSubtitles.org',
        'Community translators',
        'Nahuatl subtitles (search)',
        'https://www.opensubtitles.org/en/search/sublanguageid-nah',
        'Modern / Mixed',
        'Film subtitles',
        'Monolingual Nahuatl (subtitle files)',
        'Yes',
        'Moderate',
        'Small corpus; modern colloquial register; useful for spoken-language style',
    ),
]

# Write headers (bold, frozen)
ws.update([HEADERS], 'A1')
ws.format('A1:J1', {
    'textFormat': {'bold': True, 'foregroundColorStyle': {'rgbColor': {'red': 1, 'green': 1, 'blue': 1}}},
    'backgroundColorStyle': {'rgbColor': {'red': 0.2, 'green': 0.4, 'blue': 0.7}},
})
ws.freeze(rows=1)

# Write data rows
if ROWS:
    ws.append_rows([list(r) for r in ROWS], value_input_option='RAW')

# Auto-resize columns (approximate widths)
body = {
    'requests': [
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': ws.id,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': len(HEADERS),
                },
                'properties': {'pixelSize': 220},
                'fields': 'pixelSize',
            }
        }
    ]
}
sh.batch_update(body)

print(f'Done — {len(ROWS)} rows written.')
print(f'Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}')
