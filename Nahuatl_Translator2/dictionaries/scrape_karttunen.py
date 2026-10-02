#!/usr/bin/env python3
"""
scrape_karttunen.py — Scrape Karttunen entries from nahuatl.wired-humanities.org

Fetches each entry at /content/<slug>, parses HTML, saves clean JSON.
Respects robots.txt crawl-delay of 10 seconds.
Resumes automatically from last saved position.

Output: dictionaries/karttunen_scraped.json
        dictionaries/karttunen_scrape_progress.json  (resume state)

Run on laptop (WSL2):
    cd ~/WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator
    source .venv/bin/activate
    pip install requests beautifulsoup4   # if not already installed
    python3 dictionaries/scrape_karttunen.py

Estimated time: ~14-17 hours for ~5,000 entries at 10s/request.
Use tmux to run overnight:
    tmux new-session -d -s scrape "python3 dictionaries/scrape_karttunen.py 2>&1 | tee scrape_karttunen.log"
"""

import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup

_HERE     = os.path.dirname(os.path.abspath(__file__))
OUT_FILE  = os.path.join(_HERE, "karttunen_scraped.json")
PROG_FILE = os.path.join(_HERE, "karttunen_scrape_progress.json")
SLUGS_SRC = os.path.join(_HERE, "raw_karttunen2.json")

BASE_URL    = "https://nahuatl.wired-humanities.org/content/"
CRAWL_DELAY = 10   # seconds — as specified in robots.txt
TIMEOUT     = 30   # HTTP request timeout

HEADERS = {
    "User-Agent": "NahuatlTranslatorResearch/1.0 (academic NLP project; contact ws@tcp-partners.com)",
    "Accept": "text/html",
}


# ---------------------------------------------------------------------------
# Slug generation
# ---------------------------------------------------------------------------

def headword_to_slug(hw: str) -> str:
    """Convert raw headword to URL slug: lowercase, strip punctuation/spaces."""
    s = hw.lower().strip()
    s = re.sub(r'[\(\)\-\·\.\s,;:\'\"]+', '', s)
    return s


def load_slugs() -> list[str]:
    """Load headwords from raw parse and convert to URL slugs."""
    with open(SLUGS_SRC, encoding="utf-8") as f:
        entries = json.load(f)
    slugs = sorted(set(
        headword_to_slug(e["headword_raw"])
        for e in entries
        if e.get("headword_raw") and len(e["headword_raw"]) > 1
    ))
    print(f"[slugs] {len(slugs):,} unique slugs from raw parse")
    return slugs


# ---------------------------------------------------------------------------
# HTML parsing
# ---------------------------------------------------------------------------

def get_field_text(soup: BeautifulSoup, label: str) -> str:
    """Find a <strong> tag containing label text and return following text."""
    for strong in soup.find_all("strong"):
        if label.lower() in strong.get_text(strip=True).lower():
            text_parts = []
            for sibling in strong.next_siblings:
                if sibling.name == "strong":
                    break
                if hasattr(sibling, "get_text"):
                    text_parts.append(sibling.get_text(" ", strip=True))
                elif isinstance(sibling, str):
                    text_parts.append(sibling.strip())
            result = " ".join(text_parts).strip()
            if result:
                return result
    return ""


def get_field_text_any(soup: BeautifulSoup, *labels: str) -> str:
    """Try multiple label strings in order; return first non-empty match.

    Also searches Drupal-style field wrappers (<div class="field-label">,
    <label>, <span class="field-label">) as a fallback beyond <strong> tags.
    """
    # 1. Try <strong> tag approach for each label
    for label in labels:
        val = get_field_text(soup, label)
        if val:
            return val

    # 2. Drupal field-label divs: <div class="field-label">Label</div>
    #    followed by <div class="field-items"> or <div class="field-item">
    for label in labels:
        for tag in soup.find_all(class_=re.compile(r'field.label', re.I)):
            if label.lower() in tag.get_text(strip=True).lower():
                # Value is in the next sibling with class field-items/field-item
                nxt = tag.find_next_sibling()
                if nxt:
                    val = nxt.get_text(" ", strip=True).strip()
                    if val:
                        return val

    # 3. <label> tags
    for label in labels:
        for tag in soup.find_all("label"):
            if label.lower() in tag.get_text(strip=True).lower():
                nxt = tag.find_next_sibling()
                if nxt:
                    val = nxt.get_text(" ", strip=True).strip()
                    if val:
                        return val

    # 4. Any element whose text contains the label, grab parent's remaining text
    for label in labels:
        for tag in soup.find_all(string=re.compile(re.escape(label), re.I)):
            parent = tag.parent
            if parent:
                # Get text after the label tag within the parent
                text_parts = []
                found = False
                for child in parent.children:
                    if found:
                        if hasattr(child, "get_text"):
                            text_parts.append(child.get_text(" ", strip=True))
                        elif isinstance(child, str):
                            text_parts.append(child.strip())
                    if hasattr(child, "get_text") and label.lower() in child.get_text(strip=True).lower():
                        found = True
                val = " ".join(text_parts).strip()
                if val:
                    return val

    return ""


