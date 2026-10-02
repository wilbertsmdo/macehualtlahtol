#!/usr/bin/env python3
"""
parse_sullivan.py — Step 1: Parse Sullivan et al. 2016
"Tlahtolxitlauhcayotl Chicontepec" into raw JSON.

Huasteca Nahuatl monolingual dictionary (NAH→NAH definitions).
Dictionary entries begin on PDF page 16.

Output: dictionaries/raw_sullivan.json

Structure per entry:
  {
    "headword_diac": "āācalaqui",     # lowercase with diacritics
    "headword_norm": "aacalaqui",     # lookup key — no diacritics, no trailing digits
    "disambiguation": null,           # int (1,2,3...) or null
    "cat":  "tlach2",
    "prefix": "ni",                   # subject/object prefix requirement
    "raw_body": "Macehualli eli...",  # full definition text (Nahuatl)
    "example": "...",                 # first quoted example sentence
    "panoc": "āācalacqui",           # past tense form
    "achi": ["ĀCALAQUI (tlaomp.)"],  # related/cross-ref forms
    "miaq": null,                     # plural form
    "source": "Sullivan2016"
  }

Key parsing rules:
  - Page header (first line of each page = HEADWORD + page_number) is stripped.
  - Headword numbers = disambiguation (ĀAHCI1 ≠ ĀAHCI2); both under key "aahci".
  - Diacritics normalisation: ā→a, ē→e, ī→i, ō→o, ū→u (for headword_norm only).
  - Cross-reference entries ("Xiquitta X") stored with cat="xiquitta", ref=target.
"""

import json
import os
import re
import sys
import unicodedata

_HERE = os.path.dirname(os.path.abspath(__file__))
DRIVE_PDF_ID = "1R4Xjxmi13GQ8Nf1hDQVAG3sx4pwEhc81"
LOCAL_PDF    = os.path.join(_HERE, "sources", "sullivan_2016.pdf")
OUTPUT_JSON  = os.path.join(_HERE, "raw_sullivan.json")

# First dictionary page (1-indexed in the PDF viewer, 0-indexed for pypdf)
DICT_START_PAGE = 15   # PDF page 16 = index 15


# ── Normalisation ─────────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    """Lowercase + strip diacritics (macrons ā→a, accents á→a, etc.)."""
    s = s.lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


# ── Category codes (Sullivan = same as IDIEZ) ─────────────────────────────────

_CATS = (
    "tlach1", "tlach2", "tlach3", "tlach4",
    "tlach.axahci",   # not-yet-achieved verb
    "tlach",          # generic verb (no class number)
    "tlaten",         # particle / functional word
    "tlat",           # noun
    "pil",            # diminutive / pronoun
    "tlaeli",         # adjective
    "tlalocotzolli",  # abbreviation
    "tlachiuhca",     # agentive noun
    "miaq",           # plural-only entry (rare at headword level)
)

_CAT_RE = re.compile(
    r'\b(tlach[1-4]?(?:\.axahci)?|tlaten|tlat|pil|tlaeli|tlalocotzolli|tlachiuhca)\b'
)

# Headword: 2+ uppercase Nahuatl letters (with diacritics), optional trailing digit
_HEAD_RE = re.compile(
    r'([ĀĒĪŌŪA-ZÁÉÍÓÚ][ĀĒĪŌŪA-ZÁÉÍÓÚ]+[0-9]?)'
    r'\.\s+'
    r'(tlach[1-4]?(?:\.axahci)?|tlaten|tlat|pil|tlaeli|tlalocotzolli|tlachiuhca)'
    r'\.'
)

# Cross-reference entry: HEADWORD. Xiquitta TARGET.
_XIQUITTA_RE = re.compile(
    r'([ĀĒĪŌŪA-ZÁÉÍÓÚ][ĀĒĪŌŪA-ZÁÉÍÓÚ]+[0-9]?)\.\s+Xiquitta\s+([^\.\n]+)\.'
)

