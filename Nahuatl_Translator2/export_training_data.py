"""
export_training_data.py
=======================
Exports NAH<->ES and NAH<->EN training pairs for NLLB-200 fine-tuning.

Sources:
  1. Crispin Google Sheet (NAH<->ES)
     Sheet ID : 12ebNz0hxWwoXEpDcXITuRN1q9Q2dlVXwiaJd2YQWUP4
     Worksheet: Crispin
     Data rows: 4-1821 (row 3 = headers)
     Col B = Nahuatl source text
     Col C = gold Spanish translation (human-corrected)
     Col F = BLEU score (0-1 float as string; may be empty)

  2. parallel_sentences.json (NAH<->EN)
     Path: /storage/self/primary/PY_Projects/Nahuatl_Translator2/parallel_sentences.json

Output files (written to training_data/):
  nah_es_pairs.json     -- NAH<->ES pairs from Crispin sheet
  nah_en_pairs.json     -- NAH<->EN pairs from parallel_sentences.json
  export_summary.json   -- stats

Run with:
  /data/data/com.termux/files/usr/bin/python3 export_training_data.py
"""

import json
import os
from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import gspread

# ---------------------------------------------------------------------------
# Platform-agnostic path resolution (Termux + WSL2)
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))

def _token_path():
    env = os.environ.get("GOOGLE_TOKEN_PATH")
    if env:
        return env
    if os.path.isdir("/storage/self/primary"):
        return "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json"
    return os.path.join(_HERE, "token.json")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TOKEN_PATH = _token_path()

NAH_ES_SOURCES = [
    {
        "doc":       "Crispin_Carlos",
        "sheet_id":  "1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg",
        "worksheet": "Crispin",
        "row_start": 4,
        "row_end":   4037,
    },
    {
        "doc":       "Eduardo",
        "sheet_id":  "1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw",
        "worksheet": "Eduardo",
        "row_start": 4,
        "row_end":   301,
    },
]

# Column indices (1-indexed for gspread)
COL_NAHUATL = 2   # B
COL_SPANISH = 3   # C
COL_BLEU    = 6   # F

PARALLEL_SENTENCES_PATH = os.path.join(_HERE, "parallel_sentences.json")

OUTPUT_DIR = os.path.join(_HERE, "training_data")

# BLEU filter settings
# Set BLEU_FILTER_ENABLED = True to exclude rows below MIN_BLEU.
# When False, all rows with non-empty Nahuatl + Spanish are included.
BLEU_FILTER_ENABLED = False
MIN_BLEU            = 0.0   # minimum BLEU score (inclusive); used only when BLEU_FILTER_ENABLED=True


# ---------------------------------------------------------------------------
# Google Sheets auth (OAuth token, not service account)
# ---------------------------------------------------------------------------
def connect_gspread() -> gspread.Client:
    """Authenticate with the stored OAuth token and return a gspread client."""
    print("[auth] Loading OAuth token from:", TOKEN_PATH)
    with open(TOKEN_PATH) as f:
        tok = json.load(f)

    creds = Credentials(
        token=tok.get("token"),
        refresh_token=tok.get("refresh_token"),
        token_uri=tok.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=tok.get("client_id"),
        client_secret=tok.get("client_secret"),
        scopes=tok.get("scopes"),
    )

    if creds.expired and creds.refresh_token:
        print("[auth] Token expired — refreshing...")
        creds.refresh(Request())
        tok["token"] = creds.token
        with open(TOKEN_PATH, "w") as f:
            json.dump(tok, f, indent=2)
        print("[auth] Token refreshed and saved.")

    gc = gspread.authorize(creds)
    print("[auth] Connected to Google Sheets API.")
    return gc


# ---------------------------------------------------------------------------
# Source 1: Crispin sheet -> NAH<->ES pairs
# ---------------------------------------------------------------------------
def fetch_nah_es_pairs_from(gc: gspread.Client, src: dict) -> list[dict]:
    """Fetch NAH<->ES pairs from a single source sheet config."""
    doc, sheet_id, worksheet = src["doc"], src["sheet_id"], src["worksheet"]
    row_start, row_end = src["row_start"], src["row_end"]

    print(f"[sheet] {doc}: opening {sheet_id!r}, worksheet {worksheet!r}...")
    ws = gc.open_by_key(sheet_id).worksheet(worksheet)

    range_str = f"B{row_start}:F{row_end}"
    print(f"[sheet] {doc}: fetching {range_str} ...")
    raw_rows = ws.get(range_str)
    print(f"[sheet] {doc}: retrieved {len(raw_rows)} rows.")

    pairs, skipped_empty, skipped_bleu, bleu_missing = [], 0, 0, 0

    for i, row in enumerate(raw_rows):
        sheet_row  = row_start + i
        row_padded = row + [""] * (5 - len(row))
        nahuatl    = row_padded[0].strip()
        spanish    = row_padded[1].strip()
        bleu_raw   = row_padded[4].strip()

        if not nahuatl or not spanish:
            skipped_empty += 1
            continue

        # Skip SKIP/SALTAR markers
        if spanish.upper() in ("SKIP", "SALTAR"):
            skipped_empty += 1
            continue

        bleu_val = "NA"
        if bleu_raw:
            try:
                bleu_val = float(bleu_raw)
            except ValueError:
                pass
        else:
            bleu_missing += 1

        if BLEU_FILTER_ENABLED and isinstance(bleu_val, float) and bleu_val < MIN_BLEU:
            skipped_bleu += 1
            continue

        pairs.append({
            "nahuatl": nahuatl,
            "spanish": spanish,
            "source":  doc,
            "row":     sheet_row,
            "bleu":    bleu_val,
        })

    print(f"[sheet] {doc}: skipped empty/SKIP: {skipped_empty}, no BLEU: {bleu_missing}, pairs: {len(pairs)}")
    return pairs


