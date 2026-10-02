#!/usr/bin/env /data/data/com.termux/files/usr/bin/python3
"""
Split column I (NAH Word Examples) into two columns:
  I: NAH Attested Examples  — words documented in Karttunen 1992, Molina 1571,
                               Sullivan/IDIEZ 2016, Lockhart 2001
  J: NAH Neologisms         — words coined for this table (not in any current dictionary)
Inserts a new column after I, then writes classified content row by row.
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
ws         = sh.get_worksheet(0)
sid        = ws.id

# ── Classified content: (attested, neologisms) per data row 1–35 ─────────────
# Attested = documented in Karttunen (1992), Molina (1571), Sullivan/IDIEZ (2016),
#            Lockhart (2001), or modern MHN political discourse.
# Neologisms = coined forms not found in any current Nahuatl dictionary.

ROWS = {
    1: (
        "tlahtoani (speaker/ruler — Karttunen, Molina)\n"
        "tequitini (worker — documented)\n"
        "pohuani (reader/counter — documented)\n"
        "mexicatl (-catl demonym suffix — classical)",
        ""
    ),
    2: (
        "-oni suffix (potential/instrumental — Karttunen)\n"
        "ittaoni (something seeable — derivable, documented pattern)\n"
        "ihcuiloni (something writable — documented in colonial texts)",
        "tepozpohuani (metal-counter → calculator)\n"
        "tepozihcuiloni (metal-writing-thing → printer/typewriter)"
    ),
    3: (
        "chihualli (thing made / artifact — Karttunen)\n"
        "tequili (something cut / quota — documented)\n"
        "ihcuilolli (something written / text / document — Karttunen)\n"
        "poalli (something counted / tally — documented)\n"
        "tlahtolli (something spoken / word / language — Molina, Karttunen)",
        ""
    ),
    4: (
        "tequitiyan (workplace — attested in colonial texts)\n"
        "kalkan (near/at the house — classical relational)",
        "tequiyan (cutting room — coined)\n"
        "tamalchihuayan (tortillería / where tamales are made — coined institutional sense)\n"
        "poaloyan (accounting office — coined)\n"
        "tlamaloyan (storage area — coined modern application)"
    ),
    5: (
        "tlahtoaliztli (speaking / speech act — Karttunen)\n"
        "tequitiliztli (working / labor — documented)\n"
        "pohualiztli (reading / counting / the act of reading — documented)\n"
        "matiliztli (knowing / knowledge as process — Karttunen)\n"
        "patiliztli (healing / the process of healing — documented)",
        "iximatiliztli (deep expertise as process — coined compound)"
    ),
    6: (
        "tlacayotl (personhood / humanity — Karttunen)\n"
        "neltiyotl (truth / truthfulness — documented)\n"
        "tlahtocayotl (sovereignty / the quality of ruling — Karttunen)\n"
        "cualliyotl (goodness / quality — documented)\n"
        "totoncayotl (heat / hotness as abstract property — Sullivan)",
        "tlahtoayotl (speech-essence / language-identity — coined compound)"
    ),
    7: (
        "pillotl (nobility / collective of nobles — Lockhart)\n"
        "cihuayotl (womanhood / women as collective identity — documented)\n"
        "altepeyotl (community identity / collective citizenship — documented)",
        "tequitinimeh (worker collective — coined compound phrase)"
    ),
    8: (
        "nantzin (dear mother / respected mother — classical)\n"
        "totoltzintli (the dear little bird / reverential small — classical)\n"
        "tlahtotzintli (the honored word / reverential speech — classical)\n"
        "kallton (little house / shack — Karttunen)\n"
        "pilton (small child / urchin — documented)",
        ""
    ),
    9: (
        "huey altepetl (great city / metropolis — classical set phrase)\n"
        "miac (many/much — classical quantifier)",
        "huey tequitiyan (great institution / large workplace — coined)\n"
        "huey tlahtocayotl (empire / great sovereignty — coined modern application)"
    ),
    10: (
        "teyoh (stony / stone-like — Karttunen)\n"
        "xochiyoh (flowery / of flower quality — documented)\n"
        "posotik (foamy / bubbly — Sullivan IDIEZ)\n"
        "cualtik (well-made / good-quality adjective — documented)",
        "tonalenyo (pertaining to the sun — coined)\n"
        "altepeile (one pertaining to the city — coined)\n"
        "tequi-yotl used adjectivally in phrase (coined usage)"
    ),
    11: (
        "a-cualli (not-good / bad / harmful — Karttunen)\n"
        "ahmo (clausal negation particle — classical)",
        "a-chica (without firmness / unstable — coined)\n"
        "a-neltic (untruthful / not-true — coined compound)\n"
        "a-tonal (without sun / sunless — coined)\n"
        "a-matiliztli (not-knowing / ignorance — coined)"
    ),
    12: (
        "cualtia (to make good / to improve — Karttunen)\n"
        "neltiltia (to make true / to confirm / validate — documented)\n"
        "chicaltia (to make firm / to strengthen — documented)\n"
        "machtia (to make know / to teach — classical)\n"
        "maltia (to bathe — classical causative)\n"
        "poaltia (to cause to count / to report — documented)",
        "cualtializtli (quality improvement as process — coined compound)"
    ),
    13: (
        "ni-mo-chihua (I make myself / I am done — classical)\n"
        "mo-tlahtoa (speaks to themselves / reflexive speech — classical)\n"
        "mo-machtia (self-educates — classical)\n"
        "momachtiani (student / one who self-teaches — classical)",
        "mo-tequitiyan (autonomous workspace — coined)\n"
        "motlahtokiliztli (self-governance / autonomy — coined)"
    ),
    14: (
        "tla-chihua-lo (things are made / impersonal passive — classical)\n"
        "tla-tequi-lo (things are cut — classical)\n"
        "tla-tlahtoa-lo (things are spoken of / it is discussed — classical)",
        "tla-tequi-lo-yan (workshop via passive+locative — coined)\n"
        "tla-poa-lo-liztli (the being-counted / accounting process — coined)"
    ),
    15: (
        "cenca (very / truly — classical intensifying adverb)\n"
        "huey (great/big — classical degree word)\n"
        "miac / miec (many/much — classical quantifier)",
        "cenca miac tominchipoltiliztli (hyper-inflation: very-much money-erosion-process — coined)\n"
        "huey tlapachiuhyotl (great-pressure / over-pressure — coined)"
    ),
    16: (
        "achi miac (a little much / somewhat many — classical phrase)\n"
        "achi cualli (somewhat good / sub-optimal — classical phrase)\n"
        "-tontli / -ton (diminutive suffix — classical)\n"
        "-tzintli (reverential diminutive — classical)",
        "tepozton (little machine / micro-device — coined)\n"
        "tequitiyanton (little workplace / micro-enterprise — coined)\n"
        "tequiyantsin (small workspace — respectful register, coined)"
    ),
    17: (
        "ce-, ome-, yei-, nahui-, macuil- (classical cardinal numerals)\n"
        "miec- / miac- (many — classical quantifier prefix)",
        "ome-altepetl-tlahtocaliztli (two-nation governing / bilateral governance — coined)\n"
        "miec-altepetl-monemitiyotl (many-nation living-quality / multilateral order — coined)"
    ),
    18: (
        "oc ce mochiua (it happens again / it is redone — classical phrase)\n"
        "oc ceppa (once more / again — classical adverb)\n"
        "on- (directional prefix — classical)",
        "oc ce tlahtoa (one speaks again / re-negotiates — coined application)\n"
        "oc ceppa tlapoa (one counts again / re-audits — coined application)"
    ),
    19: (
        "ceyotl (unity / oneness / convergence — documented)\n"
        "ceyolia (to unite / to make one — documented)",
        "nohuentlahtocaliztli (mutual governing / co-governance — coined)\n"
        "altepetlahzohtlalisyotl (inter-national love-quality — coined)\n"
        "altepetl-altepetl-tlahtocaliztli (nation-nation governing / international governance — coined)\n"
        "ceyoliztli (unification / cooperation as process — coined)"
    ),
    20: (
        "achtopa (before / prior — classical adverb)\n"
        "zatepan / niman (afterward / after — classical adverbs)",
        "achtopa tlahtocayotl (prior sovereignty / pre-governance period — coined)\n"
        "achtopa tlahtocani (former ruler / ex-president — coined)\n"
        "zatepan tlahtocayotl (post-governance era — coined)\n"
        "zatepan tlapalowalistli (post-pandemic process — coined)"
    ),
    21: (
        "ichpak (above — classical relational noun)\n"
        "itlan / tlantli (below / under — classical relational)\n"
        "itzinco / tzintli (base/foundation — classical body-part root)\n"
        "ixpan (in front of / over-facing — classical relational)",
        "ichpak tlamaniliztli (above-placing / superstructure — coined)\n"
        "itlan-tlamaniliztli (under-structure / infrastructure — coined)\n"
        "tzintlamaniliztli (base-structure / fundamental structure — coined)\n"
        "ixpan tlahtocayotl (above-governance / supranational authority — coined)"
    ),
    22: (
        "nohuian (everywhere / throughout — classical adverb)",
        "altepetl-ipan-yotl (within-nation-quality / intra-national — coined)\n"
        "altepetl-otli-tlahtocaliztli (cross-border governance — coined)"
    ),
    23: (
        "a- (privative prefix — classical)\n"
        "yaotl (enemy / war — classical noun)",
        "yaotl-tlahtocaliztli (war-governance / counter-strategy — coined)\n"
        "a-tlahzolchihualiztli (anti-corruption / without-dirt-making-process — coined)\n"
        "a-tlahzol-yotl (anti-corruption orientation — coined)\n"
        "a-yaoyotl (anti-war / pacifism: without-war-quality — coined)"
    ),
    24: (
        "iximati (to know deeply / to recognize — Karttunen)",
        "tla-tlaltikpak-iximatiliztli (deep-knowing of the earth / geology — coined)\n"
        "tla-yoliliztli-iximatiliztli (deep-knowing of life / biology — coined)\n"
        "tla-tomin-iximatiliztli (deep-knowing of money / economics — coined)\n"
        "tla-nemilistli-iximatiliztli (deep-knowing of society / sociology — coined)\n"
        "tla-tonatiuh-iximatiliztli (deep-knowing of the sun / astronomy — coined)"
    ),
    25: (
        "momachtiani (student / one who self-teaches — classical)",
        "tla-tlaltikpak-iximatini (deep-knower of the earth / geologist — coined)\n"
        "tla-tomin-iximatini (deep-knower of money / economist — coined)\n"
        "tla-altepetl-tlahtocaliztli-iximatini (deep-knower of governance / political scientist — coined)\n"
        "tla-yoliliztli-iximatini (biologist — coined)\n"
        "tomin-matini (money-knower / economist colloquial — coined)"
    ),
    26: (
        "",
        "tlapalachtli-tlapohualiztli (measuring of pressure / barometry — coined)\n"
        "totoncayotl-tlapohualiztli (measuring of heat / thermometry — coined)\n"
        "tepoz-totoncayotl-pohuani (metal-heat-counter / thermometer — coined)\n"
        "tepoz-tlapalachtli-pohuani (metal-pressure-counter / barometer — coined)"
    ),
    27: (
        "cocolyotl (sickness / disease — Karttunen)\n"
        "cocoa (to hurt / to be sick — classical verb)",
        "momaxtilanococolyotl (joint-sickness / arthritis concept — coined)\n"
        "eztli-cocolyotl (blood-sickness / anemia concept — coined)\n"
        "momaxtilanoh-cocoa-liztli (joint-hurting-process / arthritis — coined)\n"
        "yollizcocolyotl (heart-disease-quality / cardiac pathology — coined)"
    ),
    28: (
        "tequi (to cut — classical verb)\n"
        "nacatl (flesh / meat — classical noun)",
        "iyiyo-tequiliztli (lung-cutting / pneumonectomy — coined)\n"
        "yollotli-tequiliztli (heart-cutting / cardiotomy — coined)\n"
        "nacatl-tequiliztli (flesh-cutting / surgery in general — coined)\n"
        "nacatepoztequililiztli (metal-flesh-cutting / surgery — coined)"
    ),
    29: (
        "ihcuilolli (something written / text / document — Karttunen)\n"
        "ihcuiloa (to write / to inscribe — classical verb)",
        "tonatiuh-ixihcuiloliztli (sun-face-recording / photography — coined)\n"
        "nemilistli-ihcuiliztli (life-writing / biography — coined)\n"
        "tepoz-ihcuiliztli (metal-writing / digital recording / printing — coined)\n"
        "tlapalihcuilolli (color-written-thing / photograph — coined)"
    ),
    30: (
        "itta (to see — classical verb)\n"
        "ittoni (something that can be seen — documented pattern)",
        "hueka-ittaliztli (far-seeing / telescopy process — coined)\n"
        "chicopil-ittaliztli (tiny-thing-seeing / microscopy — coined)\n"
        "tepoz-hueka-ittoni (metal far-viewer / telescope — coined)\n"
        "tepoz-chicopil-ittoni (metal tiny-thing-viewer / microscope — coined)\n"
        "tepoz-itic-ittoni (metal inner-viewer / endoscope — coined)"
    ),
    31: (
        "mauhcayotl / mauhkayotl (fear-quality — Karttunen)\n"
        "temauhti (something frightful — documented)",
        "tlacatekolotkayotl (stranger/outsider-fear / xenophobia — coined)\n"
        "ixtlahuatl-mauhkayotl (open-space-fear / agoraphobia — coined)\n"
        "coyotlahtolli-mauhkayotl (foreign-language fear — coined)"
    ),
    32: (
        "tlazohtla (to love — classical verb)\n"
        "tlazohtlaliztli (the act of loving — documented)",
        "amox-tlazohtlaliztli (book-loving / bibliophilia — coined)\n"
        "amox-tlazohtlani (book-lover / bibliophile — coined)\n"
        "tlaltikpak-tlazohtlani (earth-lover / ecophile / environmentalist — coined)"
    ),
    33: (
        "macehual-tlahtocayotl (commoner-governing / democracy — attested in modern Nahuatl political discourse)",
        "tomin-tlahtocayotl (money-governing / plutocracy — coined)\n"
        "pilli-tlahtocayotl (noble-governing / aristocracy — coined)\n"
        "mochiuhtiani-tlahtocayotl (functionary-governing / bureaucracy — coined)\n"
        "ome-tlahtocan-tlahtocayotl (two-ruler-governing / diarchy — coined)"
    ),
    34: (
        "miec- / miac- (many — classical quantifier prefix)\n"
        "nohuian (everywhere / all-around — classical adverb)",
        "miec-altepetl-tlahtocaliztli (many-nation-governing / multilateral governance — coined)\n"
        "miec-tlahtol-yotl (many-language-quality / multilingualism — coined)\n"
        "miec-tlacayotl (many-people-quality / pluralism — coined)\n"
        "nohuian-tlahtocayotl (everywhere-governing / pan-governance — coined)"
    ),
    35: (
        "mo- (reflexive prefix — classical)\n"
        "noma / nomahtia (by oneself / with one's own hand — classical)",
        "mo-tlahtoca-liztli (self-governing / autonomy — coined)\n"
        "mo-tequiti-liztli (self-working / self-management — coined)\n"
        "mo-palehui-liztli (self-helping / self-sufficiency — coined)\n"
        "mo-chihua-liztli (self-making / automation — coined)\n"
        "noma-tequiti-liztli (own-hand-working / fully autonomous labor — coined)"
    ),
}

# ── Step 1: Insert new column after I (index 9 in 0-based column indices) ─────
print("Inserting new column after I …")
sheets_svc.spreadsheets().batchUpdate(
    spreadsheetId=SHEET_ID,
    body={'requests': [{
        'insertDimension': {
            'range': {
                'sheetId': sid,
                'dimension': 'COLUMNS',
                'startIndex': 9,
                'endIndex': 10,
            },
            'inheritFromBefore': False,
        }
    }]}
).execute()
print("  Column inserted.")

# ── Step 2: Update headers ─────────────────────────────────────────────────────
print("Updating headers …")
ws.update(values=[['NAH Attested Examples', 'NAH Neologisms']], range_name='I1',
          value_input_option='RAW')

# ── Step 3: Write classified content for each data row ────────────────────────
print("Writing classified content …")
updates = []
for row_num, (attested, neologisms) in ROWS.items():
    sheet_row = row_num + 1   # data rows start at row 2 (row 1 is header)
    updates.append({
        'range': f'I{sheet_row}:J{sheet_row}',
        'values': [[attested, neologisms]],
    })

ws.batch_update(updates, value_input_option='RAW')
print(f"  {len(updates)} rows written.")

# ── Step 4: Apply formatting to new column J (NAH Neologisms) ─────────────────
print("Formatting new column J …")
requests = []

# Header: bold + blue background + white text (match existing header row)
requests.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1,
              'startColumnIndex': 9, 'endColumnIndex': 10},
    'cell': {'userEnteredFormat': {
        'textFormat': {'bold': True, 'fontSize': 10,
                       'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
        'backgroundColor': {'red': 0.20, 'green': 0.40, 'blue': 0.65},
        'horizontalAlignment': 'CENTER',
    }},
    'fields': 'userEnteredFormat(textFormat,backgroundColor,horizontalAlignment)',
}})

# Data rows: wrap text, top-align
requests.append({'repeatCell': {
    'range': {'sheetId': sid, 'startRowIndex': 1,
              'startColumnIndex': 9, 'endColumnIndex': 10},
    'cell': {'userEnteredFormat': {
        'wrapStrategy': 'WRAP',
        'verticalAlignment': 'TOP',
        'textFormat': {'italic': True, 'fontSize': 9},
    }},
    'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment,textFormat)',
}})

# Column width: 280px for neologisms column
requests.append({'updateDimensionProperties': {
    'range': {'sheetId': sid, 'dimension': 'COLUMNS',
              'startIndex': 9, 'endIndex': 10},
    'properties': {'pixelSize': 300},
    'fields': 'pixelSize',
}})

# Column I (attested) also needs a width refresh: 260px
requests.append({'updateDimensionProperties': {
    'range': {'sheetId': sid, 'dimension': 'COLUMNS',
              'startIndex': 8, 'endIndex': 9},
    'properties': {'pixelSize': 260},
    'fields': 'pixelSize',
}})

sheets_svc.spreadsheets().batchUpdate(
    spreadsheetId=SHEET_ID,
    body={'requests': requests}
).execute()
print("  Formatting applied.")

print(f"\nDone. Sheet URL:")
print(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
