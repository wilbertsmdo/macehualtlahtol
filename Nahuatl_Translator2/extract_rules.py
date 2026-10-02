#!/usr/bin/env python3
"""
extract_rules.py — Harvest translation rules from all source sheets
                   and merge into translation_rules.json.

Run this after each translate_and_learn.py pass to pull new rules
from col H (auto) and col I (human) into the shared rule base.

Sources configured in SOURCES below — add new sheets as they accumulate data.

Usage:
    /data/data/com.termux/files/usr/bin/python3 extract_rules.py
"""

import json, os, re, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import gspread

_HERE = os.path.dirname(os.path.abspath(__file__))

def _token_path():
    env = os.environ.get("GOOGLE_TOKEN_PATH")
    if env:
        return env
    if os.path.isdir("/storage/self/primary"):
        return "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json"
    return os.path.join(_HERE, "token.json")

TOKEN_PATH  = _token_path()
RULES_FILE  = os.path.join(_HERE, "translation_rules.json")

# ── Sheet sources: add Eduardo and future sheets here ────────────────────────
SOURCES = [
    {
        "doc":        "Crispin",
        "sheet_id":   "12ebNz0hxWwoXEpDcXITuRN1q9Q2dlVXwiaJd2YQWUP4",
        "worksheet":  "Crispin",
        "data_start": 4,     # first data row (skip headers)
        "data_end":   1821,  # last row with gold Spanish (col C)
        # col layout: B=NAH, C=gold, E=draft, F=BLEU, G=delta, H=auto_rule, I=human_rule
    },
    {
        "doc":        "Crispin_Carlos",
        "sheet_id":   "1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg",
        "worksheet":  "Crispin",
        "data_start": 4,
        "data_end":   4037,
    },
    {
        "doc":        "Eduardo",
        "sheet_id":   "1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw",
        "worksheet":  "Eduardo",
        "data_start": 4,
        "data_end":   301,
    },
]

MIN_BLEU_FOR_AUTO = 0.0   # include all auto rules regardless of BLEU


# ── Auth ──────────────────────────────────────────────────────────────────────
def connect():
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
    return gspread.authorize(creds)


# ── Load existing rules file ──────────────────────────────────────────────────
def load_existing():
    try:
        with open(RULES_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"version": 1, "rules": []}


# ── Deduplication: exact + near-match ────────────────────────────────────────
def normalise(text):
    return re.sub(r'\s+', ' ', text.lower().strip())

def is_duplicate(new_rule, existing_rules):
    n = normalise(new_rule)
    for r in existing_rules:
        if normalise(r["rule"]) == n:
            return True
        # near-match: >80% word overlap
        a = set(n.split())
        b = set(normalise(r["rule"]).split())
        if a and b and len(a & b) / max(len(a), len(b)) > 0.8:
            return True
    return False


# ── Harvest from one sheet ────────────────────────────────────────────────────
def harvest(gc, source, existing_rules):
    doc       = source["doc"]
    start     = source["data_start"]
    end       = source["data_end"]

    print(f"\n  Source: {doc} (rows {start}–{end})")
    ws   = gc.open_by_key(source["sheet_id"]).worksheet(source["worksheet"])
    # Read cols B, C, E, F, G, H, I  →  range B:I
    data = ws.get(f"B{start}:I{end}")

    new_rules = []
    for i, row in enumerate(data):
        row_num    = start + i
        bleu_str   = row[4].strip() if len(row) > 4 else ""
        auto_rule  = row[6].strip() if len(row) > 6 else ""
        human_rule = row[7].strip() if len(row) > 7 else ""

        bleu = 0.0
        try:
            bleu = float(bleu_str) if bleu_str else 0.0
        except ValueError:
            pass

        # Human rule takes precedence; fall back to auto
        rule_text      = human_rule if human_rule else auto_rule
        human_verified = bool(human_rule)

        if not rule_text:
            continue
        if bleu < MIN_BLEU_FOR_AUTO and not human_verified:
            continue
        if is_duplicate(rule_text, existing_rules + new_rules):
            continue

        new_rules.append({
            "rule":           rule_text,
            "source_doc":     doc,
            "source_row":     row_num,
            "bleu":           bleu,
            "human_verified": human_verified,
            "evidence_count": 1,
        })

    print(f"    {len(new_rules)} new rules harvested")
    return new_rules


# ── Merge + rank ──────────────────────────────────────────────────────────────
def merge_and_rank(all_rules):
    """Sort: human-verified first, then by BLEU descending."""
    return sorted(
        all_rules,
        key=lambda r: (not r["human_verified"], -r["bleu"])
    )


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  EXTRACT RULES → translation_rules.json")
    print("=" * 60)

    gc       = connect()
    existing = load_existing()
    prior    = len(existing["rules"])
    print(f"\n  Existing rules: {prior}")

    all_new = []
    for source in SOURCES:
        new = harvest(gc, source, existing["rules"])
        all_new.extend(new)
        time.sleep(1)

    existing["rules"].extend(all_new)
    existing["rules"] = merge_and_rank(existing["rules"])

    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    total = len(existing["rules"])
    human = sum(1 for r in existing["rules"] if r["human_verified"])
    print(f"\n  Rules after merge : {total} ({total - prior} new)")
    print(f"  Human-verified    : {human}")
    print(f"  Auto only         : {total - human}")
    print(f"\n  Saved → {RULES_FILE}")


if __name__ == "__main__":
    main()
