"""
score_perplexity.py — Score every Nahuatl sentence (col B) in all sheets
with Tiyat perplexity and write the result to col L ("Tiyat PPL").

Low PPL  (5–50)   → natural, high-confidence Nahuatl
Medium   (50–200) → normal for literary/complex sentences
High PPL (200+)   → possible OCR error, Spanish word, unusual construction

Run: /usr/bin/python3 score_perplexity.py

Config flags (edit below):
  OVERWRITE   = False  → skip rows where col L is already filled
  DRY_RUN     = True   → compute but don't write to sheet (for testing)
  MAX_ROWS    = None   → process all rows; set e.g. 50 for a test pass
"""

import json, math, sys, time
import gspread
from google.oauth2.service_account import Credentials

# ── Config ───────────────────────────────────────────────────────────────────
OVERWRITE  = False
DRY_RUN    = False
MAX_ROWS   = None          # None = all rows; set to 50 for a test run
COL_NAH    = 2             # col B — Nahuatl source
COL_PPL    = 12            # col L — Tiyat perplexity output
DATA_START = 4             # first data row (row 1=title, 2=blank, 3=headers)
BATCH_SIZE = 8             # sentences per inference batch (lower if OOM)
MAX_TOKENS = 512           # Tiyat context window is 918; leave headroom

SA_PATH = "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json"
SCOPES  = ["https://www.googleapis.com/auth/spreadsheets"]

# All sheets to process: (spreadsheet_id, worksheet_name, label)
SHEETS = [
    ("1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg", "Crispin",  "Crispin_Carlos"),
    ("1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw", "Eduardo",  "Eduardo"),
    # Add the 10 new doc sheets here once their IDs are confirmed:
    # ("SHEET_ID", "WORKSHEET", "label"),
]

# ── Load Tiyat ────────────────────────────────────────────────────────────────
print("Loading Tiyat model and tokenizer...")
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    tok = AutoTokenizer.from_pretrained(
        "tachiwin/tiyat_alpha_arch1", trust_remote_code=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        "tachiwin/tiyat_alpha_arch1",
        trust_remote_code=True,
        torch_dtype=torch.float32,
    )
    model.eval()
    print(f"  Model loaded ({sum(p.numel() for p in model.parameters()):,} params)")
    HAVE_TORCH = True
except ImportError:
    print("  WARNING: torch not available — perplexity will be estimated via token count only")
    HAVE_TORCH = False

# ── Perplexity function ───────────────────────────────────────────────────────
def compute_perplexity(text):
    """Return Tiyat perplexity for a single Nahuatl sentence."""
    if not HAVE_TORCH:
        # Fallback: no real perplexity, return -1 as sentinel
        return -1.0

    text = text.strip()
    if not text:
        return None

    ids = tok.encode(text, return_tensors="pt")
    if ids.shape[1] > MAX_TOKENS:
        ids = ids[:, :MAX_TOKENS]   # truncate very long sentences
    if ids.shape[1] < 2:
        return None                 # too short to score

    with torch.no_grad():
        try:
            out  = model(ids, labels=ids)
            loss = out.loss.item()   # mean cross-entropy per token
            return round(math.exp(loss), 2)
        except Exception as e:
            print(f"    inference error: {e}")
            return None

# ── Sheets auth ───────────────────────────────────────────────────────────────
print("\nConnecting to Google Sheets...")
creds = Credentials.from_service_account_file(SA_PATH, scopes=SCOPES)
gc    = gspread.authorize(creds)

# ── Process each sheet ────────────────────────────────────────────────────────
for sheet_id, worksheet_name, label in SHEETS:
    print(f"\n{'='*60}")
    print(f"Sheet: {label} ({worksheet_name})")

    try:
        sh = gc.open_by_key(sheet_id)
        ws = sh.worksheet(worksheet_name)
    except Exception as e:
        print(f"  ERROR opening sheet: {e}")
        continue

    # Read all col B (Nahuatl) and col L (existing PPL scores)
    all_b = ws.col_values(COL_NAH)    # list of all values in col B
    all_l = ws.col_values(COL_PPL)    # list of all values in col L (may be short)

    total_rows = len(all_b)
    print(f"  Rows in col B: {total_rows}  (data starts row {DATA_START})")

    # Write col L header if missing
    header_l = all_l[2] if len(all_l) >= 3 else ""
    if not header_l and not DRY_RUN:
        ws.update_cell(3, COL_PPL, "Tiyat PPL")
        print("  Wrote col L header")

    # Collect rows to process
    to_process = []
    for i in range(DATA_START - 1, total_rows):   # 0-indexed
        row_num  = i + 1
        nah_text = all_b[i].strip() if i < len(all_b) else ""
        existing = all_l[i].strip() if i < len(all_l) else ""

        if not nah_text:
            continue
        if existing and not OVERWRITE:
            continue
        if nah_text.upper() in ("SKIP", "SALTAR"):
            continue
        to_process.append((row_num, nah_text))

        if MAX_ROWS and len(to_process) >= MAX_ROWS:
            break

    print(f"  Rows to score: {len(to_process)}")
    if not to_process:
        print("  Nothing to do.")
        continue

    # Score and write in batches
    scored, skipped, errors = 0, 0, 0
    updates = []      # batch up writes: [(row_num, ppl_value)]

    for idx, (row_num, nah_text) in enumerate(to_process):
        ppl = compute_perplexity(nah_text)

        if ppl is None:
            skipped += 1
            continue

        updates.append((row_num, ppl))
        scored += 1

        # Progress print
        if (idx + 1) % 50 == 0 or idx == len(to_process) - 1:
            print(f"  [{idx+1}/{len(to_process)}] row {row_num}: ppl={ppl}")

        # Flush writes every BATCH_SIZE rows
        if len(updates) >= BATCH_SIZE and not DRY_RUN:
            cell_updates = [
                gspread.Cell(r, COL_PPL, str(v)) for r, v in updates
            ]
            ws.update_cells(cell_updates)
            updates = []
            time.sleep(0.3)   # brief pause to respect API rate limits

    # Final flush
    if updates and not DRY_RUN:
        cell_updates = [gspread.Cell(r, COL_PPL, str(v)) for r, v in updates]
        ws.update_cells(cell_updates)

    print(f"  Done — scored: {scored}, skipped (empty/short): {skipped}, errors: {errors}")
    if DRY_RUN:
        print("  DRY_RUN=True — nothing written to sheet")

print("\n\nAll sheets complete.")

# ── Optional: export perplexity stats to training_data JSON ──────────────────
if HAVE_TORCH and not DRY_RUN:
    print("\nAppending perplexity scores to training_data/nah_es_pairs.json ...")
    try:
        pairs_path = "training_data/nah_es_pairs.json"
        with open(pairs_path) as f:
            pairs = json.load(f)

        changed = 0
        for p in pairs:
            if p.get("nahuatl") and "tiyat_ppl" not in p:
                ppl = compute_perplexity(p["nahuatl"])
                if ppl is not None:
                    p["tiyat_ppl"] = ppl
                    changed += 1

        with open(pairs_path, "w") as f:
            json.dump(pairs, f, ensure_ascii=False, indent=2)
        print(f"  Updated {changed} pairs with tiyat_ppl field")
    except Exception as e:
        print(f"  Could not update training data: {e}")
