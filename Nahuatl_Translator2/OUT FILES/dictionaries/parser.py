#!/usr/bin/env python3
"""
parser.py — Step 1: Digitizing IDIEZ PDF into Raw Nahuatl-centric JSON.

Focused exclusively on IDIEZ Modern Huasteca Nahuatl.
"""

import json
import re
import os
import sys
from pypdf import PdfReader

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(BASE_DIR, "sources")
IDIEZ_PDF = os.path.join(SOURCE_DIR, "IDIEZ_Dictionary.pdf")
RAW_IDIEZ_JSON = os.path.join(BASE_DIR, "raw_idiez.json")

def extract_text(pdf_path, start_page=0):
    print(f"Reading: {os.path.basename(pdf_path)}")
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for i in range(start_page, len(reader.pages)):
            full_text += reader.pages[i].extract_text() + "\n"
        return full_text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def parse_idiez(text):
    print("Digitizing IDIEZ format...")
    entries = {}
    
    # Pre-clean noise
    text = re.sub(r'©.*?IDIEZ.*?org\s+\d+\s*', ' ', text)
    text = re.sub(r'Diccionario Náhuatl.*?Inglés\s*', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    # Boundary pattern: headword followed by category
    boundary_pattern = re.compile(
        r'([a-zāēīōūáéíóúüñśš]+[0-9]*)\.\s+'
        r'(tlach\d*(?:/\d+)*|tlat|tlap|quen|quenun|adv|adj|prep|interj|conj|num)\.\s+'
    )

    matches = list(boundary_pattern.finditer(text))
    
    for i, match in enumerate(matches):
        headword = match.group(1).strip()
        category = match.group(2).strip()
        
        start_pos = match.end()
        end_pos = matches[i+1].start() if i+1 < len(matches) else len(text)
        
        entry_text = text[start_pos:end_pos].strip()
        
        # 1. Extract Past Tense (PANOC) for verbs
        past_tense = None
        if category.startswith('tlach'):
            past_match = re.match(r'^([^.0-9]+?)\.\s+', entry_text)
            if past_match:
                past_tense = past_match.group(1).strip()
                entry_text = entry_text[past_match.end():].strip()
        
        # Store as Raw Body
        clean_headword = re.sub(r'[0-9]+$', '', headword)
        if clean_headword not in entries:
            entries[clean_headword] = []
            
        entries[clean_headword].append({
            "cat": category,
            "past": past_tense,
            "raw_body": entry_text,
            "source": "IDIEZ"
        })

    return entries

def main():
    if os.path.exists(IDIEZ_PDF):
        text = extract_text(IDIEZ_PDF, start_page=1)
        if text:
            data = parse_idiez(text)
            with open(RAW_IDIEZ_JSON, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(data)} IDIEZ raw entries to {RAW_IDIEZ_JSON}")
    else:
        print(f"Error: {IDIEZ_PDF} not found.")

if __name__ == "__main__":
    main()
