#!/usr/bin/env python3
"""
grammar_rules.py — Nahuatl grammar rules for English→Nahuatl translation.

Provides:
  - Function word mappings (pronouns, prepositions, articles, conjunctions, etc.)
  - Irregular verb forms and plurals
  - Number translation (0-1000+)
  - Common phrase patterns
  - Suffix/prefix rules for better word lookup

Based on: IDIEZ Huasteca Nahuatl course materials, Karttunen, Andrews grammar.

Data files (loaded from data/*.json):
  - function_words.json, irregular_verbs.json, common_phrases.json
  - direct_en_nah.json, en_to_es.json
"""

import re
import json
from pathlib import Path

# --- Data directory ---
_DATA_DIR = Path(__file__).parent / "data"

def _load_json(filename):
    """Load a JSON data file from the data/ directory."""
    filepath = _DATA_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# --- Large dictionaries externalized to JSON ---
FUNCTION_WORDS   = _load_json("function_words.json")
IRREGULAR_VERBS  = _load_json("irregular_verbs.json")
COMMON_PHRASES   = _load_json("common_phrases.json")
DIRECT_EN_NAH    = _load_json("direct_en_nah.json")
EN_TO_ES         = _load_json("en_to_es.json")

# Import synonym map
from synonyms import SYNONYMS

# Import verb conjugator
from verb_conjugator import find_verb_info, translate_and_conjugate


def clean_nahuatl_text(text):
    """Clean up Nahuatl text for output.
    
    - Remove hyphens from words (TIANQUIZ-TLI → tianquiztli)
    - Remove parentheses from words (ATLAHU(I)-TL → atlahuitl)
    - Strip diacritics/macrons (ā → a, ē → e, ī → i, ō → o, ū → u)
    - Convert ALL CAPS or mostly-uppercase words to lowercase
    - Capitalize first letter of each sentence
    - Clean up extra spaces
    """
    if not text:
        return text

    # Step 0: Strip diacritics/macrons to avoid font rendering issues
    diacritic_map = {
        'ā': 'a', 'ē': 'e', 'ī': 'i', 'ō': 'o', 'ū': 'u',
        'Ā': 'A', 'Ē': 'E', 'Ī': 'I', 'Ō': 'O', 'Ū': 'U',
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ü': 'u', 'Ü': 'U',
        'ñ': 'n', 'Ñ': 'N',
        'š': 's', 'Š': 'S',
        'ś': 's', 'Ś': 'S',
    }
    for src, dst in diacritic_map.items():
        text = text.replace(src, dst)

    # Step 1: Remove parentheses from words (ATLAHU(I)-TL → ATLAHUI-TL)
    text = re.sub(r'\(([A-Za-z])\)', r'\1', text)

    # Step 2: Remove hyphens from words
    text = re.sub(r'([A-Za-z])-([A-Za-z])', r'\1\2', text)

    # Step 3: Convert ALL CAPS or mostly-uppercase words to lowercase
    def clean_word(match):
        word = match.group(0)
        upper_count = sum(1 for c in word if c.isupper())
        total_letters = sum(1 for c in word if c.isalpha())
        if total_letters > 2 and upper_count / total_letters > 0.5:
            return word.lower()
        return word

    text = re.sub(r'\b[A-Za-z][A-Za-z]*\b', clean_word, text)

    # Step 4: Capitalize first letter of each sentence
    sentences = re.split(r'([.!?]+\s*)', text)
    cleaned = []
    for i, part in enumerate(sentences):
        if i % 2 == 0:
            part = part.strip()
            if part:
                part = part[0].upper() + part[1:] if len(part) > 1 else part.upper()
            cleaned.append(part)
        else:
            cleaned.append(part)

    text = ''.join(cleaned)

    # Step 5: Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# ============================================================
# 15. ENGLISH → SPANISH MAPPING
#     Final fallback: translate unknown English word to Spanish,
#     then look up Spanish word in the dictionary.
#     Loaded from data/en_to_es.json
# ============================================================

# ============================================================
# 16. DIRECT ENGLISH → NAHUATL FALLBACK
#     For common words not in the dictionary and not in Spanish.
#     Loaded from data/direct_en_nah.json
# ============================================================

# ============================================================
# 1. FUNCTION WORDS
#    These are intentionally excluded from dictionary STOP_WORDS
#    because a translator needs them.
#    Loaded from data/function_words.json
# ============================================================

