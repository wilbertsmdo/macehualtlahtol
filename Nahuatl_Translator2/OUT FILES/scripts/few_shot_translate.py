#!/usr/bin/env python3
"""
few_shot_translate.py
NAH→ES translation using Claude API (few-shot + IDIEZ dictionary hints).

Test mode: translates 10 rows from the Crispin sheet and writes drafts to col E.
Gold Spanish is in col C (rows 4-488) — compare E vs C to measure error rate.

Usage:
    /data/data/com.termux/files/usr/bin/python3 few_shot_translate.py
"""

import json, re, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import gspread
import anthropic

# ── Config ─────────────────────────────────────────────────────────────────────
TOKEN_PATH     = "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json"
SPREADSHEET_ID = "12ebNz0hxWwoXEpDcXITuRN1q9Q2dlVXwiaJd2YQWUP4"
DICT_PATH      = "/storage/self/primary/PY_Projects/Nahuatl_Translator2/dictionaries/enriched_idiez.json"
MODEL          = "claude-haiku-4-5"

# Rows to translate (test batch — all have gold Spanish in col C)
TEST_ROWS      = list(range(15, 25))   # 10 sentences from the Presentacion section
FEW_SHOT_ROWS  = list(range(5, 10))    # 5 rows from Acknowledgements section (as examples)
MAX_DICT_HINTS = 8                     # max IDIEZ entries to inject per sentence


# ── Auth ───────────────────────────────────────────────────────────────────────
def get_worksheet():
    with open(TOKEN_PATH) as f:
        tok = json.load(f)
    creds = Credentials(
        token=tok["token"], refresh_token=tok["refresh_token"],
        token_uri=tok["token_uri"], client_id=tok["client_id"],
        client_secret=tok["client_secret"], scopes=tok["scopes"],
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        tok["token"] = creds.token
        with open(TOKEN_PATH, "w") as f:
            json.dump(tok, f, indent=2)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    return sh.worksheet("Crispin")


# ── Dictionary lookup ──────────────────────────────────────────────────────────
def load_dictionary():
    with open(DICT_PATH) as f:
        return json.load(f)

def dict_hints(sentence, dictionary):
    """Return up to MAX_DICT_HINTS IDIEZ Spanish definitions for tokens in sentence."""
    tokens = re.findall(r'[a-záéíóúāēīōū]+', sentence.lower())
    seen, hints = set(), []
    for token in tokens:
        if token in dictionary and token not in seen:
            seen.add(token)
            entries = dictionary[token]
            if isinstance(entries, list) and entries:
                defs = entries[0].get("definitions", [])
                if defs:
                    es_def = defs[0].get("es", "").strip()
                    if es_def:
                        hints.append(f"  {token} → {es_def}")
        if len(hints) >= MAX_DICT_HINTS:
            break
    return hints


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("Loading dictionary and connecting to sheet...")
    dictionary = load_dictionary()
    ws = get_worksheet()

    # Read few-shot examples (NAH col B + ES col C)
    fs_data = ws.get(f"B{min(FEW_SHOT_ROWS)}:C{max(FEW_SHOT_ROWS)}")
    few_shot = [(r[0].strip(), r[1].strip()) for r in fs_data if len(r) >= 2 and r[0].strip() and r[1].strip()]
    print(f"Loaded {len(few_shot)} few-shot examples from rows {min(FEW_SHOT_ROWS)}-{max(FEW_SHOT_ROWS)}")

    # Read test rows (NAH col B + gold ES col C for comparison)
    test_data = ws.get(f"B{min(TEST_ROWS)}:C{max(TEST_ROWS)}")
    while len(test_data) < len(TEST_ROWS):
        test_data.append(["", ""])

    # Build base few-shot message turns (shared across all requests)
    few_shot_messages = []
    for nah, es in few_shot:
        few_shot_messages.append({"role": "user",      "content": f"Traduce al español: {nah}"})
        few_shot_messages.append({"role": "assistant", "content": es})

    system = (
        "Eres un experto en traducción del náhuatl huasteco (documentado por el IDIEZ) al español. "
        "Traduce cada oración al español natural y fluido del México. "
        "Responde ÚNICAMENTE con la traducción — sin notas, sin explicaciones."
    )

    client = anthropic.Anthropic()
    results = []

    print(f"\nTranslating {len(TEST_ROWS)} rows...\n{'─'*60}")

    for i, row_num in enumerate(TEST_ROWS):
        row   = test_data[i]
        nah   = row[0].strip() if row else ""
        gold  = row[1].strip() if len(row) > 1 else ""

        if not nah:
            print(f"Row {row_num}: (empty — skipping)")
            results.append((row_num, "", ""))
            continue

        # Build per-sentence dict hints
        hints = dict_hints(nah, dictionary)
        hint_block = ""
        if hints:
            hint_block = "\n\n[Diccionario IDIEZ]\n" + "\n".join(hints)

        messages = few_shot_messages + [
            {"role": "user", "content": f"Traduce al español: {nah}{hint_block}"}
        ]

        resp = client.messages.create(
            model=MODEL,
            max_tokens=512,
            system=system,
            messages=messages,
        )
        translation = resp.content[0].text.strip()
        results.append((row_num, nah, translation))

        print(f"Row {row_num}")
        print(f"  NAH : {nah[:90]}")
        print(f"  GOLD: {gold[:90]}")
        print(f"  CLAU: {translation[:90]}")
        print()

        time.sleep(0.3)

    # Write drafts to col E
    print("─"*60)
    print("Writing drafts to col E...")
    for row_num, nah, translation in results:
        if translation:
            ws.update(f"E{row_num}", [[translation]])
            time.sleep(0.15)

    translated = sum(1 for _, _, t in results if t)
    print(f"\nDone — {translated}/{len(TEST_ROWS)} rows written to col E.")
    print("Review: compare col C (gold) vs col E (Claude draft) in the sheet.")


if __name__ == "__main__":
    main()
