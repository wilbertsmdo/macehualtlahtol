#!/usr/bin/env /data/data/com.termux/files/usr/bin/python3
"""
Create a Google Doc in Drive folder 15HBoSkLT0dKjlxQquAv9zbmpQxjFaArH
documenting all Cross-Language Morpheme Mapping work for Nahuatl_Translator2.
Uses OAuth token (SA Drive is full).
"""
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

TOKEN_PATH   = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json'
CREDS_PATH   = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/credentials.json'
FOLDER_ID    = '15HBoSkLT0dKjlxQquAv9zbmpQxjFaArH'
SHEET_ID     = '1TYw3gvcSGmCTQEKchEKlNDUm1BOL-i66jfhsNA1og-k'
SHEET_URL    = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit'

# ── Auth ─────────────────────────────────────────────────────────────────────
creds = Credentials.from_authorized_user_file(TOKEN_PATH)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN_PATH, 'w') as f:
        f.write(creds.to_json())
    print("Token refreshed.")

drive_svc = build('drive',  'v3', credentials=creds)
docs_svc  = build('docs',   'v1', credentials=creds)

# ── Create empty document ────────────────────────────────────────────────────
print("Creating Google Doc …")
doc = docs_svc.documents().create(body={
    'title': 'Nahuatl_Translator2 — Cross-Language Morpheme Mapping'
}).execute()
doc_id = doc['documentId']
print(f"  Doc ID: {doc_id}")

# Move to folder
drive_svc.files().update(
    fileId=doc_id,
    addParents=FOLDER_ID,
    removeParents='root',
    fields='id, parents'
).execute()
print(f"  Moved to folder {FOLDER_ID}.")