# ============================================================
# ============================================================
# 2. IRREGULAR VERB FORMS
#    Map English irregular conjugations to their root form
#    so the dictionary lookup can find them.
#    Loaded from data/irregular_verbs.json
# ============================================================

# ============================================================
# 3. IRREGULAR PLURALS
# ============================================================

IRREGULAR_PLURALS = {
    "men": "man",
    "women": "woman",
    "children": "child",
    "people": "person",
    "feet": "foot",
    "teeth": "tooth",
    "geese": "goose",
    "mice": "mouse",
    "lice": "louse",
    "oxen": "ox",
    "dice": "die",
    "elves": "elf",
    "halves": "half",
    "knives": "knife",
    "lives": "life",
    "loaves": "loaf",
    "selves": "self",
    "shelves": "shelf",
    "thieves": "thief",
    "wives": "wife",
    "wolves": "wolf",
    "leaves": "leaf",
    "sheaves": "sheaf",
    "calves": "calf",
}

# ============================================================
# 4. IRREGULAR COMPARATIVES / SUPERLATIVES
# ============================================================

COMPARATIVES = {
    "better": "good",
    "best": "good",
    "worse": "bad",
    "worst": "bad",
    "more": "much",
    "most": "much",
    "less": "little",
    "least": "little",
    "fewer": "few",
    "fewest": "few",
    "further": "far",
    "furthest": "far",
    "farther": "far",
    "farthest": "far",
    "elder": "old",
    "eldest": "old",
    "older": "old",
    "oldest": "old",
    "younger": "young",
    "youngest": "young",
    "later": "late",
    "latest": "late",
    "latter": "late",
    "last": "late",
    "first": "one",
    "second": "two",
    "third": "three",
}

# ============================================================
# 5. NUMBERS (0-1000+)
#    Based on IDIEZ Huasteca Nahuatl numbering system.
# ============================================================

NUMBERS = {
    # 0-10
    "zero": "cero",
    "one": "ce",
    "two": "ome",
    "three": "eyi",
    "four": "nahui",
    "five": "macuilli",
    "six": "chicuace",
    "seven": "chicome",
    "eight": "chicueyi",
    "nine": "chiucnahui",
    "ten": "mahtlactli",
    # 11-19
    "eleven": "mahtlactli huan ce",
    "twelve": "mahtlactli huan ome",
    "thirteen": "mahtlactli huan eyi",
    "fourteen": "mahtlactli huan nahui",
    "fifteen": "mahtlactli huan macuilli",
    "sixteen": "mahtlactli huan chicuace",
    "seventeen": "mahtlactli huan chicome",
    "eighteen": "mahtlactli huan chicueyi",
    "nineteen": "mahtlactli huan chiucnahui",
    # Tens
    "twenty": "cempohualli",
    "thirty": "cempohualli huan mahtlactli",
    "forty": "ompohualli",
    "fifty": "ompohualli huan mahtlactli",
    "sixty": "epohualli",
    "seventy": "epohualli huan mahtlactli",
    "eighty": "nauhpohualli",
    "ninety": "nauhpohualli huan mahtlactli",
    # Hundreds+
    "hundred": "cempohualli",
    "thousand": "cempohualli",
    "million": "cempohualli",
}

# ============================================================
# ============================================================
# 6. COMMON PHRASES
#    Multi-word expressions that should be translated as a unit.
#    Loaded from data/common_phrases.json
# ============================================================

# ============================================================
# 7. SUFFIX RULES
#    Additional suffixes beyond the basic ones in translator.py
# ============================================================

SUFFIX_RULES = [
    # (suffix, min_root_length, strip_from_end)
    ("s", 3, 1),       # plurals: cats -> cat
    ("es", 3, 2),      # boxes -> box
    ("ies", 4, 3),     # berries -> berry (need to restore y)
    ("ed", 4, 2),      # walked -> walk
    ("ied", 5, 3),     # tried -> try (need to restore y)
    ("ing", 5, 3),     # walking -> walk
    ("ly", 4, 2),      # quickly -> quick
    ("tion", 5, 4),    # action -> act
    ("sion", 5, 4),    # decision -> decide
    ("ment", 5, 4),    # movement -> move
    ("ness", 5, 4),    # kindness -> kind
    ("ship", 5, 4),    # friendship -> friend
    ("hood", 5, 4),    # childhood -> child
    ("dom", 4, 3),     # freedom -> free
    ("ful", 4, 3),     # beautiful -> beauty
    ("less", 5, 4),    # hopeless -> hope
    ("ous", 4, 3),     # dangerous -> danger
    ("ive", 4, 3),     # active -> act
    ("able", 5, 4),    # readable -> read
    ("ible", 5, 4),    # visible -> see
    ("al", 4, 2),      # arrival -> arrive
    ("ance", 5, 4),    # importance -> important
    ("ence", 5, 4),    # difference -> different
    ("ity", 4, 3),     # ability -> able
    ("ty", 4, 2),      # safety -> safe
    ("ure", 4, 3),     # pressure -> press
    ("er", 4, 2),      # worker -> work
    ("or", 4, 2),      # actor -> act
    ("ist", 4, 3),     # artist -> art
    ("ism", 4, 3),     # realism -> real
    ("est", 4, 3),     # biggest -> big
]

