#!/usr/bin/env /data/data/com.termux/files/usr/bin/python3
"""
Fix ACK spelling errors in columns I (Attested) and J (Neologisms).
All corrections identified in review 2026-09-27.
"""
import gspread
from google.oauth2.service_account import Credentials

SA_PATH  = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
SHEET_ID = '1TYw3gvcSGmCTQEKchEKlNDUm1BOL-i66jfhsNA1og-k'
SCOPES   = ['https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(SA_PATH, scopes=SCOPES)
gc    = gspread.authorize(creds)
ws    = gc.open_by_key(SHEET_ID).get_worksheet(0)

# Sheet row = data row + 1 (row 1 is header)
# Each entry: (sheet_row, col_letter, corrected_full_cell_content)

FIXES = {
    # I5 — Row 4 attested: kalkan → calcan
    'I5': (
        "tequitiyan (workplace — attested in colonial texts)\n"
        "calcan (near/at the house — classical relational)"
    ),
    # I9 — Row 8 attested: kallton → calton
    'I9': (
        "nantzin (dear mother / respected mother — classical)\n"
        "totoltzintli (the dear little bird / reverential small — classical)\n"
        "tlahtotzintli (the honored word / reverential speech — classical)\n"
        "calton (little house / shack — Karttunen)\n"
        "pilton (small child / urchin — documented)"
    ),
    # I11 — Row 10 attested: posotik → pozotic, cualtik → cualtic
    'I11': (
        "teyoh (stony / stone-like — Karttunen)\n"
        "xochiyoh (flowery / of flower quality — documented)\n"
        "pozotic (foamy / bubbly — Sullivan IDIEZ)\n"
        "cualtic (well-made / good-quality adjective — documented)"
    ),
    # I22 — Row 21 attested: ichpak → icpac
    'I22': (
        "icpac (above — classical ACK relational noun)\n"
        "itlan / tlantli (below / under — classical relational)\n"
        "itzinco / tzintli (base/foundation — classical body-part root)\n"
        "ixpan (in front of / over-facing — classical relational)"
    ),
    # J22 — Row 21 neologisms: ichpak → icpac
    'J22': (
        "icpac tlamaniliztli (above-placing / superstructure — coined)\n"
        "itlan-tlamaniliztli (under-structure / infrastructure — coined)\n"
        "tzintlamaniliztli (base-structure / fundamental structure — coined)\n"
        "ixpan tlahtocayotl (above-governance / supranational authority — coined)"
    ),
    # J25 — Row 24 neologisms: tlaltikpak → tlalticpac (×3)
    'J25': (
        "tla-tlalticpac-iximatiliztli (deep-knowing of the earth / geology — coined)\n"
        "tla-yoliliztli-iximatiliztli (deep-knowing of life / biology — coined)\n"
        "tla-tomin-iximatiliztli (deep-knowing of money / economics — coined)\n"
        "tla-nemilistli-iximatiliztli (deep-knowing of society / sociology — coined)\n"
        "tla-tonatiuh-iximatiliztli (deep-knowing of the sun / astronomy — coined)"
    ),
    # J26 — Row 25 neologisms: tlaltikpak → tlalticpac (×1)
    'J26': (
        "tla-tlalticpac-iximatini (deep-knower of the earth / geologist — coined)\n"
        "tla-tomin-iximatini (deep-knower of money / economist — coined)\n"
        "tla-altepetl-tlahtocaliztli-iximatini (deep-knower of governance / political scientist — coined)\n"
        "tla-yoliliztli-iximatini (biologist — coined)\n"
        "tomin-matini (money-knower / economist colloquial — coined)"
    ),
    # I32 — Row 31 attested: remove mauhkayotl (IDIEZ), keep mauhcayotl only
    'I32': (
        "mauhcayotl (fear-quality — Karttunen)\n"
        "temauhti (something frightful — documented)"
    ),
    # J32 — Row 31 neologisms: tlacatekolotkayotl → tlacatecolotcayotl; mauhkayotl → mauhcayotl ×2
    'J32': (
        "tlacatecolotcayotl (devil-being-fear-quality / xenophobia — coined)\n"
        "ixtlahuatl-mauhcayotl (open-space-fear / agoraphobia — coined)\n"
        "coyotlahtolli-mauhcayotl (foreign-language fear — coined)"
    ),
    # J33 — Row 32 neologisms: tlaltikpak → tlalticpac
    'J33': (
        "amox-tlazohtlaliztli (book-loving / bibliophilia — coined)\n"
        "amox-tlazohtlani (book-lover / bibliophile — coined)\n"
        "tlalticpac-tlazohtlani (earth-lover / ecophile / environmentalist — coined)"
    ),
    # J28 — Row 27 neologisms: yollizcocolyotl → yollotcocolyotl
    'J28': (
        "momaxtilanococolyotl (joint-sickness / arthritis concept — coined)\n"
        "eztli-cocolyotl (blood-sickness / anemia concept — coined)\n"
        "momaxtilanoh-cocoa-liztli (joint-hurting-process / arthritis — coined)\n"
        "yollotcocolyotl (heart-disease-quality / cardiac pathology — coined)"
    ),
}

updates = []
for cell_ref, content in FIXES.items():
    updates.append({
        'range': cell_ref,
        'values': [[content]],
    })

ws.batch_update(updates, value_input_option='RAW')
print(f"Applied {len(updates)} cell corrections:")
for ref in FIXES:
    print(f"  {ref} ✓")
print("\nDone.")
