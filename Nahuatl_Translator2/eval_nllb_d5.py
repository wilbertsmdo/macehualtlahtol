#!/usr/bin/env python3
"""
eval_nllb_d5.py — D5: Evaluate fine-tuned NLLB model on all NAH->ES pairs.

Reads training_data/nah_es_pairs.json, runs the fine-tuned NLLB model on
each Nahuatl sentence, computes sentence-level BLEU vs gold Spanish (col C),
and writes results back to the source Google Sheets.

New columns written (existing cols B-I are never touched):
  Col J = NLLB fine-tuned translation
  Col K = NLLB BLEU score (0.0-1.0)

Also saves training_data/d5_eval_results.json for local analysis.

Run on the laptop (WSL2) where the fine-tuned model lives:
  cd ~/WS_Own_Projects_Windows/Nahuatl_Translator
  source .venv/bin/activate
  python3 eval_nllb_d5.py

Place service_account.json at ~/service_account.json, or set SA_KEY_PATH env var.
"""

import argparse
import json
import os
import time
from collections import defaultdict

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sacrebleu.metrics import BLEU
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_HERE      = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(_HERE, "models", "nllb-nah-es-final")
PAIRS_PATH = os.path.join(_HERE, "training_data", "nah_es_pairs.json")
OUT_PATH   = os.path.join(_HERE, "training_data", "d5_eval_results.json")

SRC_LANG   = "nah_Latn"
TGT_LANG   = "spa_Latn"
BATCH_SIZE = 16

SHEET_IDS = {
    "Crispin_Carlos": "1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg",
    "Eduardo":        "1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw",
}
WORKSHEET_NAMES = {
    "Crispin_Carlos": "Crispin",
    "Eduardo":        "Eduardo",
}