# Page header: first line of each extracted page block
# Pattern: ALL-CAPS word (with diacritics) immediately followed by digit(s)
_PAGE_HEADER_RE = re.compile(
    r'^([ĀĒĪŌŪA-ZÁÉÍÓÚ][ĀĒĪŌŪA-ZÁÉÍÓÚ\s]+?)\s*[0-9]+\s*$'
)


# ── PDF download / load ───────────────────────────────────────────────────────

def _ensure_pdf():
    """Download PDF from Google Drive if not cached locally."""
    if os.path.exists(LOCAL_PDF):
        print(f"[pdf] Using cached: {LOCAL_PDF}")
        return

    print("[pdf] Downloading Sullivan 2016 from Google Drive...")
    import sys
    # Resolve token path same way as other scripts
    if os.path.isdir("/storage/self/primary"):
        token_path = "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json"
    else:
        token_path = os.path.join(os.path.dirname(_HERE), "token.json")

    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    with open(token_path) as f:
        tok = json.load(f)
    creds = Credentials(
        token=tok["token"], refresh_token=tok["refresh_token"],
        token_uri=tok["token_uri"], client_id=tok["client_id"],
        client_secret=tok["client_secret"], scopes=tok["scopes"],
    )
    if creds.expired:
        creds.refresh(Request())

    service = build("drive", "v3", credentials=creds)
    data = service.files().get_media(fileId=DRIVE_PDF_ID).execute()

    os.makedirs(os.path.dirname(LOCAL_PDF), exist_ok=True)
    with open(LOCAL_PDF, "wb") as f:
        f.write(data)
    print(f"[pdf] Saved {len(data)//1024} KB → {LOCAL_PDF}")


# ── Text extraction ───────────────────────────────────────────────────────────

def _extract_pages(pdf_path: str, start_page: int) -> list[str]:
    """Return list of page text strings starting from start_page (0-indexed)."""
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    pages = []
    for i in range(start_page, len(reader.pages)):
        pages.append(reader.pages[i].extract_text() or "")
    print(f"[pdf] Extracted {len(pages)} pages (starting at PDF page {start_page + 1})")
    return pages


def _strip_page_header(text: str) -> str:
    """Remove the running header (first line = HEADWORD + page_number)."""
    lines = text.split("\n")
    if lines:
        first = lines[0].strip()
        # Header pattern: all-caps (with diacritics) + optional space + digit(s) at end
        if re.match(r'^[ĀĒĪŌŪA-ZÁÉÍÓÚ][ĀĒĪŌŪA-ZÁÉÍÓÚ\s\-]+\s*[0-9]+\s*$', first):
            return "\n".join(lines[1:])
    return text


def _merge_pages(pages: list[str]) -> str:
    """Strip headers and join all pages into one text block."""
    clean = [_strip_page_header(p) for p in pages]
    return " ".join(" ".join(c.split()) for c in clean)


# ── Entry parsing ─────────────────────────────────────────────────────────────

def _extract_field(text: str, label: str) -> tuple[str | None, str]:
    """
    Find 'label. VALUE.' in text, return (value, text_with_field_removed).
    label examples: 'panoc', 'achi', 'miaq'
    """
    # Match label followed by content up to next label or end
    pattern = re.compile(
        r'\b' + re.escape(label) + r'\.\s+([^.]+(?:\([^)]*\)[^.]*)?)\.'
    )
    m = pattern.search(text)
    if m:
        value = m.group(1).strip()
        text = text[:m.start()] + text[m.end():]
        return value, text
    return None, text


def _extract_example(text: str) -> tuple[str | None, str]:
    """Extract first quoted example sentence."""
    m = re.search(r'"([^"]+)"', text)
    if m:
        return m.group(1).strip(), text
    return None, text