def fetch_nah_es_pairs(gc: gspread.Client) -> list[dict]:
    """Fetch NAH<->ES pairs from all configured sources."""
    all_pairs = []
    for src in NAH_ES_SOURCES:
        all_pairs.extend(fetch_nah_es_pairs_from(gc, src))
    print(f"[sheet] Total NAH<->ES pairs collected: {len(all_pairs)}")
    return all_pairs


# ---------------------------------------------------------------------------
# Source 2: parallel_sentences.json -> NAH<->EN pairs
# ---------------------------------------------------------------------------
def load_nah_en_pairs() -> list[dict]:
    """
    Read parallel_sentences.json and return a list of NAH<->EN pair dicts.
    Each record in the file is expected to have at least 'nahuatl' and 'english' keys.
    Records missing either key are skipped with a warning.
    """
    print(f"[parallel] Reading {PARALLEL_SENTENCES_PATH} ...")
    with open(PARALLEL_SENTENCES_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    print(f"[parallel] Loaded {len(raw)} records from parallel_sentences.json.")

    pairs = []
    skipped = 0
    for record in raw:
        nahuatl = (record.get("nahuatl") or "").strip()
        english = (record.get("english") or "").strip()
        if not nahuatl or not english:
            skipped += 1
            continue
        pairs.append({
            "nahuatl": nahuatl,
            "english": english,
            "source":  "parallel_sentences",
        })

    if skipped:
        print(f"[parallel] Records skipped (missing nahuatl or english): {skipped}")
    print(f"[parallel] NAH<->EN pairs collected: {len(pairs)}")
    return pairs


# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------
def write_outputs(nah_es: list[dict], nah_en: list[dict]) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    es_path      = os.path.join(OUTPUT_DIR, "nah_es_pairs.json")
    en_path      = os.path.join(OUTPUT_DIR, "nah_en_pairs.json")
    summary_path = os.path.join(OUTPUT_DIR, "export_summary.json")

    print(f"\n[write] Saving NAH<->ES pairs -> {es_path}")
    with open(es_path, "w", encoding="utf-8") as f:
        json.dump(nah_es, f, ensure_ascii=False, indent=2)

    print(f"[write] Saving NAH<->EN pairs -> {en_path}")
    with open(en_path, "w", encoding="utf-8") as f:
        json.dump(nah_en, f, ensure_ascii=False, indent=2)

    summary = {
        "nah_es_count":    len(nah_es),
        "nah_en_count":    len(nah_en),
        "total_pairs":     len(nah_es) + len(nah_en),
        "min_bleu_filter": MIN_BLEU if BLEU_FILTER_ENABLED else None,
        "bleu_filter_enabled": BLEU_FILTER_ENABLED,
        "exported_at":     datetime.now(timezone.utc).isoformat(),
    }

    print(f"[write] Saving export summary -> {summary_path}")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
def print_summary(nah_es: list[dict], nah_en: list[dict]) -> None:
    total = len(nah_es) + len(nah_en)
    bleu_filter_note = (
        f"BLEU >= {MIN_BLEU}" if BLEU_FILTER_ENABLED else "no BLEU filter"
    )

    print("\n" + "=" * 50)
    print("  EXPORT SUMMARY")
    print("=" * 50)
    print(f"  {'Source':<30} {'Pairs':>8}")
    print(f"  {'-'*30} {'-'*8}")
    from collections import Counter
    src_counts = Counter(p["source"] for p in nah_es)
    for src in NAH_ES_SOURCES:
        label = f"{src['doc']} (NAH<->ES)"
        print(f"  {label:<30} {src_counts.get(src['doc'], 0):>8,}")
    print(f"  {'parallel_sentences (NAH<->EN)':<30} {len(nah_en):>8,}")
    print(f"  {'-'*30} {'-'*8}")
    print(f"  {'TOTAL':<30} {total:>8,}")
    print("=" * 50)
    print(f"  BLEU filter: {bleu_filter_note}")
    print(f"  Output dir : {OUTPUT_DIR}")
    print("=" * 50 + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("\n=== export_training_data.py ===\n")

    # Step 1: connect to Google Sheets
    gc = connect_gspread()

    # Step 2: fetch NAH<->ES pairs from Crispin sheet
    nah_es = fetch_nah_es_pairs(gc)

    # Step 3: load NAH<->EN pairs from parallel_sentences.json
    nah_en = load_nah_en_pairs()

    # Step 4: write output files
    write_outputs(nah_es, nah_en)

    # Step 5: print summary table
    print_summary(nah_es, nah_en)


if __name__ == "__main__":
    main()