COL_NLLB_TRANS = 10   # J
COL_NLLB_BLEU  = 11   # K


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
def _sa_path():
    env = os.environ.get("SA_KEY_PATH")
    if env and os.path.isfile(env):
        return env
    candidates = [
        os.path.expanduser("~/service_account.json"),
        os.path.join(_HERE, "service_account.json"),
        "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json",
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    raise FileNotFoundError(
        "service_account.json not found.\n"
        "Copy it to ~/service_account.json or set SA_KEY_PATH=/path/to/key.json"
    )


def connect_sheets():
    sa_path = _sa_path()
    print(f"[auth] Using service account: {sa_path}")
    creds = Credentials.from_service_account_file(
        sa_path,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    gc = gspread.authorize(creds)
    print("[auth] Connected to Google Sheets.")
    return gc


def write_headers(gc):
    for source, sheet_id in SHEET_IDS.items():
        ws = gc.open_by_key(sheet_id).worksheet(WORKSHEET_NAMES[source])
        existing = ws.row_values(3)
        padded   = existing + [""] * (COL_NLLB_BLEU - len(existing))
        if not padded[COL_NLLB_TRANS - 1]:
            ws.update_cell(3, COL_NLLB_TRANS, "NLLB Tlahtoltlanextilli")
        if not padded[COL_NLLB_BLEU - 1]:
            ws.update_cell(3, COL_NLLB_BLEU, "NLLB BLEU")
        print(f"[headers] {source}: J+K headers ready.")
        time.sleep(0.5)


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[model] Loading {MODEL_PATH}  device={device}")
    if device == "cuda":
        print(f"[model] GPU: {torch.cuda.get_device_name(0)}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    ).to(device)
    model.eval()
    tgt_lang_id = tokenizer.convert_tokens_to_ids(TGT_LANG)
    print("[model] Ready.")
    return tokenizer, model, device, tgt_lang_id


# ---------------------------------------------------------------------------
# BLEU
# ---------------------------------------------------------------------------
_bleu = BLEU(smooth_method="exp")


def sentence_bleu(hypothesis: str, reference: str) -> float:
    score = _bleu.corpus_score([hypothesis], [[reference]])
    return round(score.score / 100, 4)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheets-only", action="store_true",
                        help="Skip inference; load saved d5_eval_results.json and write to sheets")
    args = parser.parse_args()

    print("\n=== eval_nllb_d5.py ===\n")

    if args.sheets_only:
        print(f"[load] Reading saved results from {OUT_PATH}")
        with open(OUT_PATH, encoding="utf-8") as f:
            results = json.load(f)
        avg_bleu = sum(r["nllb_bleu"] for r in results) / len(results)
        print(f"[summary] Avg NLLB BLEU: {avg_bleu:.4f}  ({avg_bleu*100:.1f}/100)")
        _write_to_sheets(results, avg_bleu)
        return

    with open(PAIRS_PATH, encoding="utf-8") as f:
        pairs = json.load(f)
    print(f"[load] {len(pairs):,} NAH<->ES pairs")

    tokenizer, model, device, tgt_lang_id = load_model()

    # Translate all in batches
    print(f"\n[translate] {len(pairs):,} sentences  batch={BATCH_SIZE}")
    nahuatl_texts = [p["nahuatl"] for p in pairs]
    translations  = []
    total_batches = -(-len(nahuatl_texts) // BATCH_SIZE)  # ceil div
    tokenizer.src_lang = SRC_LANG

    for batch_idx in range(total_batches):
        start = batch_idx * BATCH_SIZE
        batch = nahuatl_texts[start : start + BATCH_SIZE]
        inputs = tokenizer(
            batch, return_tensors="pt", padding=True, truncation=True, max_length=256
        ).to(device)
        with torch.no_grad():
            generated = model.generate(
                **inputs,
                forced_bos_token_id=tgt_lang_id,
                max_length=256,
            )
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        translations.extend(decoded)
        if batch_idx % 20 == 0:
            pct = start / len(nahuatl_texts) * 100
            print(f"  {start:,}/{len(nahuatl_texts):,} ({pct:.0f}%)")

    print(f"[translate] {len(translations):,} translations done.")

    # Compute sentence BLEU
    print("[bleu] Computing sentence-level BLEU...")
    results = []
    for pair, nllb_trans in zip(pairs, translations):
        bleu = sentence_bleu(nllb_trans, pair["spanish"])
        results.append({
            "source":      pair["source"],
            "row":         pair.get("row"),
            "nahuatl":     pair["nahuatl"],
            "gold_spanish": pair["spanish"],
            "nllb_trans":  nllb_trans,
            "nllb_bleu":   bleu,
        })

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[save] {OUT_PATH}")

    avg_bleu = sum(r["nllb_bleu"] for r in results) / len(results)
    print(f"\n[summary] Avg NLLB BLEU: {avg_bleu:.4f}  ({avg_bleu*100:.1f}/100)")

    _write_to_sheets(results, avg_bleu)


def _write_to_sheets(results, avg_bleu):
    print("\n[sheets] Writing NLLB translations + BLEU to cols J+K...")
    gc = connect_sheets()
    write_headers(gc)

    by_source = defaultdict(list)
    for r in results:
        if r["row"] is not None and r["source"] in SHEET_IDS:
            by_source[r["source"]].append(r)

    for source, src_results in by_source.items():
        ws = gc.open_by_key(SHEET_IDS[source]).worksheet(WORKSHEET_NAMES[source])
        print(f"[sheets] {source}: {len(src_results):,} rows → cols J+K")

        updates = []
        for r in src_results:
            row = r["row"]
            updates.append({"range": f"J{row}", "values": [[r["nllb_trans"]]]})
            updates.append({"range": f"K{row}", "values": [[r["nllb_bleu"]]]})

        chunk = 500
        total_chunks = -(-len(updates) // chunk)
        for i in range(0, len(updates), chunk):
            ws.batch_update(updates[i : i + chunk])
            print(f"  chunk {i//chunk + 1}/{total_chunks}")
            time.sleep(1.5)

        print(f"[sheets] {source}: done.")

    print("\n=== D5 complete ===")
    print(f"Avg NLLB BLEU : {avg_bleu:.4f}")
    print(f"Local results : {OUT_PATH}")
    print("Sheet updated : cols J (NLLB translation) + K (NLLB BLEU)")


if __name__ == "__main__":
    main()
