"""
morphology.py — Heuristic morphological analyzer for Modern Huasteca Nahuatl (IDIEZ dialect).

Strips known affixes from inflected words to expose roots for dictionary lookup.
Not a full parser — partial decomposition is the goal.
"""

import os
import unicodedata

_HERE = os.path.dirname(os.path.abspath(__file__))

# ── Affix inventories ─────────────────────────────────────────────────────────

# Optional completive aspect prefix (precedes subject prefix)
_COMPLETIVE = ("o",)

# Subject prefixes — ordered longest-first to avoid short-prefix shadowing
_SUBJECT = ("an", "ni", "ti")

# Object / reflexive prefixes — longest-first is critical here
_OBJECT = (
    "amech", "nech", "mitz", "tech", "quin", "kin",
    "qui", "tla", "mo", "te", "c",
)

# Directional prefixes (after object)
_DIRECTIONAL = ("cal", "on")

# Verb suffixes — longest-first so greedy match takes the most-specific form
_VERB_SUFFIXES = (
    "tzinohua", "tzinoa", "ltilia", "huilia",
    "tihcaz", "tihuitz", "tihuia", "yahya", "htoc",
    "toca", "huia", "ltia", "ltih", "lizki",
    "cahki", "tinen", "tiuh", "tiaz", "tiyaz",
    "queh", "yohua", "tzino",
    "znequi", "nequi",      # desiderative — very common, not in original spec
    "yaya", "ya",
    # 3pl present/past forms
    "ah",
    "qui",                  # directional; guard (>4 chars) applied below
    "tia", "tih", "tiz",
    "yah", "keh", "hki", "ki",
    "iz",                   # future allomorph before consonant-final stems
    "h",                    # 3pl marker (short, keep last among short ones)
    "z", "s",
)

# Noun suffixes — longest-first
_NOUN_SUFFIXES = (
    "liztli", "tzitzin", "tzintin", "tzinmeh",
    "tzihmeh", "tzihtin",
    "tzin", "tsin", "ton",
    "tin", "meh",
    "wan", "yoh", "ih",
    "ztli",     # handles -lli+ztli merger: pohuall+iztli -> strip ztli -> pohualli
    "tli", "tl",
    "in",
)

# Possessive prefixes on nouns (can appear instead of subject prefix context)
_POSSESSIVE = ("amo", "no", "mo", "to", "in", "i", "y")

# Embedded object-prefix anchors: when scanning inside a stem for these,
# the suffix portion becomes a candidate root.
_EMBEDDED_OBJ = ("tla", "te", "mo", "nech", "mitz", "tech", "qui")

# Minimum stem length kept after any single strip operation
_MIN_STEM = 3


# ── Normalization ─────────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    """Lowercase + strip vowel length marks (ā→a, ē→e, ī→i, ō→o)."""
    s = s.lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


# ── Core stripping helpers ────────────────────────────────────────────────────

def _strip_prefix(word: str, prefixes: tuple) -> list[str]:
    """Return all results of stripping exactly one prefix from word."""
    results = []
    for pfx in prefixes:
        if word.startswith(pfx) and len(word) - len(pfx) >= _MIN_STEM:
            results.append(word[len(pfx):])
    return results


def _strip_suffix(word: str, suffixes: tuple) -> list[str]:
    """Return all results of stripping exactly one suffix from word."""
    results = []
    for suf in suffixes:
        if suf == "qui" and len(word) - len(suf) <= 4:
            # guard: directional -qui only stripped when stem remains long enough
            continue
        if word.endswith(suf) and len(word) - len(suf) >= _MIN_STEM:
            results.append(word[:-len(suf)])
    return results


def _embedded_obj_candidates(word: str) -> list[str]:
    """
    Scan word for an embedded object-prefix anchor and return the portion
    from that anchor onwards (and without it). Handles noun incorporation
    like xochi+tla+pohua+liztli -> tlapohua, pohua.
    """
    results = []
    for obj in _EMBEDDED_OBJ:
        idx = word.find(obj)
        # only useful if the prefix is not at position 0 (already handled) and
        # something meaningful remains after it
        if idx > 0 and len(word) - idx >= _MIN_STEM:
            from_obj = word[idx:]            # e.g. tlapohua
            after_obj = word[idx + len(obj):]  # e.g. pohua
            if len(from_obj) >= _MIN_STEM:
                results.append(from_obj)
            if len(after_obj) >= _MIN_STEM:
                results.append(after_obj)
    return results


# ── Public API ────────────────────────────────────────────────────────────────

