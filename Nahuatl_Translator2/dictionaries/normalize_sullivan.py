#!/usr/bin/env python3
"""
normalize_sullivan.py — Step 2: Normalize raw_sullivan.json into the
same schema used by dictionary_idiez.json so morphology.py can query it.

Input:  dictionaries/raw_sullivan.json
Output: dictionaries/normalized_sullivan.json

Output schema (per headword_norm key):
  {
    "headword_norm": [
      {
        "headword_diac":  "āācalaqui",    # with macrons
        "cat":            "tlach2",
        "past":           "āācalacqui",   # panoc field mapped to past
        "prefix":         "ni",
        "raw_body":       "Macehualli...",
        "nah_def":        "Macehualli...", # Nahuatl definition (ready to enrich)
        "disambiguation": null,
        "achi":           "ĀCALAQUI (tlaomp.)",
        "miaq":           null,
        "example":        "Niaacalacqui...",
        "source":         "Sullivan2016",
        "definitions": [
          {
            "es": "",     # empty until enrichment step
            "nah": "Macehualli..."
          }
        ]
      }
    ]
  }

Cross-reference (xiquitta) entries are stored in a separate
normalized_sullivan_xref.json keyed by headword_norm:
  { "acahci": "aahci2" }  # normalized ref target
"""

import json
import os
import unicodedata

_HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON  = os.path.join(_HERE, "raw_sullivan.json")
OUTPUT_JSON = os.path.join(_HERE, "normalized_sullivan.json")
XREF_JSON   = os.path.join(_HERE, "normalized_sullivan_xref.json")


def _norm(s: str) -> str:
    s = s.lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def normalize(raw: dict) -> tuple[dict, dict]:
    """
    Returns (main_dict, xref_dict).
    main_dict keyed by headword_norm -> list of entry dicts.
    xref_dict keyed by headword_norm -> normalized ref target string.
    """
    main: dict[str, list] = {}
    xref: dict[str, str]  = {}

    for norm_key, entries in raw.items():
        for entry in entries:
            if entry["cat"] == "xiquitta":
                ref_target = _norm(entry.get("ref", ""))
                xref[norm_key] = ref_target
                continue

            nah_def = entry.get("raw_body", "").strip()

            normalized_entry = {
                "headword_diac":  entry["headword_diac"],
                "cat":            entry["cat"],
                "past":           entry.get("panoc"),
                "prefix":         entry.get("prefix"),
                "raw_body":       nah_def,
                "nah_def":        nah_def,
                "disambiguation": entry.get("disambiguation"),
                "achi":           entry.get("achi"),
                "miaq":           entry.get("miaq"),
                "example":        entry.get("example"),
                "source":         "Sullivan2016",
                "definitions": [
                    {
                        "es":  "",      # placeholder — fill via enrichment step
                        "nah": nah_def,
                    }
                ],
            }

            key = entry["headword_norm"]
            if key not in main:
                main[key] = []
            main[key].append(normalized_entry)

    return main, xref


def main():
    print("\n=== normalize_sullivan.py ===\n")

    print(f"[load] Reading {INPUT_JSON} ...")
    with open(INPUT_JSON, encoding="utf-8") as f:
        raw = json.load(f)

    total_raw = sum(len(v) for v in raw.values())
    print(f"[load] {len(raw):,} headword keys, {total_raw:,} total entries")

    main_dict, xref_dict = normalize(raw)

    total_main = sum(len(v) for v in main_dict.values())
    print(f"[norm] Main entries : {total_main:,} ({len(main_dict):,} unique headword keys)")
    print(f"[norm] Xref entries : {len(xref_dict):,}")

    # Category breakdown
    from collections import Counter
    cats = Counter(
        e["cat"]
        for entries in main_dict.values()
        for e in entries
    )
    print("\n[norm] Category breakdown:")
    for cat, cnt in cats.most_common():
        print(f"  {cat:<25} {cnt:>5}")

    # Coverage stats
    has_past    = sum(1 for e in (e for v in main_dict.values() for e in v) if e["past"])
    has_example = sum(1 for e in (e for v in main_dict.values() for e in v) if e["example"])
    has_achi    = sum(1 for e in (e for v in main_dict.values() for e in v) if e["achi"])
    print(f"\n[norm] Field coverage (of {total_main} main entries):")
    print(f"  past    : {has_past:>5}  ({has_past/total_main*100:.1f}%)")
    print(f"  example : {has_example:>5}  ({has_example/total_main*100:.1f}%)")
    print(f"  achi    : {has_achi:>5}  ({has_achi/total_main*100:.1f}%)")

    # Sample
    sample_keys = list(main_dict.keys())[:3]
    print("\n[sample]")
    for k in sample_keys:
        for e in main_dict[k]:
            print(f"  {e['headword_diac']} [{k}] cat={e['cat']} past={e['past']}")
            print(f"    nah_def[:80]: {e['nah_def'][:80]}")

    print(f"\n[write] {OUTPUT_JSON}")
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(main_dict, f, ensure_ascii=False, indent=2)

    print(f"[write] {XREF_JSON}")
    with open(XREF_JSON, "w", encoding="utf-8") as f:
        json.dump(xref_dict, f, ensure_ascii=False, indent=2)

    print("\nDone.")


if __name__ == "__main__":
    main()
