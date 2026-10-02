#!/usr/bin/env python3
"""
merger.py — Step 5: Final Dictionary Assembly (IDIEZ focus).

Combines the inverted IDIEZ data into the final master dictionary.json.
"""

import json
import os

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INV_IDIEZ = os.path.join(BASE_DIR, "dictionary_idiez.json")
MASTER_DICT = os.path.join(BASE_DIR, "dictionary.json")

def main():
    if not os.path.exists(INV_IDIEZ):
        print(f"Error: {INV_IDIEZ} not found.")
        return

    print(f"Loading inverted IDIEZ data...")
    with open(INV_IDIEZ, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # In an IDIEZ-only scenario, merging is just a copy/rename, 
    # but we keep the script for future modularity.
    with open(MASTER_DICT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Final Master Dictionary saved: {MASTER_DICT} ({len(data)} keys)")

if __name__ == "__main__":
    main()