# ============================================================
# 8. GREETINGS / VALEDICTIONS
# ============================================================

GREETINGS = {
    "hello": "nimitztlahpaloz",
    "hi": "nimitztlahpaloz",
    "good morning": "nimitztlahpaloz tlayi",
    "good afternoon": "nimitztlahpaloz tocompah",
    "good evening": "nimitztlahpaloz tateh",
    "goodbye": "timoittazceh",
    "bye": "timoittazceh",
    "see you later": "timoittazceh",
    "see you tomorrow": "moztlayoc",
    "see you afterwards": "teipayoc",
    "thank you": "tlazcamati",
    "thanks": "tlazcamati",
    "thank": "tlazcamati",
    "you're welcome": "axtlen",
    "please": "xinechtlahpaltili",
    "sorry": "xinechtlahpaltili",
    "excuse me": "xinechtlahpaltili",
    "yes": "quena",
    "no": "amo",
    "not": "amo",
    "how are you": "queniuhqui tica",
    "i am fine": "cualli nica",
    "what is your name": "tlein motoca",
    "my name is": "notoca ca",
    "i don't understand": "amo niquimati",
    "i don't know": "amo nimati",
    "i know": "nimati",
    "i understand": "niquimati",
    "help": "palehui",
    "stop": "mocehui",
    "come": "xihuala",
    "go": "xihui",
    "wait": "xicalhui",
    "listen": "xicaqui",
    "look": "xitta",
    "eat": "xitlacua",
    "drink": "xiatli",
    "sleep": "xicochi",
    "work": "xitequiti",
    "speak": "xitlahtoa",
    "talk": "xitlahtoa",
    "tell me": "xinechilhui",
    "show me": "xinechnextili",
    "give me": "xinechmaca",
    "take me": "xinechhuica",
    "bring me": "xinechhuica",
    "let me": "xinechcahuali",
    "help me": "xinechpalehui",
    "teach me": "xinechtemachti",
}

# ============================================================
# 9. BODY PARTS (always possessed in Nahuatl)
# ============================================================

BODY_PARTS = {
    "head": "tzontecon",
    "face": "ixco",
    "eye": "ixtiyol",
    "eyes": "ixtiyol",
    "ear": "nacaz",
    "ears": "nacaz",
    "nose": "yacatzol",
    "mouth": "camac",
    "tongue": "nenepil",
    "tooth": "tlancuah",
    "teeth": "tlancuah",
    "neck": "quechcuayo",
    "shoulder": "acol",
    "arm": "mahcol",
    "hand": "mah",
    "hands": "mah",
    "finger": "mahpil",
    "fingers": "mahpil",
    "chest": "ahuac",
    "heart": "yolixco",
    "stomach": "cuitlapan",
    "leg": "icxi",
    "legs": "icxi",
    "foot": "icxi",
    "feet": "icxi",
    "body": "nacayo",
    "skin": "nacayo",
    "bone": "omitl",
    "bones": "omeh",
    "blood": "eztli",
    "hair": "tzontli",
    "back": "cuitlapan",
    "knee": "nextli",
    "elbow": "mamolic",
}

# ============================================================
# 11. IRREGULAR VERB CONJUGATIONS (from IDIEZ N1 unidades 5-6, p.67)
#     The 4 core irregular verbs with full conjugation tables.
#     Maps English tense+pronoun -> Nahuatl form.
# ============================================================

# Pronoun -> subject prefix mapping
PRONOUN_PREFIX = {
    "i": "ni",
    "you": "ti",
    "he": "",
    "she": "",
    "it": "",
    "we": "ti",
    "they": "",
}

