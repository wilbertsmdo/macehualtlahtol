#!/usr/bin/env python3
"""
translate_and_learn.py — Self-improving NAH→ES translation loop

For each processed row:
  Col B  (Nahuatl source)      → input
  Col E  (Claude draft)        → auto: translation
  Col F  (BLEU score)          → auto: similarity vs col C gold (when gold exists)
  Col G  (Tlatocopa / delta)   → auto: key difference between E and C (Claude)
  Col H  (Tlahtol Auto)        → auto: generalised rule derived from delta (Claude)
  Col I  (Tlahtol Human)       → EMPTY — left for human correction in sheet

Dynamic few-shot:  selects top-BLEU rows from col F on each run (falls back to
                   DEFAULT_FEW_SHOT_ROWS when no scored data exists yet).
Dynamic rules:     reads col I (human-verified) then col H (auto) and injects
                   up to MAX_RULES into the system prompt each run.

Usage:
    /data/data/com.termux/files/usr/bin/python3 translate_and_learn.py
"""

import json, re, time, math, os
from collections import Counter
from anthropic import Anthropic
from morphology import get_hints as _morph_hints
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import gspread

_HERE = os.path.dirname(os.path.abspath(__file__))

def _token_path():
    env = os.environ.get("GOOGLE_TOKEN_PATH")
    if env:
        return env
    if os.path.isdir("/storage/self/primary"):
        return "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json"
    return os.path.join(_HERE, "token.json")


# ── Retry wrapper ─────────────────────────────────────────────────────────────
def with_retry(fn, retries=4, base_delay=5):
    """Call fn(), retrying on any network/transport error with exponential backoff."""
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = base_delay * (2 ** attempt)
            print(f"    [retry {attempt+1}/{retries-1}] {type(e).__name__}: {e} — waiting {wait}s")
            time.sleep(wait)


# ── Config ────────────────────────────────────────────────────────────────────
TOKEN_PATH     = _token_path()
SPREADSHEET_ID = "1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw"   # Eduardo
WORKSHEET      = "Eduardo"
DICT_PATH      = os.path.join(_HERE, "dictionaries", "enriched_idiez.json")
SULLIVAN_PATH  = os.path.join(_HERE, "dictionaries", "normalized_sullivan.json")
GLOSSARY_PATH  = os.path.join(_HERE, "nah_es_glossary.json")
MODEL          = "claude-haiku-4-5"

# Row range to process (sheet row numbers, 1-indexed, end is exclusive)
PROCESS_START  = 4    # first data row
PROCESS_END    = 302  # last data row + 1 (process rows 4–301 only)

GOLD_START     = 4    # first row that has gold Spanish in col C
GOLD_END       = 301  # last  row that has gold Spanish in col C

MAX_DICT_HINTS          = 8
FEW_SHOT_N              = 5
MAX_RULES               = 10
DEFAULT_FEW_SHOT_ROWS   = list(range(5, 10))   # fallback when no BLEU data yet
OVERWRITE               = False                 # skip rows that already have col E

# ── Column layout (1-indexed for gspread) ────────────────────────────────────
COL_A, COL_B, COL_C, COL_D = 1, 2, 3, 4
COL_E, COL_F, COL_G, COL_H, COL_I = 5, 6, 7, 8, 9

HEADER_ROW = 3
HEADERS = [
    "",                                       # A — section label
    "Nahuatlahtolli",                         # B — Nahuatl source
    "Coyotlahtolli",                          # C — gold Spanish (human)
    "Tlahtlaniliztli Zo Yancuic Tlahtolli",   # D — vocab / grammar notes
    "Claude Tlahtoltlanextilli",              # E — Claude draft translation
    "BLEU",                                   # F — similarity score vs col C
    "Tlatocopa",                              # G — key difference (Claude)
    "Tlahtol (Auto)",                         # H — derived rule, automated
    "Tlahtol (Human)",                        # I — corrected rule, human
]


# ── Print helpers ─────────────────────────────────────────────────────────────
def section(title):
    bar = "─" * 60
    print(f"\n{bar}\n  {title}\n{bar}")

def subhead(title):
    print(f"\n  ── {title}")


# ── Auth ──────────────────────────────────────────────────────────────────────
def connect():
    with open(TOKEN_PATH) as f:
        tok = json.load(f)
    creds = Credentials(
        token=tok["token"], refresh_token=tok["refresh_token"],
        token_uri=tok["token_uri"], client_id=tok["client_id"],
        client_secret=tok["client_secret"], scopes=tok["scopes"],
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        tok["token"] = creds.token
        with open(TOKEN_PATH, "w") as f:
            json.dump(tok, f, indent=2)
    gc = gspread.authorize(creds)
    return gc.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET)


