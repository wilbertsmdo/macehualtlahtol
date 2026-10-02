#!/usr/bin/env python3
"""
parse_karttunen.py — Parse Karttunen 1992 "An Analytical Dictionary of Nahuatl"

Handles the two-column PDF layout by extracting left and right columns
separately per page, then joining them before parsing entries.

Entry format in the dictionary:
  HEADWORD [gram-info] english-def / spanish-def [(citations)] [See CROSS-REF.]

Output: dictionaries/raw_karttunen2.json
  {
    "headword": "acec-tli",          # lowercase, normalized
    "headword_raw": "ACEC-TLI",      # original caps
    "cat": "n",                      # grammatical category (if found)
    "pret": "-TEC",                  # preterite form (if found)
    "en": "icicles, ice in trees",   # English definition
    "es": "hielo en arbol",          # Spanish definition
    "refs": ["See A-TL", "See CAX(I)-TL"],   # cross-references
    "citations": ["(2)Zp.67"],       # source citations
    "raw": "ACEC-TLI icicles ... hielo en arbol (Z)[(2)Zp.67]"
  }

Run:
  /data/data/com.termux/files/usr/bin/python3 dictionaries/parse_karttunen.py
"""

import json
import os
import re

try:
    import pdfplumber
except ImportError:
    print("Install pdfplumber: pip3 install pdfplumber")
    raise

_HERE   = os.path.dirname(os.path.abspath(__file__))
PDF_IN  = "/storage/self/primary/Download/Karttunen 1992 An Analytical Dictionary of Nahuatl.pdf"
OUT     = os.path.join(_HERE, "raw_karttunen2.json")

# Dictionary content starts at page 18 (0-indexed), ends at ~page 185
DICT_START_PAGE = 17   # 0-indexed (page 18 in the book = "A" entries)
DICT_END_PAGE   = 185  # 0-indexed

# Grammatical category abbreviations used in Karttunen
GRAM_CATS = {
    "vt": "transitive verb",
    "vi": "intransitive verb",
    "vrefl": "reflexive verb",
    "n": "noun",
    "adv": "adverb",
    "part": "particle",
    "num": "numeral",
    "adj": "adjective",
    "pref": "prefix",
    "suf": "suffix",
    "redup": "reduplicated",
    "nonact": "nonactive",
    "applic": "applicative",
    "caus": "causative",
    "indef": "indefinite",
}

# Running header pattern (page numbers + partial headwords at top of columns)
HEADER_RE = re.compile(r'^\d+\s+[A-Z][\w\-\.]+\s*$')

# Headword line: starts with 2+ uppercase letters (possibly with parens/hyphens)
HEADWORD_RE = re.compile(
    r'^([A-ZÁÉÍÓÚ][A-ZÁÉÍÓÚ\(\)\-\·\.]{1,}(?:\s[A-ZÁÉÍÓÚ\(\)\-]{1,})?)\s+'
    r'(.*)'
)

# Citation pattern: [(3)Xp.25] or (Z) or [Cf.98]
CITATION_RE = re.compile(r'\[[\(\)a-zA-Z0-9\.,\s\-\+\/\:]+\]|\([A-Za-z]+\)')

# Preterite pattern
PRET_RE = re.compile(r'pret[\.:]?\s*:?\s*([A-ZÁÉÍÓÚ\(\)\-]+)', re.IGNORECASE)

# Cross-reference pattern
XREF_RE = re.compile(r'See\s+([A-ZÁÉÍÓÚ\(\)\-\,\s]+?)(?:\.|$)', re.IGNORECASE)


GUTTER   = 415   # x-coordinate separating left and right columns
LINE_TOL = 3     # pixels: chars within this vertical distance = same line
SPACE_GAP = 3    # pixels: gap between chars that implies a space


def chars_to_text(char_list):
    """
    Reconstruct text from character objects with position data.
    Groups chars into lines by top-coordinate proximity, inserts spaces
    where horizontal gaps between chars exceed SPACE_GAP.
    """
    if not char_list:
        return ""
    char_list = sorted(char_list, key=lambda c: (round(c['top'] / LINE_TOL) * LINE_TOL, c['x0']))
    lines, cur_top, cur_x1, cur_line = [], None, None, []
    for c in char_list:
        t = round(c['top'] / LINE_TOL) * LINE_TOL
        if cur_top is None or abs(t - cur_top) > LINE_TOL * 2:
            if cur_line:
                lines.append(''.join(cur_line))
            cur_top, cur_x1, cur_line = t, c['x1'], [c['text']]
        else:
            gap = c['x0'] - cur_x1 if cur_x1 is not None else 0
            if gap > SPACE_GAP:
                cur_line.append(' ')
            cur_line.append(c['text'])
            cur_x1 = c['x1']
    if cur_line:
        lines.append(''.join(cur_line))
    return '\n'.join(lines)