def get_links_after(soup: BeautifulSoup, label: str) -> list[str]:
    """Find links following a <strong> label — used for cross-references."""
    for strong in soup.find_all("strong"):
        if label.lower() in strong.get_text(strip=True).lower():
            refs = []
            for sibling in strong.next_siblings:
                if sibling.name == "strong":
                    break
                if hasattr(sibling, "find_all"):
                    for a in sibling.find_all("a"):
                        t = a.get_text(strip=True)
                        if t:
                            refs.append(t)
            return refs
    return []


def parse_entry(slug: str, html: str) -> dict:
    """Parse a single entry page into a structured dict."""
    soup = BeautifulSoup(html, "html.parser")

    # Headword from <h2> (the entry title)
    h2 = soup.find("h2")
    headword_raw = h2.get_text(strip=True).rstrip(".") if h2 else slug

    # Core fields — try multiple label variants for robustness
    en       = get_field_text_any(soup,
                   "Principal English Translation",
                   "English Translation",
                   "English",
                   "Translation")
    ipa      = get_field_text_any(soup, "IPA", "Phonetics")
    kart_raw = get_field_text_any(soup, "Frances Karttunen", "Karttunen", "Definition")
    themes   = get_links_after(soup, "themes")
    xrefs    = get_links_after(soup, "See also") or get_links_after(soup, "Cross-ref")

    # Extract Spanish from Karttunen citation (pattern: "english / spanish")
    es = ""
    if kart_raw and "/" in kart_raw:
        parts = kart_raw.split("/", 1)
        # Spanish is after the slash — take up to first citation bracket
        es_raw = parts[1].strip()
        es_raw = re.sub(r'\[.*?\]', '', es_raw)   # strip citations
        es_raw = re.sub(r'\(.*?\)', '', es_raw)    # strip source refs
        es = re.sub(r'\s+', ' ', es_raw).strip().rstrip(".,;")

    # Attestation in Spanish (sometimes cleaner than Karttunen citation)
    es_attest = get_field_text(soup, "Attestations from sources in Spanish")
    if es_attest and not es:
        es = es_attest[:200]

    # Grammatical category — look in Karttunen raw text
    cat = None
    cat_match = re.search(
        r'\b(vt|vi|vrefl|n\b|adv|part|num|adj|pref|suf|redup|nonact|applic|caus)',
        kart_raw, re.IGNORECASE
    )
    if cat_match:
        cat = cat_match.group(1).lower()

    return {
        "slug":         slug,
        "headword":     headword_raw.lower(),
        "headword_raw": headword_raw,
        "en":           en,
        "es":           es,
        "ipa":          ipa,
        "cat":          cat,
        "karttunen_raw": kart_raw,
        "xrefs":        xrefs,
        "themes":       themes,
    }


# ---------------------------------------------------------------------------
# Progress tracking
# ---------------------------------------------------------------------------

def load_progress() -> tuple[dict, set]:
    """Load previously scraped entries and set of done slugs."""
    results = {}
    done = set()
    if os.path.isfile(OUT_FILE):
        with open(OUT_FILE, encoding="utf-8") as f:
            results = {e["slug"]: e for e in json.load(f)}
        done = set(results.keys())
        print(f"[resume] {len(done):,} entries already scraped")
    if os.path.isfile(PROG_FILE):
        with open(PROG_FILE) as f:
            prog = json.load(f)
        done.update(prog.get("failed", []))  # skip known 404s too
    return results, done


def save_progress(results: dict, failed: list) -> None:
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(results.values()), f, ensure_ascii=False, indent=2)
    with open(PROG_FILE, "w") as f:
        json.dump({"scraped": len(results), "failed": failed}, f, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n=== scrape_karttunen.py ===\n")

    slugs = load_slugs()
    results, done_slugs = load_progress()
    failed = []

    remaining = [s for s in slugs if s not in done_slugs]
    print(f"[queue]  {len(remaining):,} slugs remaining to fetch\n")

    session = requests.Session()
    session.headers.update(HEADERS)

    for i, slug in enumerate(remaining):
        url = BASE_URL + slug
        try:
            resp = session.get(url, timeout=TIMEOUT)
            if resp.status_code == 200:
                entry = parse_entry(slug, resp.text)
                results[slug] = entry
                print(f"  [{i+1}/{len(remaining)}] {slug:30s}  en={entry['en'][:40]!r}")
            elif resp.status_code == 404:
                failed.append(slug)
                print(f"  [{i+1}/{len(remaining)}] {slug:30s}  404 — skipped")
            else:
                print(f"  [{i+1}/{len(remaining)}] {slug:30s}  HTTP {resp.status_code} — retrying next run")
                failed.append(slug)
        except Exception as e:
            print(f"  [{i+1}/{len(remaining)}] {slug:30s}  ERROR: {e}")
            failed.append(slug)

        # Save progress every 50 entries
        if (i + 1) % 50 == 0:
            save_progress(results, failed)
            print(f"  --- checkpoint: {len(results):,} scraped, {len(failed):,} failed ---")

        time.sleep(CRAWL_DELAY)

    save_progress(results, failed)

    print(f"\n=== Done ===")
    print(f"  Scraped : {len(results):,}")
    print(f"  Failed  : {len(failed):,}")
    with_en = sum(1 for e in results.values() if e['en'])
    with_es = sum(1 for e in results.values() if e['es'])
    print(f"  With EN : {with_en:,}")
    print(f"  With ES : {with_es:,}")
    print(f"  Output  : {OUT_FILE}")


if __name__ == "__main__":
    main()