# ── Sheet headers ─────────────────────────────────────────────────────────────
def update_sheet_headers(ws):
    ws.update(values=[HEADERS], range_name=f"A{HEADER_ROW}:I{HEADER_ROW}")
    print(f"  Headers written to row {HEADER_ROW} (cols A–I)")


# ── Glossary ──────────────────────────────────────────────────────────────────
def load_glossary():
    if not os.path.exists(GLOSSARY_PATH):
        return []
    with open(GLOSSARY_PATH) as f:
        return json.load(f)

def glossary_hints(sentence, glossary):
    """Return verified NAH→ES glossary hits for tokens in sentence (via morphology)."""
    from morphology import decompose, _norm
    tokens = re.findall(r"[a-záéíóúāēīōū]+", sentence.lower())
    index = {_norm(e["nahuatl"]): e for e in glossary}
    seen, hints = set(), []
    for token in tokens:
        for candidate in decompose(token):
            key = _norm(candidate)
            if key in index and key not in seen:
                seen.add(key)
                e = index[key]
                note = f" ({e['note']})" if e.get("note") else ""
                hints.append(f"  [GLOSARIO] {e['nahuatl']} → {e['spanish']}{note}")
                break
    return hints


# ── Dictionary ────────────────────────────────────────────────────────────────
def load_dictionary():
    with open(DICT_PATH) as f:
        return json.load(f)

def load_sullivan():
    if not os.path.exists(SULLIVAN_PATH):
        return {}
    with open(SULLIVAN_PATH) as f:
        return json.load(f)

def sullivan_hints(sentence, sullivan_dict):
    """Return Nahuatl-definition hints from Sullivan 2016 for tokens in sentence."""
    from morphology import decompose, _norm
    tokens = re.findall(r"[a-záéíóúāēīōū]+", sentence.lower())
    seen, hints = set(), []
    for token in tokens:
        for candidate in decompose(token):
            key = _norm(candidate)
            if key in sullivan_dict and key not in seen:
                seen.add(key)
                entries = sullivan_dict[key]
                if not entries:
                    continue
                e = entries[0]
                nah_def = (e.get("nah_def") or "").strip()
                cat = e.get("cat", "")
                if nah_def and len(nah_def) > 5:
                    hints.append(f"  {e.get('headword_diac', key)} ({cat}): {nah_def[:120]}")
                break
        if len(hints) >= 4:
            break
    return hints

def dict_hints(sentence, dictionary):
    tokens = re.findall(r"[a-záéíóúāēīōū]+", sentence.lower())
    seen, hints = set(), []
    for token in tokens:
        # First try exact match, then morphological decomposition
        morph_hits = _morph_hints(token, dictionary)
        for hit in morph_hits:
            if hit not in seen:
                seen.add(hit)
                hints.append(f"  {hit}")
        if not morph_hits and token not in seen:
            seen.add(token)
            entries = dictionary.get(token)
            if isinstance(entries, list) and entries:
                defs = entries[0].get("definitions", [])
                if defs:
                    es_def = defs[0].get("es", "").strip()
                    if es_def:
                        hints.append(f"  {token} → {es_def}")
        if len(hints) >= MAX_DICT_HINTS:
            break
    return hints