def clean_line(line):
    """Remove running headers and page number artifacts."""
    line = line.strip()
    if re.match(r'^\d+$', line):
        return ""
    if HEADER_RE.match(line):
        return ""
    return line


def extract_page_text(page):
    """Extract left then right column using character-level bounding boxes."""
    chars = page.chars
    left_chars  = [c for c in chars if c['x0'] < GUTTER]
    right_chars = [c for c in chars if c['x0'] >= GUTTER]

    all_lines = []
    for col_chars in (left_chars, right_chars):
        for line in chars_to_text(col_chars).split("\n"):
            cl = clean_line(line)
            if cl:
                all_lines.append(cl)
    return "\n".join(all_lines)


def split_en_es(body):
    """Split 'english / spanish' body into (en, es) parts."""
    if "/" in body:
        parts = body.split("/", 1)
        return parts[0].strip(), parts[1].strip()
    return body.strip(), ""


def parse_entry_body(body_text):
    """Extract cat, pret, en, es, citations, xrefs from a raw entry body."""
    # Extract citations
    citations = CITATION_RE.findall(body_text)
    body_clean = CITATION_RE.sub("", body_text).strip()

    # Extract preterite
    pret_match = PRET_RE.search(body_clean)
    pret = pret_match.group(1) if pret_match else None
    if pret_match:
        body_clean = body_clean[:pret_match.start()].strip() + " " + body_clean[pret_match.end():].strip()

    # Extract grammatical category (appears early in the body)
    cat = None
    for abbr in sorted(GRAM_CATS.keys(), key=len, reverse=True):
        pat = re.compile(r'\b' + re.escape(abbr) + r'\b', re.IGNORECASE)
        if pat.search(body_clean[:40]):
            cat = abbr
            break

    # Extract cross-references
    xrefs = []
    for m in XREF_RE.finditer(body_clean):
        xrefs.append("See " + m.group(1).strip().rstrip("."))
    body_clean = XREF_RE.sub("", body_clean).strip()

    # Split English / Spanish
    en, es = split_en_es(body_clean)

    # Clean up en/es
    en = re.sub(r'\s+', ' ', en).strip().rstrip(".,;")
    es = re.sub(r'\s+', ' ', es).strip().rstrip(".,;")

    return {
        "cat":       cat,
        "pret":      pret,
        "en":        en,
        "es":        es,
        "citations": [c.strip() for c in citations],
        "refs":      xrefs,
    }


def parse_entries(full_text):
    """Parse all dictionary entries from the full extracted text."""
    entries = []
    current_headword = None
    current_raw_lines = []

    def flush():
        if not current_headword:
            return
        raw = " ".join(current_raw_lines).strip()
        parsed = parse_entry_body(raw)
        entries.append({
            "headword":     current_headword.lower(),
            "headword_raw": current_headword,
            **parsed,
            "raw": raw,
        })

    for line in full_text.split("\n"):
        m = HEADWORD_RE.match(line)
        if m:
            flush()
            current_headword = m.group(1).strip()
            current_raw_lines = [m.group(2).strip()]
        elif current_headword:
            current_raw_lines.append(line.strip())

    flush()
    return entries


def main():
    print(f"\n=== parse_karttunen.py ===\n")
    print(f"[pdf]  {PDF_IN}")

    with pdfplumber.open(PDF_IN) as pdf:
        total_pages = len(pdf.pages)
        print(f"[pdf]  {total_pages} pages total")
        print(f"[pdf]  Parsing pages {DICT_START_PAGE+1}–{DICT_END_PAGE+1} (dictionary content)\n")

        all_text_parts = []
        for i in range(DICT_START_PAGE, min(DICT_END_PAGE + 1, total_pages)):
            page_text = extract_page_text(pdf.pages[i])
            all_text_parts.append(page_text)
            if (i - DICT_START_PAGE) % 20 == 0:
                pct = (i - DICT_START_PAGE) / (DICT_END_PAGE - DICT_START_PAGE) * 100
                print(f"  page {i+1}  ({pct:.0f}%)")

    full_text = "\n".join(all_text_parts)
    print(f"\n[parse] Extracted {len(full_text):,} chars of text")

    entries = parse_entries(full_text)
    print(f"[parse] Found {len(entries):,} entries")

    # Stats
    with_es  = sum(1 for e in entries if e["es"])
    with_cat = sum(1 for e in entries if e["cat"])
    with_ref = sum(1 for e in entries if e["refs"])
    print(f"[stats] With Spanish def : {with_es:,}")
    print(f"[stats] With gram. cat   : {with_cat:,}")
    print(f"[stats] With cross-refs  : {with_ref:,}")

    # Sample output
    print(f"\n[sample] First 5 entries:")
    for e in entries[:5]:
        print(f"  {e['headword_raw']:25s} en={e['en'][:40]!r:42s} es={e['es'][:40]!r}")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"\n[done]  Saved {len(entries):,} entries → {OUT}")


if __name__ == "__main__":
    main()
