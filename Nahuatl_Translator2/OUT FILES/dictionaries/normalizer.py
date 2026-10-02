#!/usr/bin/env python3
"""
normalizer.py — Step 2: Normalizing IDIEZ text and splitting definitions.

Cleans PDF artifacts and splits the body into Spanish/English pairs.
"""

import json
import os
import re

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "raw_idiez.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "normalized_idiez.json")

def normalize_text(text):
    text = re.sub(r'(\w)\.(\d)', r'\1. \2', text)
    text = re.sub(r'([a-z])\.([A-Z])', r'\1. \2', text)
    text = re.sub(r'(\d+)\.([^\s])', r'\1. \2', text)
    return text.strip()

def split_body(text):
    ones = [m.start() for m in re.finditer(r'(^|\s+)1\.\s+', text)]
    if len(ones) >= 2:
        split_pos = ones[1]
        sp_part = text[:split_pos].strip()
        en_part = text[split_pos:].strip()
        sp_items = [s.strip() for s in re.split(r'\d+\.\s+', sp_part) if s.strip()]
        en_items = [e.strip() for e in re.split(r'\d+\.\s+', en_part) if e.strip()]
        return [{"es": s, "en": e} for s, e in zip(sp_items, en_items)]
    
    first_dot = text.find('.')
    if first_dot != -1:
        return [{"es": text[:first_dot].strip(), "en": text[first_dot+1:].strip()}]
    return [{"es": "", "en": text}]

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Normalizing IDIEZ data...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for nah_word, entries in data.items():
        for entry in entries:
            entry["definitions"] = split_body(normalize_text(entry.get("raw_body", "")))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved normalized IDIEZ data to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