def _parse_headword(hw_raw: str) -> tuple[str, str, int | None]:
    """
    From raw matched headword (e.g. 'ĀAHCI2') return:
      (headword_diac, headword_norm, disambiguation)
    headword_diac: lowercase with diacritics, no trailing digit
    headword_norm: no diacritics, no trailing digit
    disambiguation: trailing digit if present, else None
    """
    m = re.match(r'^([^0-9]+)([0-9]?)$', hw_raw)
    base_upper = m.group(1) if m else hw_raw
    digit_str  = m.group(2) if m else ""
    disambig   = int(digit_str) if digit_str else None
    diac       = base_upper.lower()
    norm       = _norm(base_upper)
    return diac, norm, disambig


def parse_entries(full_text: str) -> dict:
    """
    Parse all entries from the merged text.
    Returns dict keyed by headword_norm, value = list of entry dicts.
    """
    entries: dict[str, list] = {}

    # ── Cross-reference entries first (they don't have a category code) ───────
    for m in _XIQUITTA_RE.finditer(full_text):
        hw_raw  = m.group(1)
        target  = m.group(2).strip()
        diac, norm, disambig = _parse_headword(hw_raw)
        entry = {
            "headword_diac":   diac,
            "headword_norm":   norm,
            "disambiguation":  disambig,
            "cat":             "xiquitta",
            "ref":             target,
            "prefix":          None,
            "raw_body":        f"Xiquitta {target}",
            "example":         None,
            "panoc":           None,
            "achi":            None,
            "miaq":            None,
            "source":          "Sullivan2016",
        }
        if norm not in entries:
            entries[norm] = []
        entries[norm].append(entry)

    # ── Main entries ──────────────────────────────────────────────────────────
    matches = list(_HEAD_RE.finditer(full_text))
    print(f"[parse] Found {len(matches)} main entry boundaries")

    for i, m in enumerate(matches):
        hw_raw   = m.group(1)
        cat      = m.group(2)
        diac, norm, disambig = _parse_headword(hw_raw)

        start  = m.end()
        end    = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        body   = full_text[start:end].strip()

        # Extract structured sub-fields
        panoc_raw, body = _extract_field(body, "panoc")
        achi_raw,  body = _extract_field(body, "achi")
        miaq_raw,  body = _extract_field(body, "miaq")
        example, _      = _extract_example(body)

        # Subject/object prefix: short word(s) before first sentence
        prefix = None
        pfx_m = re.match(r'^((?:ni|nic|qui|nimo|nech|mitz|tech|quin|an|ti|zan[^.]+?)\s*\.)\s+', body)
        if pfx_m:
            prefix = pfx_m.group(1).rstrip(".")
            body   = body[pfx_m.end():]

        entry = {
            "headword_diac":  diac,
            "headword_norm":  norm,
            "disambiguation": disambig,
            "cat":            cat,
            "prefix":         prefix,
            "raw_body":       body.strip(),
            "example":        example,
            "panoc":          panoc_raw,
            "achi":           achi_raw,
            "miaq":           miaq_raw,
            "source":         "Sullivan2016",
        }

        if norm not in entries:
            entries[norm] = []
        entries[norm].append(entry)

    return entries


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n=== parse_sullivan.py ===\n")

    _ensure_pdf()

    pages     = _extract_pages(LOCAL_PDF, DICT_START_PAGE)
    full_text = _merge_pages(pages)
    print(f"[text] Merged text length: {len(full_text):,} chars")

    entries = parse_entries(full_text)
    print(f"[parse] Total headword keys: {len(entries):,}")
    total_entries = sum(len(v) for v in entries.values())
    print(f"[parse] Total entries (incl. disambiguation): {total_entries:,}")

    # Sample output
    sample_keys = list(entries.keys())[:5]
    print("\n[sample]")
    for k in sample_keys:
        for e in entries[k]:
            print(f"  {e['headword_diac']} [{e['headword_norm']}]"
                  f" disambig={e['disambiguation']} cat={e['cat']}"
                  f" panoc={e['panoc']}")
            print(f"    body: {e['raw_body'][:80]}...")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"\n[output] Saved → {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
