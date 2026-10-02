#!/usr/bin/env python3
"""
inverter.py — Step 4: High-Precision Mapping using Scoring and Multi-Match.

This script takes the 'enriched' IDIEZ data and creates an English-to-Nahuatl 
lookup where each English key points to a RANKED LIST of possible translations.
"""

import json
import os

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "enriched_idiez.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "dictionary_idiez.json")

# Linguistic Weightings
NOISE_ROOTS = {"person", "animal", "thing", "someone", "something", "s.o.", "s.t.", "be", "have"}
GRAMMAR_MAP = {
    "tlat": ["noun", "name", "thing", "animal", "place"], # Nahuatl Noun
    "tlach": ["verb", "action", "take", "make", "put", "get", "become"], # Nahuatl Verb
    "quen": ["adjective", "adverb", "very", "much", "full", "covered"] # Nahuatl Adj/Adv
}

def calculate_score(key, nah_word, cat, root_list, en_def):
    score = 0
    key_lower = key.lower()
    def_lower = en_def.lower()
    
    # 1. Root Priority (The semantic core)
    if key_lower in [r.lower() for root in root_list for r in (root.split('.') if '.' in root else [root])]:
        score += 15
        
    # 2. Literal Def Match (If the key is exactly the definition)
    if key_lower == def_lower.strip('.'):
        score += 25
    elif key_lower in def_lower:
        score += 5

    # 3. Noise Penalty
    if key_lower in NOISE_ROOTS:
        score -= 10

    # 4. Grammatical Alignment (Heuristic)
    # If the Nahuatl cat matches the English word usage in the definition
    if cat:
        for nah_prefix, en_keywords in GRAMMAR_MAP.items():
            if cat.startswith(nah_prefix):
                if any(kw in def_lower for kw in en_keywords):
                    score += 10
                    break

    # 5. Brevity Bonus (Direct translations usually have shorter definitions)
    if len(def_lower.split()) <= 2:
        score += 10

    return score

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print("Inverting enriched IDIEZ data with Scoring System...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    inverted = {}

    for nah_word, entries in data.items():
        for entry in entries:
            cat = entry.get("cat")
            past = entry.get("past")
            
            for d in entry.get("definitions", []):
                en_def = d.get("en", "")
                if not en_def: continue
                
                analysis = d.get("analysis_en", {})
                roots = analysis.get("roots", [])
                lemmas = analysis.get("lemmas", [])
                
                # Identify all potential English keys
                potential_keys = set()
                potential_keys.update(roots)
                potential_keys.update(lemmas)
                
                # Add short phrases
                words = en_def.lower().split()
                if len(words) <= 5:
                    potential_keys.add(" ".join(words).strip().rstrip('.,;:'))

                # Clean keys (remove "lodo.mud" artifacts from parser)
                final_keys = []
                for pk in potential_keys:
                    if '.' in pk:
                        final_keys.extend([x for x in pk.split('.') if len(x) > 2])
                    else:
                        if len(pk) > 2: final_keys.append(pk)

                # Map each key
                for key in set(final_keys):
                    score = calculate_score(key, nah_word, cat, roots, en_def)
                    
                    if key not in inverted:
                        inverted[key] = []
                    
                    inverted[key].append({
                        "nah": nah_word,
                        "cat": cat,
                        "past": past,
                        "score": score,
                        "def": en_def
                    })

    # Sort each key's list by score descending
    print("Ranking translations...")
    for key in inverted:
        inverted[key] = sorted(inverted[key], key=lambda x: x['score'], reverse=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(inverted, f, ensure_ascii=False, indent=2)
    
    print(f"Success! Created {len(inverted)} English lookup keys with multiple ranked translations.")

if __name__ == "__main__":
    main()
