#!/usr/bin/env python3
"""
enricher.py — Step 3: Linguistic Analysis of IDIEZ Definitions.

Adds NLP context (roots, lemmas) to the normalized definitions.
"""

import json
import os
import spacy
from tqdm import tqdm

# Load models
print("Loading NLP models...")
try:
    nlp_en = spacy.load("en_core_web_sm")
    nlp_es = spacy.load("es_core_news_sm")
except OSError:
    print("Error: Models not found.")
    exit(1)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "normalized_idiez.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "enriched_idiez.json")

def get_linguistic_data(text, nlp):
    if not text or not isinstance(text, str):
        return {"roots": [], "lemmas": []}
    doc = nlp(text.lower())
    roots = [token.lemma_ for token in doc if token.dep_ == "ROOT"]
    lemmas = [token.lemma_ for token in doc if token.pos_ in ["NOUN", "VERB", "ADJ"] and not token.is_stop and len(token.text) > 2]
    return {"roots": list(set(roots)), "lemmas": list(set(lemmas))}

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Enriching IDIEZ data...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for nah_word, entries in tqdm(data.items()):
        for entry in entries:
            for d in entry.get("definitions", []):
                d["analysis_en"] = get_linguistic_data(d.get("en", ""), nlp_en)
                d["analysis_es"] = get_linguistic_data(d.get("es", ""), nlp_es)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved enriched IDIEZ data to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
