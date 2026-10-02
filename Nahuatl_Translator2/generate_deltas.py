#!/usr/bin/env python3
"""
generate_deltas.py — Build "Deltas" review tabs in each source Google Sheet.

Reads training_data/d5_eval_results.json, classifies each low-BLEU row,
and writes a filtered + flagged "Deltas" tab to Crispin_Carlos and Eduardo sheets.

Columns written:
  A Source | B Row | C Nahuatl | D Gold Spanish | E NLLB Translation
  F BLEU Raw | G BLEU Norm | H Flag | I Error Type | J Rule / Note
  K Human Correction | L Status

Flags:
  skip         — gold contains SKIP/SALTAR (Classical Nahuatl row, excluded from scoring)
  diacritics   — BLEU=0 but texts match after stripping accents (not a real error)
  proper_name  — mostly capitalized tokens, no Nahuatl morphology markers
  heading      — very short (≤3 tokens), no verb ending
  real_error   — genuine translation gap → human fills cols I, J, K

Error Type (pre-filled guess for real_error rows):
  nominalization  — Nahuatl word ends in -liztli / -tl
  verb_morphology — complex prefix stack detected
  hallucination   — NLLB output much longer than gold
  omission        — NLLB output much shorter than gold
  (blank)         — unclear; human fills

Run on tablet (Termux Python — no GPU needed):
  /data/data/com.termux/files/usr/bin/python3 generate_deltas.py
"""

import json
import os
import time
import unicodedata
from collections import Counter, defaultdict

import gspread
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_HERE        = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(_HERE, "training_data", "d5_eval_results.json")

SHEET_IDS = {
    "Crispin_Carlos": "1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg",
    "Eduardo":        "1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw",
}
WORKSHEET_NAME = "Deltas"
BLEU_THRESHOLD = 0.85   # rows at or above this are good — skip

HEADERS = [
    "Source", "Row", "Nahuatl", "Gold Spanish", "NLLB Translation",
    "BLEU Raw", "BLEU Norm", "Flag",
    "Error Type", "Rule / Note",       # ← human fills these to extract grammar rules
    "Human Correction", "Status",
]

# Valid Error Type values (put in sheet instructions / col I note)
ERROR_TYPES = [
    "tense_aspect",      # wrong tense — past vs present, completive vs incompletive
    "verb_morphology",   # object/subject prefixes, applicatives, causatives lost
    "nominalization",    # -liztli, -tl suffix not decoded correctly
    "lexical",           # wrong word choice, missing from dictionary
    "hallucination",     # model invented content not in source
    "place_name",        # proper noun hallucinated or mistranslated
    "register",          # correct meaning, wrong register/formality
    "omission",          # part of the meaning dropped
    "other",
]

# Nahuatl morpheme markers — presence means it's a real Nahuatl word, not a proper name
NAH_MARKERS = {
    "ni", "ti", "xi", "mo", "tla", "tli", "li", "ya", "qui",
    "neh", "meh", "zeh", "on", "oc", "amo", "huan", "ca", "ma",
}

NAH_VERB_ENDINGS = ("toc", "toya", "queh", "yaya", "yahya", "zquia",
                    "znequi", "ya", "z", "h", "qui", "ni")

# Nominalizing suffixes in Huasteca Nahuatl
NAH_NOMINAL_SUFFIXES = ("liztli", "tli", "tl", "li", "yotl", "tzintli")

# Typical Nahuatl verb prefix combinations that indicate complex morphology
NAH_PREFIX_STACK = ("niquin", "tiquin", "nimo", "timo", "quimo", "nech",
                    "tech", "mitz", "kinon", "tlach")