# --- ITZTOC = "to be" (people & animals only) ---
ITZTOC_CONJUGATIONS = {
    # Present
    ("i", "present"): "niitztoc",
    ("you", "present"): "tiitztoc",
    ("he", "present"): "itztoc",
    ("she", "present"): "itztoc",
    ("we", "present"): "tiitztoqueh",
    ("they", "present"): "itztoqueh",
    # Imperfect / Past
    ("i", "past"): "niitztoya",
    ("you", "past"): "tiitztoya",
    ("he", "past"): "itztoya",
    ("she", "past"): "itztoya",
    ("we", "past"): "tiitztoyah",
    ("they", "past"): "itztoyah",
    # Future
    ("i", "future"): "niitztoz",
    ("you", "future"): "tiitztoz",
    ("he", "future"): "itztoz",
    ("she", "future"): "itztoz",
    ("we", "future"): "tiitztozceh",
    ("they", "future"): "itztozceh",
}

# --- ELTOC = "to be" (inanimate things & plants only) ---
ELTOC_CONJUGATIONS = {
    # Present
    ("singular", "present"): "eltoc",
    ("plural", "present"): "eltoc",
    # Imperfect / Past
    ("singular", "past"): "eltoya",
    ("plural", "past"): "eltoyah",
    # Future
    ("singular", "future"): "eltoz",
    ("plural", "future"): "eltozceh",
}

# --- ONCAH = "there is/are" (hay) ---
ONCAH_CONJUGATIONS = {
    "present": "oncah",
    "past": "oncac",
    "future": "oncaz",
}

# --- YAUH = "to go" (ir) ---
YAUH_CONJUGATIONS = {
    # Present
    ("i", "present"): "niyauh",
    ("you", "present"): "tiyauh",
    ("he", "present"): "yohui",
    ("she", "present"): "yohui",
    ("we", "present"): "tiyohuih",
    ("they", "present"): "yohuih",
    # Past
    ("i", "past"): "niyahqui",
    ("you", "past"): "tiyahqui",
    ("he", "past"): "yahqui",
    ("she", "past"): "yahqui",
    ("we", "past"): "tiyahqueh",
    ("they", "past"): "inyahqueh",
    # Future
    ("i", "future"): "niyaz",
    ("you", "future"): "tiyaz",
    ("he", "future"): "yaz",
    ("she", "future"): "yaz",
    ("we", "future"): "tiyazceh",
    ("they", "future"): "inyazceh",
    # Conditional
    ("i", "conditional"): "niyazquia",
    ("you", "conditional"): "tiyazquia",
    ("he", "conditional"): "yazquia",
    ("she", "conditional"): "yazquia",
    ("we", "conditional"): "tiyazquiah",
    ("they", "conditional"): "inyazquiah",
    # Imperfect (continuous past)
    ("i", "imperfect"): "niyohuiyaya",
    ("you", "imperfect"): "tiyohuiyaya",
    ("he", "imperfect"): "yohuiyaya",
    ("she", "imperfect"): "yohuiyaya",
    ("we", "imperfect"): "tiyohuiyayah",
    ("they", "imperfect"): "yohuiyayah",
}

# ============================================================
# 12. TENSE DETECTION PATTERNS
#     Detect English tense from auxiliary verbs
# ============================================================

