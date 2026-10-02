#!/usr/bin/env python3
"""
prep_training_data.py — Prepare NAH<->ES pairs for NLLB-200 fine-tuning.

Input:  training_data/nah_es_pairs.json
Output: training_data/hf_train/  (HuggingFace arrow dataset, 90%)
        training_data/hf_val/    (HuggingFace arrow dataset, 10%)

Run once before finetune_nllb.py.
"""

import json, os
from datasets import Dataset

_HERE = os.path.dirname(os.path.abspath(__file__))
INPUT  = os.path.join(_HERE, "training_data", "nah_es_pairs.json")
OUTDIR = os.path.join(_HERE, "training_data")
VAL_SPLIT = 0.10

def main():
    print("\n=== prep_training_data.py ===\n")

    with open(INPUT, encoding="utf-8") as f:
        pairs = json.load(f)
    print(f"[load] {len(pairs):,} NAH<->ES pairs from nah_es_pairs.json")

    records = [{"src": p["nahuatl"], "tgt": p["spanish"]} for p in pairs
               if p.get("nahuatl","").strip() and p.get("spanish","").strip()]
    print(f"[filter] {len(records):,} non-empty pairs")

    n_val   = int(len(records) * VAL_SPLIT)
    n_train = len(records) - n_val

    ds_train = Dataset.from_list(records[n_val:])
    ds_val   = Dataset.from_list(records[:n_val])

    train_path = os.path.join(OUTDIR, "hf_train")
    val_path   = os.path.join(OUTDIR, "hf_val")

    ds_train.save_to_disk(train_path)
    ds_val.save_to_disk(val_path)

    print(f"[split] Train: {n_train:,}  Val: {n_val:,}")
    print(f"[write] {train_path}")
    print(f"[write] {val_path}")
    print("\nDone — ready to run finetune_nllb.py")

if __name__ == "__main__":
    main()