# Gold values that mark Classical Nahuatl rows to skip
SKIP_MARKERS = {"skip", "saltar", "skip/saltar", "saltar/skip"}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
def connect_sheets():
    candidates = [
        os.path.expanduser("~/service_account.json"),
        os.path.join(_HERE, "service_account.json"),
        "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json",
    ]
    sa_path = next((p for p in candidates if os.path.isfile(p)), None)
    if not sa_path:
        raise FileNotFoundError(
            "service_account.json not found — copy it to ~/service_account.json"
        )
    creds = Credentials.from_service_account_file(
        sa_path,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    gc = gspread.authorize(creds)
    print(f"[auth] Connected ({sa_path})")
    return gc


# ---------------------------------------------------------------------------
# Normalized similarity (word overlap after stripping diacritics)
# ---------------------------------------------------------------------------
def strip_diacritics(text: str) -> str:
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode()


def norm_similarity(hypothesis: str, reference: str) -> float:
    h_words = set(strip_diacritics(hypothesis.lower()).split())
    r_words = set(strip_diacritics(reference.lower()).split())
    if not r_words:
        return 0.0
    return round(len(h_words & r_words) / len(r_words), 4)


# ---------------------------------------------------------------------------
# Flagging
# ---------------------------------------------------------------------------
def is_skip_row(gold: str) -> bool:
    """True if the gold column marks this as a Classical Nahuatl / skip row."""
    return gold.strip().lower() in SKIP_MARKERS or \
           any(m in gold.lower() for m in ("skip", "saltar"))


def classify(nahuatl: str, gold: str, nllb: str,
             bleu_raw: float, sim_norm: float) -> str:
    tokens = nahuatl.strip().split()
    n = len(tokens)

    # Diacritics: raw score is low but normalized texts overlap strongly
    if bleu_raw < BLEU_THRESHOLD and sim_norm >= 0.8:
        return "diacritics"

    # Proper name: short, mostly capitalized, no Nahuatl morpheme markers
    if n <= 6:
        cap_ratio = sum(1 for t in tokens if t and t[0].isupper()) / n
        lower_toks = {t.lower().rstrip(".,;:!?") for t in tokens}
        has_nah = bool(lower_toks & NAH_MARKERS)
        if cap_ratio >= 0.6 and not has_nah:
            return "proper_name"

    # Heading: very short, last token has no typical Nahuatl verb ending
    if n <= 3:
        last = tokens[-1].lower().rstrip("?!.,;:") if tokens else ""
        has_verb_ending = any(last.endswith(e) for e in NAH_VERB_ENDINGS)
        if not has_verb_ending:
            return "heading"

    return "real_error"


def guess_error_type(nahuatl: str, gold: str, nllb: str) -> str:
    """Pre-fill Error Type with a best guess. Human corrects if wrong."""
    nah_lower = nahuatl.lower().rstrip("?!.,;: ")
    nah_words = nah_lower.split()

    # Nominalization: any word ends with a nominal suffix
    for word in nah_words:
        if any(word.endswith(suf) for suf in NAH_NOMINAL_SUFFIXES):
            return "nominalization"

    # Complex verb morphology: known prefix stacks
    if any(nah_lower.startswith(pfx) or f" {pfx}" in nah_lower
           for pfx in NAH_PREFIX_STACK):
        return "verb_morphology"

    # Hallucination: NLLB output much longer than gold
    gold_words = len(gold.split())
    nllb_words = len(nllb.split())
    if gold_words > 0 and nllb_words > gold_words * 2:
        return "hallucination"

    # Omission: NLLB output much shorter than gold
    if nllb_words > 0 and gold_words > nllb_words * 2:
        return "omission"

    return ""   # unclear — human fills


# ---------------------------------------------------------------------------
# Process all results
# ---------------------------------------------------------------------------
def process(results: list) -> list:
    deltas = []
    skipped_good = 0
    skipped_classical = 0

    for r in results:
        bleu_raw = r["nllb_bleu"]
        gold     = r["gold_spanish"]

        # Classical Nahuatl rows — should never have been scored
        if is_skip_row(gold):
            skipped_classical += 1
            deltas.append({
                "source":      r["source"],
                "row":         r.get("row"),
                "nahuatl":     r["nahuatl"],
                "gold_spanish": gold,
                "nllb_trans":  r["nllb_trans"],
                "bleu_raw":    bleu_raw,
                "bleu_norm":   0.0,
                "flag":        "skip",
                "error_type":  "",
            })
            continue

        # Good enough — no review needed
        if bleu_raw >= BLEU_THRESHOLD:
            skipped_good += 1
            continue

        sim_norm   = norm_similarity(r["nllb_trans"], gold)
        flag       = classify(r["nahuatl"], gold, r["nllb_trans"], bleu_raw, sim_norm)
        error_type = guess_error_type(r["nahuatl"], gold, r["nllb_trans"]) \
                     if flag == "real_error" else ""

        deltas.append({
            "source":      r["source"],
            "row":         r.get("row"),
            "nahuatl":     r["nahuatl"],
            "gold_spanish": gold,
            "nllb_trans":  r["nllb_trans"],
            "bleu_raw":    bleu_raw,
            "bleu_norm":   sim_norm,
            "flag":        flag,
            "error_type":  error_type,
        })

    print(f"[process] {len(results):,} total")
    print(f"  good (BLEU≥{BLEU_THRESHOLD})    : {skipped_good:,}  (skipped)")
    print(f"  classical/skip rows : {skipped_classical:,}  (excluded from scoring)")
    print(f"  deltas written      : {len(deltas):,}")

    counts = Counter(d["flag"] for d in deltas)
    for flag in ("real_error", "diacritics", "proper_name", "heading", "skip"):
        print(f"    {flag:12s}: {counts.get(flag, 0):,}")

    if skipped_classical:
        bleu_without_skip = [
            r["nllb_bleu"] for r in results
            if not is_skip_row(r["gold_spanish"])
        ]
        if bleu_without_skip:
            adj_avg = sum(bleu_without_skip) / len(bleu_without_skip)
            print(f"\n  Adjusted avg BLEU (skip rows excluded): {adj_avg:.4f}  "
                  f"({adj_avg*100:.1f}/100)")

    return deltas


# ---------------------------------------------------------------------------
# Write Deltas tab
# ---------------------------------------------------------------------------
def write_deltas_tab(gc, source: str, sheet_id: str, rows: list):
    sh = gc.open_by_key(sheet_id)
    n_cols = len(HEADERS)
    last_col = chr(ord("A") + n_cols - 1)   # "L" for 12 columns

    try:
        ws = sh.worksheet(WORKSHEET_NAME)
        ws.clear()
        print(f"[sheet] {source}: cleared existing Deltas tab")
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(
            title=WORKSHEET_NAME,
            rows=max(len(rows) + 10, 100),
            cols=n_cols,
        )
        print(f"[sheet] {source}: created Deltas tab")

    ws.update([HEADERS], "A1")
    ws.format(f"A1:{last_col}1", {"textFormat": {"bold": True}})
    ws.freeze(rows=1)
    time.sleep(0.5)

    if not rows:
        print(f"[sheet] {source}: no deltas to write")
        return

    data = [
        [
            r["source"],
            r["row"] or "",
            r["nahuatl"],
            r["gold_spanish"],
            r["nllb_trans"],
            r["bleu_raw"],
            r["bleu_norm"],
            r["flag"],
            r["error_type"],   # pre-filled guess; human corrects if wrong
            "",                # Rule / Note — human fills
            "",                # Human Correction — human fills
            "skip" if r["flag"] == "skip" else "pending",
        ]
        for r in rows
    ]

    chunk_size = 500
    total_chunks = -(-len(data) // chunk_size)
    for i in range(0, len(data), chunk_size):
        ws.update(data[i : i + chunk_size], f"A{i + 2}")
        print(f"  chunk {i // chunk_size + 1}/{total_chunks}")
        time.sleep(1.0)

    print(f"[sheet] {source}: {len(rows):,} rows written")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("\n=== generate_deltas.py ===\n")

    with open(RESULTS_PATH, encoding="utf-8") as f:
        results = json.load(f)
    print(f"[load] {len(results):,} eval results from d5_eval_results.json\n")

    deltas = process(results)

    by_source = defaultdict(list)
    for d in deltas:
        if d["source"] in SHEET_IDS:
            by_source[d["source"]].append(d)

    gc = connect_sheets()

    for source, sheet_id in SHEET_IDS.items():
        rows = by_source.get(source, [])
        print(f"\n[write] {source}: {len(rows):,} deltas")
        write_deltas_tab(gc, source, sheet_id, rows)
        time.sleep(1.0)

    real_errors = sum(1 for d in deltas if d["flag"] == "real_error")
    skip_rows   = sum(1 for d in deltas if d["flag"] == "skip")
    print(f"\n=== Done ===")
    print(f"Total deltas         : {len(deltas):,}")
    print(f"Need human review    : {real_errors:,}  (real_error — fill cols I, J, K)")
    print(f"Classical/skip rows  : {skip_rows:,}  (status=skip, no action needed)")
    print(f"Sheets updated       : {', '.join(SHEET_IDS)}")
    print(f"\nError Type valid values: {', '.join(ERROR_TYPES)}")


if __name__ == "__main__":
    main()
