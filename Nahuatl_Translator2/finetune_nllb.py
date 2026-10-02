#!/usr/bin/env python3
"""
finetune_nllb.py — Fine-tune facebook/nllb-200-distilled-600M on NAH<->ES pairs.

Prerequisites:
    python3 prep_training_data.py   (generates training_data/hf_train + hf_val)
    pip install torch transformers datasets accelerate sentencepiece sacrebleu

Output: models/nllb-nah-es-final/

Estimated time: ~30-60 min on GPU, ~8-12 hrs on CPU.
"""

import os
import importlib.util
import sys

# Preflight: fail fast with a clear message if packages are missing
_REQUIRED = ["datasets", "transformers", "accelerate", "sentencepiece", "sacrebleu", "torch"]
_missing = [p for p in _REQUIRED if importlib.util.find_spec(p) is None]
if _missing:
    print(f"[ERROR] Missing packages: {', '.join(_missing)}")
    print(f"  Fix: pip install {' '.join(_missing)}")
    sys.exit(1)

import torch
import transformers
from datasets import load_from_disk
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq,
)

print(f"[versions] transformers={transformers.__version__}  torch={torch.__version__}")

_HERE     = os.path.dirname(os.path.abspath(__file__))
TRAIN_DIR = os.path.join(_HERE, "training_data", "hf_train")
VAL_DIR   = os.path.join(_HERE, "training_data", "hf_val")
MODEL_OUT = os.path.join(_HERE, "models", "nllb-nah-es-final")
CKPT_DIR  = os.path.join(_HERE, "models", "nllb-nah-es")

MODEL_NAME = "facebook/nllb-200-distilled-600M"
SRC_LANG   = "nah_Latn"
TGT_LANG   = "spa_Latn"
MAX_LEN    = 128


def tokenize(batch, tokenizer):
    inputs = tokenizer(
        batch["src"],
        max_length=MAX_LEN,
        truncation=True,
        padding="max_length",
    )
    labels = tokenizer(
        text_target=batch["tgt"],
        max_length=MAX_LEN,
        truncation=True,
        padding="max_length",
    )
    inputs["labels"] = labels["input_ids"]
    return inputs


def main():
    print("\n=== finetune_nllb.py ===\n")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[device] {device}")
    if device == "cuda":
        print(f"[gpu]    {torch.cuda.get_device_name(0)}")

    print(f"[load]   Tokenizer + model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, src_lang=SRC_LANG)
    model     = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    # Tell the model which language to generate during eval/inference
    model.generation_config.forced_bos_token_id = tokenizer.convert_tokens_to_ids(TGT_LANG)

    print("[data]   Loading datasets...")
    ds_train = load_from_disk(TRAIN_DIR)
    ds_val   = load_from_disk(VAL_DIR)
    print(f"[data]   Train: {len(ds_train):,}  Val: {len(ds_val):,}")

    print("[tok]    Tokenizing...")
    ds_train = ds_train.map(
        lambda b: tokenize(b, tokenizer), batched=True, remove_columns=["src", "tgt"]
    )
    ds_val = ds_val.map(
        lambda b: tokenize(b, tokenizer), batched=True, remove_columns=["src", "tgt"]
    )

    os.makedirs(CKPT_DIR, exist_ok=True)
    os.makedirs(MODEL_OUT, exist_ok=True)

    args = Seq2SeqTrainingArguments(
        output_dir=CKPT_DIR,
        num_train_epochs=10,
        per_device_train_batch_size=4,       # reduced from 8 to avoid CUDA OOM
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=2,       # effective batch = 4*2 = 8, same throughput
        warmup_steps=100,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        predict_with_generate=True,
        fp16=(device == "cuda"),
        logging_steps=50,
        report_to="none",
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=args,
        train_dataset=ds_train,
        eval_dataset=ds_val,
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model, padding=True),
    )

    # Resume from last checkpoint if one exists
    import glob
    checkpoints = sorted(glob.glob(os.path.join(CKPT_DIR, "checkpoint-*")))
    resume_from = checkpoints[-1] if checkpoints else None
    if resume_from:
        print(f"\n[train]  Resuming from {resume_from}")
    else:
        print(f"\n[train]  Starting fresh")
    print(f"         Epochs={args.num_train_epochs}  batch={args.per_device_train_batch_size}  "
          f"grad_accum={args.gradient_accumulation_steps}  fp16={args.fp16}")
    print(f"         Checkpoints → {CKPT_DIR}\n")
    trainer.train(resume_from_checkpoint=resume_from)

    print(f"\n[save]   Best model → {MODEL_OUT}")
    trainer.save_model(MODEL_OUT)
    tokenizer.save_pretrained(MODEL_OUT)

    # Quick sanity test
    print("\n[test]   Running 3 inference sentences...")
    from transformers import pipeline as hf_pipeline
    pipe = hf_pipeline(
        "translation",
        model=MODEL_OUT,
        tokenizer=MODEL_OUT,
        src_lang=SRC_LANG,
        tgt_lang=TGT_LANG,
        device=0 if device == "cuda" else -1,
    )
    for s in [
        "Niaacalacqui quemman tiyahqueh atlauhco.",
        "Nitlatequitiz notequiuh.",
        "Tlami ce tequitl.",
    ]:
        print(f"  NAH: {s}")
        print(f"  ES : {pipe(s)[0]['translation_text']}\n")

    print(f"[done]   Model saved to {MODEL_OUT}")


if __name__ == "__main__":
    main()