TENSE_PATTERNS = [
    # (pattern_regex, tense, notes)
    (r'\b(am|is|are)\s+\w+ing\b', 'present_continuous', "I am going"),
    (r'\b(was|were)\s+\w+ing\b', 'past_continuous', "I was going"),
    (r'\b(will|shall)\s+\w+\b', 'future', "I will go"),
    (r'\b(would|should|could|might)\s+\w+\b', 'conditional', "I would go"),
    (r'\b(has|have)\s+\w+ed\b', 'present_perfect', "I have gone"),
    (r'\b(had)\s+\w+ed\b', 'past_perfect', "I had gone"),
    (r'\b(was|were)\s+\w+ed\b', 'past_passive', "I was taken"),
    (r'\b(is|are)\s+\w+ed\b', 'present_passive', "I am taken"),
    (r'\b(went|came|saw|knew|said|gave|took|made|found|brought|heard|ran|felt|thought|told|spoke|wrote|read|learned|taught|understood|began|grew|stood|fell|lost|paid|met|sat|led|meant|built|bought|sold|sent|spent|left|slept|lay|caught|fought|sought|struck|won|bound|dug|hung|stuck|stung|swung|spun|slid|spat|split|spread|shed|bet|cut|hit|hurt|cost|cast|thrust|quit|shut|rid|bled|bred|fed|sped|lit|clung|flung|slung|wrung|ground|wound)\b', 'simple_past', "I went"),
    (r'\b(going|coming|seeing|knowing|saying|giving|taking|making|finding|bringing|hearing|running|feeling|thinking|telling|speaking|writing|reading|learning|teaching|understanding|beginning|growing|standing|falling|losing|paying|meeting|sitting|leading|meaning|building|buying|selling|sending|spending|leaving|sleeping|lying|catching|fighting|seeking|striking|winning|binding|digging|hanging|sticking|stinging|swinging|spinning|sliding|spitting|splitting|spreading|shedding|betting|cutting|hitting|hurting|costing|casting|thrusting|quitting|shutting|ridding|bleeding|breeding|feeding|speeding|lighting|clinging|flinging|slinging|wringing|grinding|winding)\b', 'present_participle', "going"),
    (r'\b(gone|come|seen|known|said|given|taken|made|found|brought|heard|run|felt|thought|told|spoken|written|read|learned|taught|understood|begun|grown|stood|fallen|lost|paid|met|sat|led|meant|built|bought|sold|sent|spent|left|slept|lain|caught|fought|sought|struck|won|bound|dug|hung|stuck|stung|swung|spun|slid|spat|split|spread|shed|bet|cut|hit|hurt|cost|cast|thrust|quit|shut|rid|bled|bred|fed|sped|lit|clung|flung|slung|wrung|ground|wound)\b', 'past_participle', "gone"),
]

# ============================================================
# 13. HELPER FUNCTIONS FOR IRREGULAR VERBS
# ============================================================

def conjugate_itztoc(pronoun, tense="present"):
    """Conjugate itztoc (to be - people/animals)."""
    return ITZTOC_CONJUGATIONS.get((pronoun.lower(), tense.lower()))


def conjugate_eltoc(number, tense="present"):
    """Conjugate eltoc (to be - inanimate/plants)."""
    return ELTOC_CONJUGATIONS.get((number.lower(), tense.lower()))


def conjugate_oncah(tense="present"):
    """Conjugate oncah (there is/are)."""
    return ONCAH_CONJUGATIONS.get(tense.lower())


def conjugate_yauh(pronoun, tense="present"):
    """Conjugate yauh (to go)."""
    return YAUH_CONJUGATIONS.get((pronoun.lower(), tense.lower()))


def detect_tense(text):
    """Detect the tense of an English sentence.
    Returns (tense, subject_pronoun) or (None, None)."""
    text_lower = text.lower()

    # Check for subject pronoun
    pronouns = ["i", "you", "he", "she", "it", "we", "they"]
    subject = None
    for p in pronouns:
        if re.search(r'\b' + p + r'\b', text_lower):
            subject = p
            break

    # Check tense patterns
    for pattern, tense, _ in TENSE_PATTERNS:
        if re.search(pattern, text_lower):
            return tense, subject

    return None, subject

def lookup_function_word(word):
    """Look up a function word. Returns Nahuatl or None."""
    return FUNCTION_WORDS.get(word.lower())


def lookup_irregular_verb(word):
    """Map irregular verb form to root. Returns root or None."""
    return IRREGULAR_VERBS.get(word.lower())


def lookup_irregular_plural(word):
    """Map irregular plural to singular. Returns singular or None."""
    return IRREGULAR_PLURALS.get(word.lower())


def lookup_comparative(word):
    """Map comparative/superlative to base. Returns base or None."""
    return COMPARATIVES.get(word.lower())


def lookup_number(word):
    """Look up a number word. Returns Nahuatl or None."""
    return NUMBERS.get(word.lower())


def lookup_phrase(text):
    """Look up a multi-word phrase. Returns Nahuatl or None."""
    text_lower = text.lower().strip()
    return COMMON_PHRASES.get(text_lower)


def lookup_greeting(word):
    """Look up a greeting or common expression. Returns Nahuatl or None."""
    return GREETINGS.get(word.lower())


def lookup_body_part(word):
    """Look up a body part. Returns Nahuatl root or None."""
    return BODY_PARTS.get(word.lower())