# ── BLEU score (unigram + bigram, no external deps) ──────────────────────────
def bleu(reference, hypothesis):
    def ngrams(tokens, n):
        return [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

    ref  = reference.lower().split()
    hyp  = hypothesis.lower().split()
    if not hyp or not ref:
        return 0.0

    # unigram precision
    ref1 = Counter(ref)
    hyp1 = Counter(hyp)
    p1 = sum(min(hyp1[t], ref1[t]) for t in hyp1) / len(hyp)

    # bigram precision
    ref2 = Counter(ngrams(ref, 2))
    hyp2 = Counter(ngrams(hyp, 2))
    if hyp2:
        p2 = sum(min(hyp2[b], ref2[b]) for b in hyp2) / len(hyp2)
    else:
        p2 = 0.0

    # brevity penalty
    bp = min(1.0, len(hyp) / max(len(ref), 1))

    if p1 == 0:
        return 0.0
    geo = math.exp(0.5 * math.log(p1) + 0.5 * math.log(p2)) if p2 > 0 else p1 * 0.5
    return round(bp * geo, 3)


# ── Dynamic few-shot selection ────────────────────────────────────────────────
def load_few_shot(ws):
    """Select top-BLEU rows from col F as few-shot examples.
    Falls back to DEFAULT_FEW_SHOT_ROWS when no scored data exists."""
    subhead("Loading few-shot examples")

    # Read cols B, C, F for the gold range
    data = ws.get(f"B{GOLD_START}:F{GOLD_END}")
    scored = []
    for i, row in enumerate(data):
        nah  = row[0].strip() if len(row) > 0 else ""
        gold = row[1].strip() if len(row) > 1 else ""
        f_val = row[4].strip() if len(row) > 4 else ""
        if nah and gold and f_val:
            try:
                scored.append((float(f_val), nah, gold))
            except ValueError:
                pass

    if scored:
        scored.sort(reverse=True)
        examples = [(nah, gold) for _, nah, gold in scored[:FEW_SHOT_N]]
        print(f"    {len(examples)} examples from top-BLEU rows (best BLEU: {scored[0][0]:.3f})")
    else:
        # fallback: fixed rows
        fs_data = ws.get(f"B{DEFAULT_FEW_SHOT_ROWS[0]}:C{DEFAULT_FEW_SHOT_ROWS[-1]}")
        examples = [
            (r[0].strip(), r[1].strip())
            for r in fs_data
            if len(r) >= 2 and r[0].strip() and r[1].strip()
        ]
        print(f"    {len(examples)} examples from default rows {DEFAULT_FEW_SHOT_ROWS[0]}–{DEFAULT_FEW_SHOT_ROWS[-1]} (no BLEU data yet)")

    return examples


# ── Dynamic rule loading ──────────────────────────────────────────────────────
RULES_FILE = os.path.join(_HERE, "translation_rules.json")

def load_rules(ws):
    """Load rules from translation_rules.json (shared, cross-document).
    Falls back to per-sheet col H/I if the file doesn't exist yet."""
    subhead("Loading translation rules")

    # ── Primary: shared rules file ────────────────────────────────────────────
    try:
        with open(RULES_FILE) as f:
            data = json.load(f)
        all_rules = data.get("rules", [])
        # Human-verified first, then by BLEU — already sorted by extract_rules.py
        rules = [r["rule"] for r in all_rules[:MAX_RULES]]
        human_n = sum(1 for r in all_rules[:MAX_RULES] if r["human_verified"])
        print(f"    {len(rules)} rules from translation_rules.json "
              f"({human_n} human-verified, {len(rules)-human_n} auto) "
              f"[{len(all_rules)} total in file]")
        return rules
    except FileNotFoundError:
        pass

    # ── Fallback: per-sheet col H/I ───────────────────────────────────────────
    print(f"    translation_rules.json not found — falling back to per-sheet cols H/I")
    sheet_data = ws.get(f"H{GOLD_START}:I{GOLD_END}")
    rules = []
    seen = set()
    for row in sheet_data:
        human = row[1].strip() if len(row) > 1 else ""
        auto  = row[0].strip() if len(row) > 0 else ""
        rule  = human if human else auto
        if rule and rule not in seen:
            seen.add(rule)
            rules.append(rule)
        if len(rules) >= MAX_RULES:
            break
    print(f"    {len(rules)} rules from sheet cols H/I")
    return rules


# ── System prompt ─────────────────────────────────────────────────────────────
def build_system(rules):
    base = (
        "Eres un experto en traducción del náhuatl huasteco (documentado por el IDIEZ) al español. "
        "Traduce cada oración al español natural y fluido de México. "
        "Responde ÚNICAMENTE con la traducción — sin notas, sin explicaciones."
    )
    if rules:
        rule_block = "\n".join(f"- {r}" for r in rules)
        return base + f"\n\nReglas de traducción aprendidas:\n{rule_block}"
    return base


# ── Translation call ──────────────────────────────────────────────────────────
def translate(client, system, few_shot_msgs, nah, dictionary, glossary=None, sullivan=None):
    g_hints = glossary_hints(nah, glossary) if glossary else []
    d_hints  = dict_hints(nah, dictionary)
    s_hints  = sullivan_hints(nah, sullivan) if sullivan else []
    hint_block = ""
    if g_hints:
        hint_block += "\n\n[Glosario verificado]\n" + "\n".join(g_hints)
    if d_hints:
        hint_block += "\n\n[Diccionario IDIEZ]\n" + "\n".join(d_hints)
    if s_hints:
        hint_block += "\n\n[Sullivan 2016 — Huasteca Nahuatl]\n" + "\n".join(s_hints)
    messages = few_shot_msgs + [
        {"role": "user", "content": f"Traduce al español: {nah}{hint_block}"}
    ]
    resp = with_retry(lambda: client.messages.create(
        model=MODEL, max_tokens=512, system=system, messages=messages
    ))
    return resp.content[0].text.strip()


# ── Delta + rule analysis (single call) ──────────────────────────────────────
def analyse(client, nah, gold, draft):
    """Compare gold vs draft; return (delta_sentence, rule_sentence) as strings."""
    prompt = (
        f"Náhuatl: {nah}\n"
        f"Traducción correcta: {gold}\n"
        f"Traducción automática: {draft}\n\n"
        "Responde en JSON con exactamente dos campos:\n"
        '  "delta": una oración que describe la diferencia principal entre las dos traducciones\n'
        '  "rule":  una regla de traducción general y concisa (máximo 20 palabras) derivada del error\n'
        "Solo el JSON, sin texto adicional."
    )
    resp = with_retry(lambda: client.messages.create(
        model=MODEL, max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    ))
    raw = resp.content[0].text.strip()
    # Strip markdown code fences if Claude wraps the JSON
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw).strip()
    try:
        obj = json.loads(raw)
        return obj.get("delta", "").strip(), obj.get("rule", "").strip()
    except json.JSONDecodeError:
        return raw[:200], ""


# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    section("TRANSLATE AND LEARN — NAH→ES Self-Improving Loop")
    print(f"  Sheet    : {WORKSHEET}")
    print(f"  Rows     : {PROCESS_START}–{PROCESS_END - 1}")
    print(f"  Model    : {MODEL}")
    print(f"  Overwrite: {OVERWRITE}")

    section("Setup")
    subhead("Connecting to sheet and loading dictionary")
    ws         = with_retry(connect, retries=6, base_delay=10)
    client     = Anthropic()
    dictionary = load_dictionary()
    glossary   = load_glossary()
    sullivan   = load_sullivan()
    print(f"    Dictionary: {len(dictionary):,} entries")
    print(f"    Glossary:   {len(glossary):,} verified entries")
    print(f"    Sullivan:   {len(sullivan):,} headword keys")

    section("Sheet Headers")
    update_sheet_headers(ws)

    section("Learning Data")
    few_shot = load_few_shot(ws)
    rules    = load_rules(ws)
    system   = build_system(rules)

    few_shot_msgs = []
    for nah_ex, es_ex in few_shot:
        few_shot_msgs.append({"role": "user",      "content": f"Traduce al español: {nah_ex}"})
        few_shot_msgs.append({"role": "assistant", "content": es_ex})

    # Read target rows: cols B, C, E
    section(f"Processing Rows {PROCESS_START}–{PROCESS_END - 1}")
    row_range = list(range(PROCESS_START, PROCESS_END))
    data = ws.get(f"B{PROCESS_START}:E{PROCESS_END - 1}")
    while len(data) < len(row_range):
        data.append(["", "", "", ""])

    stats = {"translated": 0, "scored": 0, "analysed": 0, "skipped": 0}

    for i, row_num in enumerate(row_range):
        row   = data[i]
        nah   = row[0].strip() if len(row) > 0 else ""
        gold  = row[1].strip() if len(row) > 1 else ""
        # col C is index 1, col D index 2, col E index 3 in B:E range
        draft_existing = row[3].strip() if len(row) > 3 else ""

        print(f"\n  Row {row_num}")

        if not nah:
            print(f"    (empty col B — skipping)")
            stats["skipped"] += 1
            continue

        if gold.upper() in ("SKIP", "SALTAR"):
            print(f"    (col C = {gold} — skipping)")
            stats["skipped"] += 1
            continue

        if draft_existing and not OVERWRITE:
            print(f"    col E already filled — skipping (set OVERWRITE=True to redo)")
            stats["skipped"] += 1
            continue

        # ── 1. Translate → col E ───────────────────────────────────────
        draft = translate(client, system, few_shot_msgs, nah, dictionary, glossary, sullivan)
        stats["translated"] += 1
        print(f"    NAH : {nah[:80]}")
        if gold:
            print(f"    GOLD: {gold[:80]}")
        print(f"    CLAU: {draft[:80]}")

        # ── 2. BLEU → col F (only when gold exists) ────────────────────
        bleu_score = ""
        if gold:
            bleu_score = str(bleu(gold, draft))
            stats["scored"] += 1
            print(f"    BLEU: {bleu_score}")

        # ── 3. Delta + Rule → cols G + H (only when gold exists) ───────
        delta, rule = "", ""
        if gold:
            time.sleep(0.3)
            delta, rule = analyse(client, nah, gold, draft)
            stats["analysed"] += 1
            print(f"    ΔΔΔΔ: {delta[:80]}")
            print(f"    RULE: {rule[:80]}")

        # ── 4. Write E, F, G, H in one batch update ────────────────────
        with_retry(lambda: ws.update(
            values=[[draft, bleu_score, delta, rule]],
            range_name=f"E{row_num}:H{row_num}"
        ))
        # Col I left empty for human input

        time.sleep(0.5)

    section("Summary")
    print(f"  Translated : {stats['translated']}")
    print(f"  BLEU scored: {stats['scored']}")
    print(f"  Analysed   : {stats['analysed']}")
    print(f"  Skipped    : {stats['skipped']}")
    print(f"\n  Col I (Tlahtol Human) is empty — add corrected rules directly in the sheet.")
    print(f"  Next run will pick up col I rules automatically.")


if __name__ == "__main__":
    main()
