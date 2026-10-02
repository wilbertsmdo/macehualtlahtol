#!/usr/bin/env python3
"""
compare_sullivan_idiez.py — Fill Sullivan es fields from IDIEZ where headwords match.

Input:  normalized_sullivan.json  (9,250 keys, es fields empty)
        enriched_idiez.json       (6,241 keys, es fields populated)

Output: normalized_sullivan_enriched.json   — Sullivan with es fields filled where possible
        sullivan_pending_enrichment.json    — list of unmatched keys needing NLLB/Claude

Match strategy: strip NFD diacritics + lowercase both key sets, then direct lookup.
Matched entries get es filled from IDIEZ + es_source = "IDIEZ".
Unmatched entries keep es = "" + es_source = "pending_enrichment".
"""

import json, os, unicodedata

_HERE  = os.path.dirname(os.path.abspath(__file__))
SULL_IN   = os.path.join(_HERE, "normalized_sullivan.json")
IDIEZ_IN  = os.path.join(_HERE, "enriched_idiez.json")
SULL_OUT  = os.path.join(_HERE, "normalized_sullivan_enriched.json")
PENDING   = os.path.join(_HERE, "sullivan_pending_enrichment.json")


def normalize_key(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().strip()


def collect_idiez_es(entries: list) -> str:
    """Collect all non-empty es definitions from an IDIEZ entry list."""
    seen, parts = set(), []
    for e in entries:
        for d in e.get("definitions", []):
            es = d.get("es", "").strip()
            if es and es not in seen:
                seen.add(es)
                parts.append(es)
    return "; ".join(parts)


def main():
    print("\n=== compare_sullivan_idiez.py ===\n")

    with open(SULL_IN, encoding="utf-8") as f:
        sullivan = json.load(f)
    with open(IDIEZ_IN, encoding="utf-8") as f:
        idiez = json.load(f)

    print(f"[load] Sullivan: {len(sullivan):,} entries")
    print(f"[load] IDIEZ:    {len(idiez):,} entries")

    # Build normalized IDIEZ index: norm_key -> original key
    idiez_index = {normalize_key(k): k for k in idiez}

    matched   = 0
    unmatched = 0
    pending_keys = []
    output = {}

    for sull_key, sull_entries in sullivan.items():
        norm = normalize_key(sull_key)
        idiez_orig_key = idiez_index.get(norm)

        if idiez_orig_key:
            es_text = collect_idiez_es(idiez[idiez_orig_key])
            if es_text:
                # Fill all definitions in this Sullivan entry
                enriched_entries = []
                for entry in sull_entries:
                    e = dict(entry)
                    e["definitions"] = [
                        {"es": es_text, "nah": d.get("nah", "")}
                        for d in entry.get("definitions", [])
                    ]
                    e["es_source"] = "IDIEZ"
                    e["idiez_key"] = idiez_orig_key
                    enriched_entries.append(e)
                output[sull_key] = enriched_entries
                matched += 1
            else:
                # IDIEZ entry exists but es is empty — treat as unmatched
                output[sull_key] = _mark_pending(sull_entries)
                unmatched += 1
                pending_keys.append(sull_key)
        else:
            output[sull_key] = _mark_pending(sull_entries)
            unmatched += 1
            pending_keys.append(sull_key)

    print(f"\n[match] Matched (IDIEZ):  {matched:,}  ({100*matched/len(sullivan):.1f}%)")
    print(f"[match] Unmatched:        {unmatched:,}  ({100*unmatched/len(sullivan):.1f}%)")
    print(f"[match] es fields filled: {matched:,} entries — free, no ML needed")
    print(f"[match] Pending NLLB/Claude enrichment: {unmatched:,} entries")

    with open(SULL_OUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[write] {SULL_OUT}")

    with open(PENDING, "w", encoding="utf-8") as f:
        json.dump(pending_keys, f, ensure_ascii=False, indent=2)
    print(f"[write] {PENDING}  ({len(pending_keys):,} keys to enrich)")

    print("\nDone.")
    print(f"  → Use normalized_sullivan_enriched.json as the new Sullivan source")
    print(f"  → Pass sullivan_pending_enrichment.json to enrich_sullivan.py for NLLB/Claude")


def _mark_pending(entries: list) -> list:
    result = []
    for entry in entries:
        e = dict(entry)
        e["es_source"] = "pending_enrichment"
        result.append(e)
    return result


if __name__ == "__main__":
    main()