def try_suffix_stripping(word):
    """Try stripping common English suffixes to find root word.
    Returns (root, suffix) or (None, None)."""
    word_lower = word.lower()
    for suffix, min_len, strip_len in SUFFIX_RULES:
        if len(word_lower) >= min_len and word_lower.endswith(suffix):
            root = word_lower[:-strip_len]
            if len(root) >= 2:
                # Handle special cases
                if suffix == "ies" and len(root) >= 2:
                    root = root + "y"  # berries -> berry
                elif suffix == "ied" and len(root) >= 2:
                    root = root + "y"  # tried -> try
                return root, suffix
    return None, None


def is_function_word(word):
    """Check if a word is a function word (article, pronoun, preposition, etc.)."""
    return word.lower() in FUNCTION_WORDS


def is_number_word(word):
    """Check if a word is a number."""
    return word.lower() in NUMBERS


def is_greeting(word):
    """Check if a word/phrase is a greeting or common expression."""
    return word.lower() in GREETINGS


def is_body_part(word):
    """Check if a word is a body part."""
    return word.lower() in BODY_PARTS


# ============================================================
# 14. MAIN TRANSLATION FUNCTION
#     Call this from translator.py — all grammar logic lives here.
# ============================================================

def translate_with_grammar(text, dictionary):
    """
    Translate English text to Nahuatl using grammar rules + dictionary.

    Lookup order per token:
      0. Irregular verb conjugations (itztoc, eltoc, oncah, yauh)
      1. Multi-word phrases
      2. Greetings
      3. Function words
      4. Numbers
      5. Body parts
      6. Direct dictionary lookup
      7. Irregular verb -> root -> dictionary
      8. Irregular plural -> singular -> dictionary
      9. Comparative -> base -> dictionary
     10. Suffix stripping -> dictionary
     11. Mark as unknown

    Returns: (translated_text, set_of_unknown_words)
    """
    unknown_words = set()
    paragraphs = text.split('\n')
    translated_paragraphs = []

    for paragraph in paragraphs:
        if not paragraph.strip():
            translated_paragraphs.append("")
            continue
        translated_paragraphs.append(
            _translate_paragraph(paragraph, dictionary, unknown_words)
        )

    return '\n'.join(translated_paragraphs), unknown_words