def decompose(word: str) -> list[str]:
    """
    Returns candidate roots from word by stripping known Huasteca Nahuatl affixes.
    Always includes the original word as final fallback.
    Shortest candidates (most-stripped) appear first.
    """
    w = _norm(word)
    candidates: list[str] = []

    def _add(cand: str):
        if cand and cand not in candidates:
            candidates.append(cand)

    # ── Pass A: work through prefix layers then suffix-strip each result ──────

    layer0 = [w]

    # Optional completive 'o' (generates parallel branch)
    layer_o = []
    for stem in layer0:
        for s in _strip_prefix(stem, _COMPLETIVE):
            layer_o.append(s)
    layer0 = layer0 + layer_o  # keep both with and without 'o'

    # Subject prefix strip
    layer1 = []
    for stem in layer0:
        for s in _strip_prefix(stem, _SUBJECT):
            layer1.append(s)

    # Possessive prefix strip (for noun analysis path — no subject prefix found)
    layer1_poss = []
    for stem in layer0:
        for s in _strip_prefix(stem, _POSSESSIVE):
            layer1_poss.append(s)

    # Object / reflexive prefix strip (three sources):
    #   1. post-subject stems (normal verbal path)
    #   2. possessive-stripped stems (nominal path)
    #   3. original layer0 stems — handles zero/null 3sg subject (tla-verb, te-verb, etc.)
    layer2 = []
    for stem in layer1:
        _add(stem)
        for s in _strip_prefix(stem, _OBJECT):
            layer2.append(s)
    for stem in layer1_poss:
        _add(stem)
        for s in _strip_prefix(stem, _OBJECT):
            layer2.append(s)
    # Null-subject path: try object prefixes directly on original (and post-o) forms
    for stem in layer0:
        for s in _strip_prefix(stem, _OBJECT):
            layer2.append(s)

    # Directional prefix strip
    layer3 = []
    for stem in layer2:
        _add(stem)
        for s in _strip_prefix(stem, _DIRECTIONAL):
            layer3.append(s)

    # After directional, the remaining stem is the verbal/nominal base
    for stem in layer3:
        _add(stem)

    # ── Pass B: suffix stripping on every stem accumulated so far ─────────────

    # Collect all unique stems produced so far to feed suffix stripping
    all_stems = list(candidates)  # snapshot before suffix-based additions

    for stem in all_stems:
        # Verb suffixes
        for stripped in _strip_suffix(stem, _VERB_SUFFIXES):
            _add(stripped)
            # One more layer of verb-suffix stripping for multi-suffix words
            for stripped2 in _strip_suffix(stripped, _VERB_SUFFIXES):
                _add(stripped2)
        # Noun suffixes
        for stripped in _strip_suffix(stem, _NOUN_SUFFIXES):
            _add(stripped)

    # Also apply verb/noun suffixes directly to the original bare-stripped stems
    # (layer2/layer3 objects that weren't yet added when we took the snapshot)
    for stem in layer2 + layer3:
        for stripped in _strip_suffix(stem, _VERB_SUFFIXES):
            _add(stripped)
            for stripped2 in _strip_suffix(stripped, _VERB_SUFFIXES):
                _add(stripped2)
        for stripped in _strip_suffix(stem, _NOUN_SUFFIXES):
            _add(stripped)

    # ── Pass C: embedded object-prefix scan ───────────────────────────────────

    # Apply to all stems so far (including original w after suffix strip)
    snap2 = list(candidates) + [w]
    for stem in snap2:
        for ec in _embedded_obj_candidates(stem):
            _add(ec)
            # Suffix-strip the embedded candidates too
            for stripped in _strip_suffix(ec, _VERB_SUFFIXES):
                _add(stripped)
            for stripped in _strip_suffix(ec, _NOUN_SUFFIXES):
                _add(stripped)

    # ── Sort by length (shortest = most-stripped first) and append original ───

    candidates = [c for c in candidates if c != w]
    candidates.sort(key=len)
    candidates.append(w)

    return candidates


def get_hints(word: str, dictionary: dict) -> list[str]:
    """
    Returns up to 3 definition strings for word, found via morphological decomposition.
    Tries each candidate from decompose() against a macron-normalised index.
    """
    # Build a normalised lookup index once per call is wasteful; callers running
    # in a loop should build it once externally if performance matters.
    # Here we build it on demand — acceptable for the heuristic pre-processing role.
    norm_index: dict[str, str] = {_norm(k): k for k in dictionary}

    hits: list[str] = []
    seen: set[str] = set()

    for candidate in decompose(word):
        key = _norm(candidate)
        if key in norm_index:
            orig_key = norm_index[key]
            if orig_key in seen:
                continue
            seen.add(orig_key)
            entries = dictionary[orig_key]
            if not isinstance(entries, list) or not entries:
                continue
            defs = entries[0].get("definitions", [])
            if not defs:
                continue
            es_def = defs[0].get("es", "").strip()
            if es_def:
                hits.append(f"{orig_key} [{candidate}]: {es_def}")
        if len(hits) >= 3:
            break

    return hits


# ── __main__ self-test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    DICT_PATH = os.path.join(_HERE, "dictionaries", "enriched_idiez.json")
    with open(DICT_PATH) as _f:
        _dictionary = json.load(_f)

    _test_words = [
        "nitlatequitiz",        # ni+tla+tequiti+z  -> tequiti (to work, future)
        "xochitlapohualiztli",  # xochi+tla+pohua+liztli -> pohua (reading/counting noun)
        "timocochi",            # ti+mo+cochi -> cochi (you sleep, reflexive)
        "niccua",               # ni+c+cua -> cua/cuā (I eat it)
        "antlapohuah",          # an+tla+pohua+h -> pohua (you-all read, 3pl marker)
        "otinechilliaya",       # o+ti+nech+illia+ya -> illia (you were saying it to me)
        "nimotequitiznequi",    # ni+mo+tequiti+z+nequi -> tequiti (I want to work)
        "timochihuaz",          # ti+mo+chihua+z -> chihua (you will be done/made)
        "tlapohualliztli",      # tla+pohua+liztli -> pohua (act of counting)
        "nimitzitta",           # ni+mitz+itta -> itta (I see you)
    ]

    for _word in _test_words:
        _candidates = decompose(_word)
        _hints = get_hints(_word, _dictionary)
        print(f"\nWord: {_word}")
        print(f"  Candidates: {_candidates}")
        if _hints:
            print("  Dict hits:")
            for _h in _hints:
                print(f"    {_h}")
        else:
            print("  Dict hits: (none)")