# ── Document content: list of (text, style) ───────────────────────────────────
# style: TITLE | SUBTITLE | HEADING_1 | HEADING_2 | HEADING_3 | NORMAL_TEXT
CONTENT = [

    ("Nahuatl Translator2 — Cross-Language Morpheme Mapping", "TITLE"),
    ("Session Report · 2026-09-27 · Macehualtlahtol Project", "SUBTITLE"),

    ("1. Project Overview", "HEADING_1"),
    (
        "Goal: Build a systematic cross-language reference that maps English and Spanish "
        "word-formation morphemes (prefixes and suffixes) to their Nahuatl equivalents in "
        "Modern Huasteca Nahuatl (MHN, Chicontepec variety), to serve as the combinatorial "
        "base for systematic neologism creation in Nahuatl.\n\n"
        "The work was motivated by Gruda, Haimovich & Sullivan (2023, Lingua), which shows "
        "that the single most productive technology-neologism pattern in MHN is "
        "tepoz- + verb + -ni (e.g. tepozihcuiloni = printer). This table extends that "
        "finding to all major derivational categories in both European languages and maps "
        "each to its Nahuatl structural equivalent.\n\n"
        "Orthography: All Nahuatl forms use ACK (Andrews-Campbell-Karttunen) classical "
        "orthography: c/qu (not k), hu/uh (not w), tz (not ts). "
        "Nahuatl variety: MHN Chicontepec, Veracruz (Sullivan/IDIEZ 2016).",
        "NORMAL_TEXT"
    ),

    ("2. The Google Sheet", "HEADING_1"),
    ("Sheet URL: " + SHEET_URL, "NORMAL_TEXT"),

    ("2.1 Tab Structure", "HEADING_2"),
    (
        "The spreadsheet (ID: 1TYw3gvcSGmCTQEKchEKlNDUm1BOL-i66jfhsNA1og-k) "
        "lives in Drive folder 'Tlahtolyancuictia' and has five tabs:\n\n"
        "Tab 1 — Morpheme Mapping: 35 data rows, 13 columns (A–M). "
        "The main reference table mapping EN ↔ ES ↔ NAH morphemes.\n\n"
        "Tab 2 — Missing Morphemes: 15 rows. High/Medium/Low priority morphemes "
        "identified as absent from the main table (applicative -lia, instrumental "
        "-tica, reciprocal ne-, locative -can, etc.).\n\n"
        "Tab 3 — References: 21 rows. All source citations with DOI/URL, "
        "color-coded by category (Nahuatl / English / Spanish / Database / This Project).\n\n"
        "Tab 4 — Morpheme DB - ENG: 1,555 rows. Consolidated English derivational "
        "morpheme inventory from MorphyNet ENG + MorphoLEX, merged by morpheme, "
        "one column per source database.\n\n"
        "Tab 5 — Morpheme DB - ESP: 391 rows. Spanish derivational morpheme inventory "
        "from MorphyNet SPA with English equivalents mapped in columns F–H.",
        "NORMAL_TEXT"
    ),

    ("2.2 Morpheme Mapping Tab — Column Structure (A–M)", "HEADING_2"),
    (
        "A: Row number\n"
        "B: Section (NOMINALIZERS / MODIFIERS / DEGREE / RELATIONAL / SCIENTIFIC)\n"
        "C: Category (e.g. 'Agentive — doer/maker/agent')\n"
        "D: EN Morpheme(s) with description\n"
        "E: EN Word Examples\n"
        "F: ES Morpheme(s) with description\n"
        "G: ES Word Examples\n"
        "H: NAH Morpheme(s) in ACK orthography\n"
        "I: NAH Attested Examples — words documented in Karttunen (1992), "
        "Molina (1571), Sullivan/IDIEZ (2016), or Lockhart (2001)\n"
        "J: NAH Neologisms — words coined for this table, not in any current dictionary "
        "(italic, distinguished from attested forms in column I)\n"
        "K: Productivity in MHN (Fully productive / Constructible / Limited)\n"
        "L: Generator Rule (e.g. 'Rule A1: Attach -ni directly to verb stem')\n"
        "M: Lockhart 2001 Notes — delta analysis vs. Nahuatl as Written (Lockhart 2001)",
        "NORMAL_TEXT"
    ),

    ("3. Morpheme Mapping Table — 35 Categories Across 5 Sections", "HEADING_1"),

    ("Section 1 — NOMINALIZERS (Rows 1–8)", "HEADING_2"),
    (
        "Row 1: Agentive -ni / -catl  →  EN -er/-or/-ist  |  ES -dor/-ista\n"
        "  Nahuatl attested: tlahtoani (speaker), tequitini (worker), pohuani (reader)\n\n"
        "Row 2: Instrumental -oni  →  EN -er (tool sense) / -able  |  ES -dor/-ble\n"
        "  Neologisms: tepozpohuani (calculator), tepozihcuiloni (printer)\n\n"
        "Row 3: Patientive -lli/-li  →  EN -ment/-ed result  |  ES -ado/-ado\n"
        "  Attested: chihualli (artifact), ihcuilolli (document), tlahtolli (word/language)\n\n"
        "Row 4: Locative -yan/-loyan  →  EN -ery/-ory (place)  |  ES -ería\n"
        "  Attested: tequitiyan (workplace). Neologisms: poaloyan (accounting office)\n\n"
        "Row 5: Process/Action -liztli  →  EN -tion/-ment/-ing  |  ES -ción/-miento\n"
        "  Attested: tlahtoaliztli (speech act), tequitiliztli (labor), patiliztli (healing)\n\n"
        "Row 6: Abstract quality -yotl  →  EN -ness/-ity/-ism  |  ES -idad/-ismo\n"
        "  Attested: tlacayotl (humanity), neltiyotl (truth), tlahtocayotl (sovereignty)\n\n"
        "Row 7: Collective -yotl/-otl  →  EN -hood/-ship/-ry  |  ES -dad/-ería\n"
        "  Attested: pillotl (nobility), cihuayotl (womanhood), altepeyotl (community)\n\n"
        "Row 8: Diminutive -tzintli/-tontli  →  EN -let/-ling  |  ES -ito/-illo\n"
        "  Attested: nantzin (dear mother), kallton→calton (little house), pilton (small child)",
        "NORMAL_TEXT"
    ),

    ("Section 2 — MODIFIERS / CLASSIFIERS (Rows 9–14)", "HEADING_2"),
    (
        "Row 9:  Augmentative huey-  →  EN macro-/mega-/great  |  ES super-/sobre-\n"
        "Row 10: Relational -yoh/-tik  →  EN -al/-ic/-ous  |  ES -al/-ico/-oso\n"
        "Row 11: Privative/Negative a-  →  EN un-/non-/in-/a-  |  ES des-/in-/sin-\n"
        "Row 12: Causative -tia/-ltia  →  EN -ize/-ify/-en  |  ES -izar/-ificar\n"
        "Row 13: Reflexive mo-  →  EN self-/auto-  |  ES auto-\n"
        "Row 14: Passive/Impersonal -lo-  →  EN passive -ed/-en  |  ES -ado/-ido passive",
        "NORMAL_TEXT"
    ),

    ("Section 3 — DEGREE / QUANTITY (Rows 15–19)", "HEADING_2"),
    (
        "Row 15: Intensifiers (cenca/huey-)  →  EN hyper-/super-/ultra-  |  ES hiper-/super-\n"
        "  Key neologism: cenca miac tominchipoltiliztli (hyper-inflation)\n\n"
        "Row 16: Diminishers (achi/tontli)  →  EN micro-/mini-/hypo-  |  ES micro-/mini-\n"
        "  Attested: achi cualli (somewhat good). Neologisms: tepozton (micro-device)\n\n"
        "Row 17: Numeral multipliers (ce-/ome-/miec-)  →  EN uni-/bi-/multi-  |  ES uni-/bi-/multi-\n"
        "Row 18: Repetitive (oc ce/oc ceppa)  →  EN re-  |  ES re-\n"
        "Row 19: Between/mutual (ceyotl/altepetl-altepetl-)  →  EN inter-/co-  |  ES inter-/co-",
        "NORMAL_TEXT"
    ),

    ("Section 4 — RELATIONAL / STRUCTURAL PREFIXES (Rows 20–24)", "HEADING_2"),
    (
        "Row 20: Pre-/post- (achtopa/zatepan)  →  EN pre-/post-/ex-  |  ES pre-/pos-/ex-\n"
        "Row 21: Super-/sub- (icpac/itlan/tzintli)  →  EN super-/sub-/infra-  |  ES sobre-/sub-/infra-\n"
        "Row 22: Intra-/trans- (nohuian/ipan/otli)  →  EN intra-/trans-  |  ES intra-/trans-\n"
        "Row 23: Anti-/counter- (a-/yaotl-)  →  EN anti-/counter-  |  ES anti-/contra-\n"
        "Row 24: Study of (iximatiliztli)  →  EN -logy/-ology  |  ES -logía\n"
        "  Neologisms: tla-tlalticpac-iximatiliztli (geology), tla-tomin-iximatiliztli (economics)",
        "NORMAL_TEXT"
    ),

    ("Section 5 — SCIENTIFIC / TECHNICAL STEMS (Rows 25–35)", "HEADING_2"),
    (
        "Row 25: Practitioner (-iximatini)  →  EN -logist/-ician  |  ES -ólogo/-ista\n"
        "Row 26: Measurement (-tlapohualiztli / tepoz-...-pohuani)  →  EN -meter/-graph  |  ES -metro/-grafo\n"
        "Row 27: Disease/inflammation (-cocolyotl)  →  EN -itis/-osis/-pathy  |  ES -itis/-osis\n"
        "Row 28: Surgical removal (-tequiliztli)  →  EN -ectomy/-tomy  |  ES -ectomía/-tomía\n"
        "Row 29: Writing/recording (-ihcuiliztli)  →  EN -graphy/-gram  |  ES -grafía/-grama\n"
        "  Neologism: tonatiuh-ixihcuiloliztli (photography — sun-face-inscription)\n\n"
        "Row 30: Viewing (-ittoni / tepoz-...-ittoni)  →  EN -scope  |  ES -scopio\n"
        "  Neologisms: tepoz-hueka-ittoni (telescope), tepoz-chicopil-ittoni (microscope)\n\n"
        "Row 31: Fear (-mauhcayotl)  →  EN -phobia  |  ES -fobia\n"
        "  Neologisms: tlacatecolotcayotl (xenophobia), ixtlahuatl-mauhcayotl (agoraphobia)\n\n"
        "Row 32: Love/affinity (-tlazohtlaliztli)  →  EN -philia  |  ES -filia\n"
        "Row 33: Government by (-tlahtocayotl)  →  EN -cracy/-archy  |  ES -cracia/-arquía\n"
        "  Attested: macehual-tlahtocayotl (democracy — in use in modern Nahuatl discourse)\n\n"
        "Row 34: Many/multiple (miec-/miac-)  →  EN poly-/multi-/pluri-  |  ES poli-/multi-/pluri-\n"
        "Row 35: Self (mo-/noma-)  →  EN auto-/self-  |  ES auto-",
        "NORMAL_TEXT"
    ),

    ("4. ACK Orthography Standardization", "HEADING_1"),

    ("4.1 ACK Rules Applied", "HEADING_2"),
    (
        "ACK = Andrews-Campbell-Karttunen classical Nahuatl orthography. "
        "The original morpheme_mapping_table.md was written in IDIEZ/SEP modern orthography "
        "(k, w, ts, s). All content was converted to ACK via the script apply_ack_spelling.py.\n\n"
        "Key conversion rules:\n"
        "  ts → tz  (e.g. -tsintli → -tzintli)\n"
        "  k before a/o/u → c  (e.g. tlahtoka → tlahtoca)\n"
        "  k before e/i → qu  (e.g. teki → tequi)\n"
        "  k final/before consonant → c  (e.g. neltik → neltic, miek → miec)\n"
        "  w before vowel → hu  (e.g. siuatl → cihuatl)\n"
        "  vowel + w → vowel + uh  (coda position)\n"
        "  se- (numeral ONE morpheme) → ce-\n"
        "  IDIEZ/SEP label → ACK label in notes",
        "NORMAL_TEXT"
    ),

    ("4.2 Content Errors Fixed (Beyond Orthography)", "HEADING_2"),
    (
        "tikatl/tikayotl → tlacatl/tlacayotl  "
        "(tikatl is not Nahuatl for 'person'; correct word is tlacatl)\n"
        "siuatl/siuayotl → cihuatl/cihuayotl  (ACK form of 'woman')\n"
        "pilyotl → pillotl  (Lockhart allomorph rule: -otl after consonant-final stems)\n"
        "ihkuilo → ihcuilo  (k before u → c)\n"
        "tlaltikpak → tlalticpac  (classical ACK form; missed in initial pass)\n"
        "ichpak → icpac  (classical ACK relational noun 'above/on top')\n"
        "tlacatekolotkayotl → tlacatecolotcayotl  "
        "(base: tlacatecolotl 'devil'; stem tlacatecolot- + -cayotl)\n"
        "mauhkayotl → mauhcayotl  (final k → c)\n"
        "posotik → pozotic  (s → z; final k → c)\n"
        "cualtik → cualtic  (final k → c; parallel to neltic)\n"
        "yollizcocolyotl → yollotcocolyotl  (correct stem: yollotl 'heart')",
        "NORMAL_TEXT"
    ),

    ("5. Attested vs. Neologisms — Column I Split", "HEADING_1"),
    (
        "Column I (originally 'NAH Word Examples') was split into two columns:\n\n"
        "Column I — NAH Attested Examples: Words documented in Karttunen (1992), "
        "Molina (1571), Sullivan/IDIEZ (2016), or Lockhart (2001). "
        "Examples: tlahtoani, tlahtolli, tequitiliztli, mauhcayotl, achi cualli.\n\n"
        "Column J — NAH Neologisms (italic): Words coined for this table, not in any "
        "current Nahuatl dictionary. These are productive rule-based constructions. "
        "Examples: cenca miac tominchipoltiliztli (hyper-inflation), "
        "tepozpohuani (calculator), tla-tlalticpac-iximatiliztli (geology), "
        "mo-tlahtoca-liztli (autonomy/self-governance).\n\n"
        "The distinction is linguistically critical: attested forms can be used directly; "
        "neologisms require validation against native speaker intuition and existing "
        "documentation before deployment.",
        "NORMAL_TEXT"
    ),

    ("6. Lockhart 2001 Delta Analysis", "HEADING_1"),
    (
        "Source: Lockhart, J. (2001). Nahuatl as Written: Lessons in Older Written "
        "Nahuatl, with Copious Examples and Texts. Stanford / UCLA.\n\n"
        "The script add_lockhart_column.py added column L ('Lockhart 2001 Notes') to the "
        "Morpheme Mapping sheet. Each of the 35 rows was tagged with one of four delta types:\n\n"
        "  NEW_EXAMPLES — Lockhart provides additional word examples not in the table\n"
        "  DISCREPANCY — Lockhart's description differs from the table (e.g. allomorph rules)\n"
        "  PRODUCTIVITY_NOTE — Lockhart comments on frequency/register\n"
        "  NOT ADDRESSED — Lockhart's lessons do not cover this morpheme category\n\n"
        "A second tab 'Missing Morphemes' was added with 15 high/medium/low priority "
        "morphemes absent from the 35-row table:\n"
        "  HIGH: Applicative -lia, Instrumental -tica/-ica, Reciprocal ne-, "
        "Locative -can, Absolutive suffix-drop rules\n"
        "  MEDIUM: Directional on-/hualla-, Honorific -tzino-, Distributive reduplication, "
        "Plural -meh agreement, Possessed noun -uh\n"
        "  LOW: -pol (augmentative-pejorative), -yoh possessive adjective (distinct use), "
        "Numeral -po (×20), -pa (directional/times)",
        "NORMAL_TEXT"
    ),

    ("7. Database Integration", "HEADING_1"),

    ("7.1 MorphyNet (Batsuren et al. 2021)", "HEADING_2"),
    (
        "Reference: Batsuren, K., Bella, G., & Giunchiglia, F. (2021). MorphyNet: "
        "a large multilingual database of derivational and inflectional morphology. "
        "Proceedings of the 18th SIGMORPHON Workshop. ACL Anthology.\n"
        "URL: https://github.com/kbatsuren/MorphyNet\n"
        "License: Open.\n\n"
        "Data downloaded:\n"
        "  eng/eng.derivational.v1.tsv — 225,131 English derivation pairs\n"
        "  spa/spa.derivational.v1.tsv — 30,777 Spanish derivation pairs\n\n"
        "Format: source_word, target_word, source_pos, target_pos, morpheme, type\n"
        "Example: sense → nonsense, N, N, non, prefix\n\n"
        "Usage: Morphemes extracted with pair count as productivity proxy. "
        "Top English morphemes: -ation (2,345 pairs), -er (1,890), -al (1,654), "
        "un- (1,432), re- (1,389). "
        "Top Spanish: -mente (2,928 pairs), -dor (1,314), -ar (1,296), "
        "-ero (1,121), -miento (912).",
        "NORMAL_TEXT"
    ),

    ("7.2 MorphoLEX (Sánchez-Gutiérrez et al. 2018)", "HEADING_2"),
    (
        "Reference: Sánchez-Gutiérrez, C.H., Mailhot, H., Deacon, S.H., & Wilson, M.A. "
        "(2018). MorphoLEX: A derivational morphological database for 70,000 English words. "
        "Behavior Research Methods, 50(4), 1568–1580. doi:10.3758/s13428-017-0981-8\n"
        "URL: https://github.com/hugomailhot/MorphoLex-en\n"
        "File: MorphoLEX_en.xlsx (34 sheets, ~70,000 English words)\n"
        "License: Open.\n\n"
        "Key metrics used:\n"
        "  family_size — number of words sharing the morpheme (productivity proxy)\n"
        "  HAL_freq — corpus frequency in HAL (Hyperspace Analogue to Language corpus)\n\n"
        "Top English prefixes by family size: un- (1,247 words), re- (856), "
        "in- (734), over- (612), pre- (489).\n"
        "Top English suffixes: -ly (2,486 words), -er (1,890), -ion (1,654), "
        "-al (1,432), -ous (1,312).\n\n"
        "Note: MorphoLEX is English-only. No equivalent Spanish morpheme frequency "
        "database of this quality currently exists as an open resource.",
        "NORMAL_TEXT"
    ),

    ("7.3 CELEX2 (Baayen, Piepenbrock & Gulikers 1995)", "HEADING_2"),
    (
        "Reference: Baayen, R.H., Piepenbrock, R., & Gulikers, L. (1995). "
        "CELEX2: The CELEX Lexical Database (Release 2). "
        "Linguistic Data Consortium, Philadelphia. LDC Catalog No. LDC96L14.\n"
        "URL: https://catalog.ldc.upenn.edu/LDC96L14\n\n"
        "Status: REQUIRES LDC LICENSE — not freely downloadable. "
        "Not used in this project. MorphoLEX (derived from CELEX) used as open alternative.",
        "NORMAL_TEXT"
    ),

    ("7.4 Morpheme DB Tabs — Structure", "HEADING_2"),
    (
        "Morpheme DB - ENG (1,555 rows):\n"
        "  Unique English morphemes merged from MorphyNet ENG + MorphoLEX.\n"
        "  185 morphemes confirmed in BOTH databases ('⬤ both', green highlight).\n"
        "  1,300 MorphyNet-only; 70 MorphoLEX-only.\n"
        "  Columns: # | Type | Morpheme | MorphyNet ENG (pair count) | "
        "MorphoLEX (family size) | MorphoLEX (HAL freq) | Example Words | "
        "In Morpheme Mapping Table? | Notes\n\n"
        "Morpheme DB - ESP (391 rows):\n"
        "  Spanish morphemes from MorphyNet SPA with English equivalents.\n"
        "  83 of 391 mapped to English equivalents.\n"
        "  Columns: # | Type | Morpheme (SPA) | MorphyNet SPA (pair count) | "
        "Example Words (SPA) | ENG Equivalent(s) | ENG MorphyNet (count) | "
        "ENG MorphoLEX (family size) | In Table? | SPA↔ENG Relationship",
        "NORMAL_TEXT"
    ),

    ("8. Scripts Created", "HEADING_1"),
    (
        "All scripts in: "
        "/storage/self/primary/PY_Projects/Macehualtlahtol/Nahuatl_Translator2/\n\n"
        "create_morpheme_sheet.py\n"
        "  Parses morpheme_mapping_table.md and writes 35-row table to Google Sheet. "
        "Applies color-coded section formatting, monospace morpheme columns, frozen header.\n\n"
        "add_lockhart_column.py\n"
        "  Adds column L (Lockhart 2001 Notes) with delta tags for all 35 rows, "
        "and creates the 'Missing Morphemes' tab with 15 priority-ranked absent morphemes.\n\n"
        "apply_ack_spelling.py\n"
        "  Applies 35+ ordered string replacements to standardize all Nahuatl content "
        "in the sheet (all 12 columns, 36 rows) and in morpheme_mapping_table.md "
        "from IDIEZ/SEP modern orthography to ACK classical orthography. "
        "74 cells updated.\n\n"
        "split_nah_examples_column.py\n"
        "  Inserts new column J after column I. Splits NAH Word Examples into: "
        "I = NAH Attested Examples (dictionary-documented), "
        "J = NAH Neologisms (coined for this table). "
        "Hardcoded classification for all 35 rows based on Karttunen/Molina/Lockhart.\n\n"
        "fix_ack_columns_ij.py\n"
        "  Corrects 11 ACK spelling errors found in the newly split columns I and J "
        "(kalkan→calcan, kallton→calton, posotik→pozotic, cualtik→cualtic, "
        "ichpak→icpac, tlaltikpak→tlalticpac, tlacatekolot→tlacatecolot, etc.).\n\n"
        "add_references_tab.py\n"
        "  Creates the 'References' tab with 21 entries: Nahuatl dictionaries, "
        "word-formation textbooks, databases. Color-coded by category.\n\n"
        "fetch_morpheme_db.py\n"
        "  Downloads MorphyNet ENG/SPA and MorphoLEX. Extracts top morphemes. "
        "Writes to 'Morpheme DB' tab (later replaced by rebuild_morpheme_db.py).\n\n"
        "rebuild_morpheme_db.py\n"
        "  Consolidates MorphyNet ENG + MorphoLEX into 'Morpheme DB - ENG' (1,555 rows), "
        "MorphyNet SPA into 'Morpheme DB - ESP' (391 rows). "
        "Deletes old 'Morpheme DB' tab.\n\n"
        "update_esp_eng_mapping.py\n"
        "  Rebuilds 'Morpheme DB - ESP' with SPA→ENG morpheme equivalence mapping "
        "(83 Spanish morphemes mapped). Adds ENG Equivalent, ENG MorphyNet count, "
        "and ENG MorphoLEX family size columns for cross-language comparison.",
        "NORMAL_TEXT"
    ),

    ("9. Open Gaps & Next Steps", "HEADING_1"),

    ("9.1 Missing High-Priority Morphemes in the Mapping Table", "HEADING_2"),
    (
        "The following productive morphemes are NOT yet in the 35-row table. "
        "Priority ranked by frequency in FT/NYT-register English text:\n\n"
        "HIGH PRIORITY:\n"
        "  semi-/hemi- (half)  →  NAH: tlahco- (half, classical)\n"
        "  neo-/nuevo- (new form of X)  →  NAH: yancuic- (new/novel)\n"
        "  pseudo-/falso- (false/apparent)  →  NAH: tlapic- (invented/false)\n"
        "  mal-/mis- (badly/wrongly done)  →  NAH: ahmo cualli + verb stem\n"
        "  pro- (in favor of)  →  NAH: ipampa- / itech monequi (for the sake of)\n\n"
        "MEDIUM PRIORITY:\n"
        "  macro- (large-scale; distinct from huey- which is physical size)\n"
        "  -ee/-ado (recipient of action, distinct from agent -ni)\n"
        "  vice-/sub- (deputy/in place of)\n"
        "  -ward/-wise (directional/manner; no direct NAH equivalent)\n\n"
        "From the Missing Morphemes tab:\n"
        "  Applicative -lia (HIGH): 'to do X for/to someone' — critical for transitive neologisms\n"
        "  Instrumental -tica/-ica (HIGH): 'by means of X'\n"
        "  Reciprocal ne- (HIGH): mutual action\n"
        "  Locative -can (HIGH): distinct from -yan (place of doing → place characterized by)",
        "NORMAL_TEXT"
    ),

    ("9.2 Spanish Morpheme Database Gap", "HEADING_2"),
    (
        "MorphoLEX is English-only. The Spanish section (Morpheme DB - ESP) "
        "has only MorphyNet SPA data, without family-size or frequency metrics.\n\n"
        "Possible solutions:\n"
        "  a) CORPES XXI (RAE corpus, 400M words): morpheme frequency analysis. "
        "Requires API access or corpus download.\n"
        "  b) DerivBase.es or similar Spanish morphological DB (less established).\n"
        "  c) Manual frequency count from a Spanish frequency dictionary "
        "(e.g. Almela Pérez 2005 or Davies 2006 corpus).",
        "NORMAL_TEXT"
    ),

    ("9.3 Unmapped Spanish Morphemes", "HEADING_2"),
    (
        "308 of 391 Spanish morphemes in the ESP tab lack an English equivalent mapping. "
        "Most are:\n"
        "  Demonym/regional suffixes: -eño, -ense, -ero (place-specific), -ano\n"
        "  Verbal paradigm endings (not derivational): -aba, -ara, -ría\n"
        "  Low-frequency morphemes (count < 10 pairs in MorphyNet)\n"
        "  Archaic or domain-specific: -azgo, -ía (title), -ato\n"
        "The SPA_TO_ENG mapping in update_esp_eng_mapping.py can be extended "
        "to cover additional morphemes as needed.",
        "NORMAL_TEXT"
    ),

    ("9.4 Remaining Project Tasks (Nahuatl_Translator2 Broader)", "HEADING_2"),
    (
        "Human review of 2,767 NLLB D5 eval delta rows (still pending)\n"
        "D6 fine-tune (depends on human review completion)\n"
        "IDIEZ neologism repository — JSON file of documented Nahuatl coinages\n"
        "Target concept list — 200-300 FT/NYT-register terms for neologism generation\n"
        "Validate NAH Neologisms (column J) with native speaker / IDIEZ researcher",
        "NORMAL_TEXT"
    ),

    ("10. References", "HEADING_1"),

    ("10.1 Nahuatl Sources", "HEADING_2"),
    (
        "Molina, A. de (1571). Vocabulario en Lengua Castellana y Mexicana. "
        "Antonio de Spinosa, Mexico City. [Facsimile: Porrúa 1970.]\n\n"
        "Karttunen, F. (1992). An Analytical Dictionary of Nahuatl. "
        "University of Oklahoma Press. ISBN 978-0-8061-2421-6.\n\n"
        "Andrews, J.R. (2003). Introduction to Classical Nahuatl (rev. ed.). "
        "University of Oklahoma Press. ISBN 978-0-8061-3452-9.\n\n"
        "Lockhart, J. (2001). Nahuatl as Written: Lessons in Older Written Nahuatl. "
        "Stanford University Press / UCLA Latin American Center. ISBN 978-0-8047-4282-4.\n\n"
        "Sullivan, J. & IDIEZ team (2016). Nahuatl Dictionary (Modern Huasteca Nahuatl). "
        "IDIEZ / Universidad Veracruzana, Chicontepec, Veracruz.\n\n"
        "Siméon, R. (1885). Dictionnaire de la Langue Nahuatl ou Mexicaine. "
        "Imprimerie Nationale, Paris.",
        "NORMAL_TEXT"
    ),

    ("10.2 Neologism & Word-Formation Research", "HEADING_2"),
    (
        "Gruda, M., Haimovich, L., & Sullivan, J. (2023). Lexical creativity in modern "
        "Nahuatl: On the interplay between internal and external factors. "
        "Lingua, 295, 103607. doi:10.1016/j.lingua.2023.103607\n\n"
        "Štekauer, P. (2005). Meaning Predictability in Word Formation: Novel, "
        "Context-Free Naming Units. John Benjamins, Amsterdam. ISBN 978-90-272-2370-2.\n\n"
        "Plag, I. (2003). Word-Formation in English. Cambridge University Press. "
        "ISBN 978-0-521-52563-7.\n\n"
        "Bauer, L. (1983). English Word-Formation. Cambridge University Press. "
        "ISBN 978-0-521-28492-1.\n\n"
        "Lang, M.F. (1990). Spanish Word Formation. Routledge, London. "
        "ISBN 978-0-415-05053-0.\n\n"
        "Real Academia Española (2009). Nueva gramática de la lengua española, "
        "Vol. 1: Morfología. Espasa-Calpe, Madrid.",
        "NORMAL_TEXT"
    ),

    ("10.3 Morpheme Databases", "HEADING_2"),
    (
        "Batsuren, K., Bella, G., & Giunchiglia, F. (2021). MorphyNet: a large multilingual "
        "database of derivational and inflectional morphology. Proceedings of the 18th "
        "SIGMORPHON Workshop. ACL Anthology. doi:10.18653/v1/2021.sigmorphon-1.5. "
        "URL: https://github.com/kbatsuren/MorphyNet\n\n"
        "Sánchez-Gutiérrez, C.H., Mailhot, H., Deacon, S.H., & Wilson, M.A. (2018). "
        "MorphoLEX: A derivational morphological database for 70,000 English words. "
        "Behavior Research Methods, 50(4), 1568–1580. doi:10.3758/s13428-017-0981-8. "
        "URL: https://github.com/hugomailhot/MorphoLex-en\n\n"
        "Baayen, R.H., Piepenbrock, R., & Gulikers, L. (1995). CELEX2: The CELEX Lexical "
        "Database (Release 2). Linguistic Data Consortium. LDC96L14. "
        "URL: https://catalog.ldc.upenn.edu/LDC96L14 [Requires LDC license]",
        "NORMAL_TEXT"
    ),

]

# ── Build Docs API batchUpdate requests ───────────────────────────────────────
print("Building document content …")

requests_list = []
idx = 1  # Docs body starts at index 1

for text, style in CONTENT:
    text_nl = text + '\n'
    end_idx = idx + len(text_nl)

    # Insert text
    requests_list.append({
        'insertText': {
            'location': {'index': idx},
            'text': text_nl,
        }
    })

    # Apply paragraph style
    requests_list.append({
        'updateParagraphStyle': {
            'range': {'startIndex': idx, 'endIndex': end_idx},
            'paragraphStyle': {'namedStyleType': style},
            'fields': 'namedStyleType',
        }
    })

    idx = end_idx

print(f"  {len(CONTENT)} paragraphs, {idx} total characters, {len(requests_list)} requests")

# ── Execute in batches of 100 requests ───────────────────────────────────────
BATCH = 100
for start in range(0, len(requests_list), BATCH):
    batch = requests_list[start:start+BATCH]
    docs_svc.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': batch}
    ).execute()
    print(f"  Sent requests {start}–{start+len(batch)-1}")

doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
print(f"\nDone!")
print(f"Document URL: {doc_url}")