def _translate_paragraph(paragraph, dictionary, unknown_words):
    """Internal: translate one paragraph with grammar-aware lookup."""

    def _get_nah(entry):
        """Extract Nahuatl word from dictionary entry (string or dict)."""
        if isinstance(entry, dict):
            return entry.get("nah", "")
        return entry

    tokens = re.findall(
        r"([A-Za-z\u00C0-\u024F]+(?:'[A-Za-z]+)?|[^A-Za-z\u00C0-\u024F\s]+|\s+)",
        paragraph
    )

    translated_tokens = []
    i = 0
    while i < len(tokens):
        token = tokens[i]

        if not token.strip():
            translated_tokens.append(token)
            i += 1
            continue
        if not re.match(r'^[A-Za-z\u00C0-\u024F]', token):
            translated_tokens.append(token)
            i += 1
            continue

        token_lower = token.lower()
        translated = None

        # --- STEP 0: Irregular verb conjugations ---

        # 0a. "there is/are/was/were/will be" -> oncah
        if token_lower == "there":
            next_word, next_idx = _next_word_token(i, tokens)
            if next_word in ("is", "are"):
                translated = conjugate_oncah("present")
                i = next_idx + 1
                translated_tokens.append(translated)
                continue
            elif next_word in ("was", "were"):
                translated = conjugate_oncah("past")
                i = next_idx + 1
                translated_tokens.append(translated)
                continue
            elif next_word == "will":
                translated = conjugate_oncah("future")
                # skip "will" and "be"
                _, after_will = _next_word_token(i, tokens)
                if after_will:
                    _, after_be = _next_word_token(after_will, tokens)
                    if after_be:
                        nw2, _ = _next_word_token(after_be, tokens)
                        if nw2 == "be":
                            i = after_be + 1
                        else:
                            i = after_will + 1
                    else:
                        i = after_will + 1
                else:
                    i = next_idx + 1
                translated_tokens.append(translated)
                continue

        # 0b. "I am going / she was going" -> yauh
        if token_lower in ("am", "is", "are", "was", "were"):
            next_word, next_idx = _next_word_token(i, tokens)
            if next_word == "going":
                subject = _find_subject_before(i, tokens)
                if subject:
                    tense = "present" if token_lower in ("am", "is", "are") else "imperfect"
                    translated = conjugate_yauh(subject, tense)
                    if translated:
                        i = next_idx + 1
                        translated_tokens.append(translated)
                        continue

        # 0c. "I am / he is / they were" -> itztoc or eltoc
        if token_lower in ("am", "is", "are", "was", "were"):
            next_word, _ = _next_word_token(i, tokens)
            if next_word == "going":
                pass  # fall through
            else:
                subject = _find_subject_before(i, tokens)
                if subject:
                    tense = "present" if token_lower in ("am", "is", "are") else "past"
                    animate = {"man", "woman", "child", "boy", "girl", "person", "people",
                               "he", "she", "they", "we", "i", "you", "who", "teacher",
                               "student", "friend", "mother", "father", "brother", "sister",
                               "dog", "cat", "bird", "fish", "animal"}
                    if next_word in animate or subject in ("i", "you", "he", "she", "we", "they"):
                        translated = conjugate_itztoc(subject, tense)
                    else:
                        number = "plural" if token_lower in ("are", "were") else "singular"
                        translated = conjugate_eltoc(number, tense)
                    if translated:
                        i += 1
                        translated_tokens.append(translated)
                        continue

        # 0d. "I go / he went / she goes" -> yauh
        if token_lower in ("go", "goes", "went", "gone", "going"):
            subject = _find_subject_before(i, tokens)
            if subject:
                tense_map = {"go": "present", "goes": "present", "went": "past",
                             "gone": "past", "going": "present"}
                translated = conjugate_yauh(subject, tense_map.get(token_lower, "present"))
                if translated:
                    i += 1
                    translated_tokens.append(translated)
                    continue

        # 0e. "will go / will be" -> future
        if token_lower == "will":
            next_word, next_idx = _next_word_token(i, tokens)
            subject = _find_subject_before(i, tokens)
            if next_word == "go" and subject:
                translated = conjugate_yauh(subject, "future")
                i = next_idx + 1
                translated_tokens.append(translated)
                continue
            elif next_word == "be" and subject:
                translated = conjugate_itztoc(subject, "future")
                i = next_idx + 1
                translated_tokens.append(translated)
                continue

        # --- STEP 1: Multi-word phrases ---
        if i + 1 < len(tokens):
            two_word = token_lower + " " + tokens[i + 1].lower()
            phrase_result = lookup_phrase(two_word)
            if phrase_result:
                translated = phrase_result
                i += 2
                if token[0].isupper():
                    translated = translated.capitalize()
                translated_tokens.append(translated)
                continue

        if i + 2 < len(tokens):
            three_word = token_lower + " " + tokens[i + 1].lower() + " " + tokens[i + 2].lower()
            phrase_result = lookup_phrase(three_word)
            if phrase_result:
                translated = phrase_result
                i += 3
                if token[0].isupper():
                    translated = translated.capitalize()
                translated_tokens.append(translated)
                continue

        # --- STEP 2: Greetings ---
        greeting_result = lookup_greeting(token_lower)
        if greeting_result:
            translated = greeting_result
            if token[0].isupper():
                translated = translated.capitalize()
            translated_tokens.append(translated)
            i += 1
            continue

        # --- STEP 3: Function words ---
        func_result = lookup_function_word(token_lower)
        if func_result is not None:
            if func_result:
                translated = func_result
                if token[0].isupper():
                    translated = translated.capitalize()
                translated_tokens.append(translated)
            i += 1
            continue

        # --- STEP 4: Numbers ---
        num_result = lookup_number(token_lower)
        if num_result:
            translated = num_result
            if token[0].isupper():
                translated = translated.capitalize()
            translated_tokens.append(translated)
            i += 1
            continue

        # --- STEP 5: Body parts ---
        body_result = lookup_body_part(token_lower)
        if body_result:
            translated = body_result
            if token[0].isupper():
                translated = translated.capitalize()
            translated_tokens.append(translated)
            i += 1
            continue

        # --- STEP 6: Direct dictionary lookup ---
        if token_lower in dictionary:
            translated = _get_nah(dictionary[token_lower])
            if translated and token[0].isupper():
                translated = translated.capitalize()
            if translated:
                translated_tokens.append(translated)
                i += 1
                continue

        # --- STEP 7: Irregular verb -> root -> dictionary ---
        verb_root = lookup_irregular_verb(token_lower)
        if verb_root and verb_root in dictionary:
            translated = _get_nah(dictionary[verb_root])
            if translated and token[0].isupper():
                translated = translated.capitalize()
            if translated:
                translated_tokens.append(translated)
                i += 1
                continue

        # --- STEP 8: Irregular plural -> singular -> dictionary ---
        plural_root = lookup_irregular_plural(token_lower)
        if plural_root and plural_root in dictionary:
            translated = _get_nah(dictionary[plural_root])
            if translated and token[0].isupper():
                translated = translated.capitalize()
            if translated:
                translated_tokens.append(translated)
                i += 1
                continue

        # --- STEP 9: Comparative -> base -> dictionary ---
        comp_root = lookup_comparative(token_lower)
        if comp_root and comp_root in dictionary:
            translated = _get_nah(dictionary[comp_root])
            if translated and token[0].isupper():
                translated = translated.capitalize()
            if translated:
                translated_tokens.append(translated)
                i += 1
                continue

        # --- STEP 10: Suffix stripping -> dictionary ---
        root, suffix = try_suffix_stripping(token_lower)
        if root and root in dictionary:
            translated = _get_nah(dictionary[root])
            if translated and token[0].isupper():
                translated = translated.capitalize()
            if translated:
                translated_tokens.append(translated)
                i += 1
                continue

        # --- STEP 10b: English verb → Nahuatl conjugation ---
        # Detect if this is a conjugated English verb, find infinitive,
        # look up Nahuatl root, and conjugate properly
        verb_infinitive, verb_tense = find_verb_info(token_lower)
        if verb_infinitive:
            # Find subject pronoun for conjugation
            subject = _find_subject_before(i, tokens)
            if not subject:
                subject = "he"  # default

            # Try to conjugate
            conjugated = translate_and_conjugate(token_lower, subject, dictionary)
            if conjugated:
                if token[0].isupper():
                    conjugated = conjugated.capitalize()
                translated_tokens.append(conjugated)
                i += 1
                continue

        # --- STEP 10c: Try synonyms ---
        if token_lower in SYNONYMS:
            synonym_found = False
            for synonym in SYNONYMS[token_lower]:
                if synonym in dictionary:
                    translated = _get_nah(dictionary[synonym])
                    if translated and token[0].isupper():
                        translated = translated.capitalize()
                    if translated:
                        translated_tokens.append(translated)
                        synonym_found = True
                        break
                syn_root, _ = try_suffix_stripping(synonym)
                if syn_root and syn_root in dictionary:
                    translated = _get_nah(dictionary[syn_root])
                    if translated and token[0].isupper():
                        translated = translated.capitalize()
                    if translated:
                        translated_tokens.append(translated)
                        synonym_found = True
                        break
            if synonym_found:
                i += 1
                continue

        # --- STEP 10d: Direct English → Nahuatl fallback ---
        if token_lower in DIRECT_EN_NAH:
            translated = DIRECT_EN_NAH[token_lower]
            if translated:  # Skip empty strings (like "the")
                if token[0].isupper():
                    translated = translated.capitalize()
                translated_tokens.append(translated)
                i += 1
                continue
            else:
                i += 1
                continue

        # --- STEP 10d: English → Spanish → Nahuatl ---
        if token_lower in EN_TO_ES:
            spanish_word = EN_TO_ES[token_lower]
            if spanish_word in dictionary:
                translated = _get_nah(dictionary[spanish_word])
                if translated and token[0].isupper():
                    translated = translated.capitalize()
                if translated:
                    translated_tokens.append(translated)
                    i += 1
                    continue
            # Try Spanish word with suffix stripping
            es_root, _ = try_suffix_stripping(spanish_word)
            if es_root and es_root in dictionary:
                translated = _get_nah(dictionary[es_root])
                if translated and token[0].isupper():
                    translated = translated.capitalize()
                if translated:
                    translated_tokens.append(translated)
                    i += 1
                    continue

        # --- STEP 11: Unknown ---
        unknown_words.add(token_lower)
        translated_tokens.append(token)
        i += 1

    return ''.join(translated_tokens)


def _next_word_token(index, tokens):
    """Find the next non-whitespace token. Returns (word, offset) or (None, None)."""
    for j in range(index + 1, len(tokens)):
        if tokens[j].strip():
            return tokens[j].lower(), j
    return None, None


def _find_subject_before(index, tokens):
    """Find the subject pronoun before a verb in the token list."""
    pronouns = {"i", "you", "he", "she", "it", "we", "they"}
    for j in range(index - 1, max(index - 8, -1), -1):
        if j < 0:
            break
        word = tokens[j].lower().strip()
        if word in pronouns:
            return word
    return None
