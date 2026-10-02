#!/usr/bin/env python3
"""
build_dict.py — Parse Nahuatl dictionary PDFs and build an English→Nahuatl JSON lookup.

Usage:
    python build_dict.py                          # uses default Karttunen PDF
    python build_dict.py dict1.pdf dict2.pdf      # use custom PDFs

Output: dictionary.json  ({"english_word": "nahuatl_word", ...})
"""

import json
import re
import sys
import os
from pypdf import PdfReader

# Portable path configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Default dictionary PDFs
IDIEZ_PDF = os.path.join(SCRIPT_DIR, "sources", "IDIEZ_Dictionary.pdf")
KARTTUNEN_PDF = os.path.join(SCRIPT_DIR, "sources", "Karttunen 1992 An Analytical Dictionary of Nahuatl.pdf")

OUTPUT_DIR = SCRIPT_DIR
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dictionary.json")

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'shall', 'can', 'need', 'dare',
    'ought', 'used', 'it', 'its', 'this', 'that', 'these', 'those', 'i',
    'you', 'he', 'she', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'our', 'their', 'mine', 'yours', 'hers', 'ours',
    'theirs', 'what', 'which', 'who', 'whom', 'whose', 'where', 'when',
    'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
    'so', 'than', 'too', 'very', 'just', 'don', 'now', 'also', 'one',
    'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'something', 'someone', 'somebody', 'anything', 'anyone', 'anybody',
    'nothing', 'noone', 'nobody', 'everything', 'everyone', 'everybody',
    'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there',
    'about', 'against', 'because', 'until', 'while', 'although', 'though',
    'if', 'unless', 'whether', 'as', 'since', 'upon', 'within', 'without',
    'along', 'among', 'across', 'behind', 'beyond', 'beside', 'besides',
    'around', 'down', 'off', 'out', 'over', 'up', 'any', 'many', 'much',
    'university', 'attestations', 'organization', 'see', 'also', 'cf',
    'etc', 'vs', 'per', 'via', 'ie', 'eg',
}


def extract_text_from_pdf(pdf_path, start_page=0):
    """Extract text from a PDF file.

    Args:
        pdf_path: path to the PDF file
        start_page: first page to extract (0-based). Use 1 to skip intro page.
    """
    print(f"  Reading: {pdf_path}")
    reader = PdfReader(pdf_path)
    print(f"  Pages: {len(reader.pages)}")
    if start_page > 0:
        print(f"  Skipping first {start_page} page(s)")
    full_text = ""
    for i in range(start_page, len(reader.pages)):
        full_text += reader.pages[i].extract_text() + "\n"
    return full_text


def parse_karttunen_entries(text):
    """
    Parse Karttunen dictionary entries from extracted text.

    Entry patterns:
        CECUlZ- TLI pI: -MEH something cold; high mountain place / frio (M)
        CEHCELIA vrefl, vt to cool off; to cool something off / enfriar (M)
        CEHU(A) to be cold / hacer frio (M)
        CEHUAL-LI shadow of something / sombra de alguna cosa (M)
    """
    entries = {}
    skipped = 0

    headword_pattern = re.compile(
        r'^([A-ZÁÉÍÓÚÜ][A-ZÁÉÍÓÚÜ\-()0-9.,]*[A-ZÁÉÍÓÚÜ0-9])\s+'
        r'(?:[a-z]{2,6}[,\s]\s*)*'
        r'([a-záéíóúüñ])',
        re.MULTILINE
    )

    matches = list(headword_pattern.finditer(text))

    for i, match in enumerate(matches):
        headword = match.group(1).strip()
        start_pos = match.start()

        if i + 1 < len(matches):
            line_end = matches[i + 1].start()
        else:
            line_end = min(start_pos + 500, len(text))

        entry_text = text[start_pos:line_end]
        first_lines = entry_text.split('\n')[:3]
        def_text = ' '.join(first_lines)

        if len(headword) < 2:
            skipped += 1
            continue
        if headword in ('INTRODUCTION', 'COMMENTARY', 'TABLE', 'APPENDIX',
                        'USER', 'GUIDE', 'ACKNOWLEDGMENTS', 'REFERENCES',
                        'FOLIO', 'PAGE', 'VOLUME', 'CHAPTER', 'SEE'):
            skipped += 1
            continue

        def_match = re.match(
            r'^[A-ZÁÉÍÓÚÜ][A-ZÁÉÍÓÚÜ\-()0-9.,]*[A-ZÁÉÍÓÚÜ0-9]\s+'
            r'(?:[a-z]{2,6}[,\s]\s*)*'
            r'(.+?)(?:\s*/|\s*\(|\s*\[|$)',
            def_text,
            re.DOTALL
        )

        if not def_match:
            skipped += 1
            continue

        english_def = def_match.group(1).strip()
        english_def = re.sub(r'\s*\([A-Z]\)\s*$', '', english_def)
        english_def = re.sub(r'\s*\[.*?\]\s*$', '', english_def)
        english_def = re.sub(r'\s*See\s+[A-Z].*$', '', english_def)
        english_def = re.sub(r'\s*redup\.\s+[A-Z].*$', '', english_def)
        english_def = re.sub(r'\s*(applic|caus|nonact|altern|calis)\.\s+[A-Z].*$', '', english_def)
        english_def = re.sub(r'\s+', ' ', english_def).strip()
        english_def = english_def.rstrip('.,;:')

        if len(english_def) < 3:
            skipped += 1
            continue
        if english_def.startswith('This ') and len(english_def) < 40:
            skipped += 1
            continue
        if english_def.startswith('Both ') or english_def.startswith('Although '):
            skipped += 1
            continue

        entries[headword] = english_def

    print(f"  Parsed {len(entries)} entries, skipped {skipped} false matches")
    return entries


def parse_idiez_entries(text):
    """
    Parse IDIEZ Nahuatl-Spanish-English dictionary entries.

    Entry format: word. tlach/tlat/quen. Spanish def. English def.
    Entries run continuously in text (not on separate lines).

    Classification:
      tlach1-4 = verb (class 1-4)
      tlat = noun
      tlap = preposition/locative/temporal marker
      quen/quenun = adjective/adverb

    Returns dict: {headword: {"english": def, "cat": category, "verb_class": N or None}}
    """
    entries = {}
    skipped = 0

    # Remove copyright headers and noise
    text = re.sub(r'©.*?IDIEZ.*?org\s+\d+\s*', ' ', text)
    text = re.sub(r'Diccionario Náhuatl.*?Inglés\s*', ' ', text)
    text = re.sub(r'Instituto de Docencia.*?estudiante\s*', ' ', text)

    # Split on entry boundaries: word. category.
    split_pattern = re.compile(
        r'([a-zāēīōūáéíóúüñśš]+[0-9]*)\.\s+'
        r'(tlach\d+(?:/\d+)*|tlat|tlap|quen|quenun|adv|adj|prep|interj|conj|num)\.\s+'
    )

    parts = split_pattern.split(text)

    for i in range(1, len(parts), 3):
        if i + 2 >= len(parts):
            break

        raw_headword = parts[i].strip().lower()
        raw_category = parts[i+1].strip()
        definition = parts[i+2].strip()

        if len(raw_headword) < 2:
            skipped += 1
            continue

        # Strip trailing numbers from headword (e.g., aacalaquia1 → aacalaquia)
        headword = re.sub(r'[0-9]+$', '', raw_headword)

        # Extract verb class from tlach (e.g., tlach3 → class "3")
        verb_class = None
        category = raw_category
        if raw_category.startswith('tlach'):
            class_match = re.match(r'tlach(\d+)', raw_category)
            if class_match:
                verb_class = class_match.group(1)
                category = 'tlach'

        # Clean definition: remove PANOC references, normalize whitespace
        definition = re.sub(r'PANOC:\s+.+?(?=\s+[a-zāēīōūáéíóúüñśš]+[0-9]*\.\s+(?:tlach|tlat|tlap|quen)|$)', '', definition)
        definition = re.sub(r'\s+', ' ', definition).strip()

        # Extract English definition by finding the FIRST English marker
        # anywhere in the text. Everything before = Spanish, after = English.
        spanish_def = ""
        english_def = ""

        eng_markers = [
            'To ', 'to ', 'For ', 'for ',
            'S.o.', 's.o.', 'S.t.', 's.t.',
            'Someone', 'someone', 'Something', 'something',
            'Anyone', 'anyone', 'Anything', 'anything',
            'Nothing', 'nothing',
        ]

        eng_pos = None
        for marker in eng_markers:
            pos = definition.find(marker)
            if pos >= 0 and (eng_pos is None or pos < eng_pos):
                eng_pos = pos

        if eng_pos is not None:
            # Verify it's at a word boundary (preceded by space, period, digit, or start)
            if eng_pos == 0 or definition[eng_pos - 1] in ' .0123456789':
                spanish_def = definition[:eng_pos].strip().rstrip('.')
                english_def = definition[eng_pos:].strip()

        if not english_def:
            # Fallback 1: Handle numbered definitions (e.g., "1. Spanish... 2. Spanish... 1. English... 2. English...")
            # Split on numbered patterns and find English text
            numbered_parts = re.split(r'\d+\.\s*', definition)
            if len(numbered_parts) >= 3:
                # Take the last 1-2 parts as English (after Spanish numbered defs)
                english_parts = numbered_parts[-2:] if len(numbered_parts) >= 4 else [numbered_parts[-1]]
                english_def = '. '.join(english_parts).strip()
                spanish_def = '. '.join(numbered_parts[:-2]).strip() if len(numbered_parts) > 2 else ''

        if not english_def:
            # Fallback 2: split on ". " and take last sentence as English
            sentences = re.split(r'\.\s+', definition)
            if len(sentences) >= 2:
                spanish_def = '. '.join(sentences[:-1]).strip()
                english_def = sentences[-1].strip()
            else:
                english_def = definition

        spanish_def = re.sub(r'\s+', ' ', spanish_def).strip()
        english_def = re.sub(r'\s+', ' ', english_def).strip()
        english_def = english_def.rstrip('.,;:')

        if not english_def or len(english_def) < 3:
            skipped += 1
            continue

        if english_def.startswith('See ') or english_def.startswith('Vea '):
            skipped += 1
            continue

        # Split sub-entries within a single English definition
        # e.g., "1. for a quantity to be sufficient after all. 2. to arrive after all."
        # → ["for a quantity to be sufficient after all", "to arrive after all"]
        sub_defs = re.split(r'\d+\.\s+', english_def)
        sub_defs = [s.strip().rstrip('.,;:') for s in sub_defs if s.strip()]
        # Also split on semicolons if no numbering but multiple meanings
        if len(sub_defs) == 1 and ';' in english_def:
            sub_defs = [s.strip().rstrip('.,;:') for s in english_def.split(';') if s.strip()]
        sub_defs = [s for s in sub_defs if len(s) >= 3]
        if not sub_defs:
            skipped += 1
            continue

        # Store with metadata — merge duplicate headwords (Option B: list of definitions)
        if headword in entries:
            existing = entries[headword]
            if not isinstance(existing['english'], list):
                existing['english'] = [existing['english']]
            existing['english'].extend(sub_defs)
        else:
            entries[headword] = {
                "english": sub_defs if len(sub_defs) > 1 else sub_defs[0],
                "cat": category,
                "verb_class": verb_class,
            }

    print(f"  Parsed {len(entries)} IDIEZ entries, skipped {skipped} false matches")
    return entries


def extract_primary_english(english_def):
    """Extract the primary English meaning from a definition."""
    primary = english_def.split(';')[0].strip()
    if len(primary.split()) <= 4 and ',' in primary:
        primary = primary.split(',')[0].strip()
    return primary


def validate_dictionary_entries(entries, is_idiez=False):
    """Filter out bad entries from parsed dictionary.
    
    The parsers sometimes extract English words from definition
    text as dictionary keys (e.g., "taken" from "a meal taken upon rising").
    This function removes those bad entries.
    
    Args:
        entries: dictionary entries to validate
        is_idiez: if True, use IDIEZ-specific rules (more lenient)
    
    Returns cleaned dictionary.
    """
    # Common English words that should NOT be dictionary keys
    # (these are likely extracted from definitions by mistake)
    english_stop = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'shall', 'can', 'need', 'dare',
        'ought', 'used', 'it', 'its', 'this', 'that', 'these', 'those', 'i',
        'you', 'he', 'she', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'its', 'our', 'their', 'mine', 'yours', 'hers',
        'ours', 'theirs', 'what', 'which', 'who', 'whom', 'whose', 'where',
        'when', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'than', 'too', 'very', 'just', 'don', 'now', 'also',
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
        'nine', 'ten', 'something', 'someone', 'somebody', 'anything',
        'anyone', 'anybody', 'nothing', 'noone', 'nobody', 'everything',
        'everyone', 'everybody', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'between', 'under', 'again', 'further',
        'then', 'once', 'here', 'there', 'about', 'against', 'because',
        'until', 'while', 'although', 'though', 'if', 'unless', 'whether',
        'as', 'since', 'upon', 'within', 'without', 'along', 'among',
        'across', 'behind', 'beyond', 'beside', 'besides', 'around', 'down',
        'off', 'out', 'over', 'up', 'any', 'many', 'much', 'see', 'also',
        'cf', 'etc', 'vs', 'per', 'via', 'ie', 'eg',
        # Common verbs often extracted from definitions
        'taken', 'take', 'takes', 'taking', 'took', 'given', 'give', 'gives',
        'giving', 'gave', 'made', 'make', 'makes', 'making', 'found', 'find',
        'finding', 'known', 'know', 'knows', 'knew', 'seen', 'see', 'sees',
        'saw', 'said', 'say', 'says', 'told', 'tell', 'tells', 'telling',
        'brought', 'bring', 'brings', 'bringing', 'heard', 'hear', 'hears',
        'hearing', 'felt', 'feel', 'feels', 'feeling', 'thought', 'think',
        'thinks', 'thinking', 'came', 'come', 'comes', 'coming', 'went',
        'go', 'goes', 'going', 'gone', 'became', 'become', 'becomes',
        'becoming', 'stood', 'stand', 'stands', 'standing', 'sat', 'sit',
        'sits', 'sitting', 'lay', 'lie', 'lies', 'lying', 'fell', 'fall',
        'falls', 'falling', 'fallen', 'lost', 'lose', 'loses', 'losing',
        'paid', 'pay', 'pays', 'paying', 'met', 'meet', 'meets', 'meeting',
        'led', 'lead', 'leads', 'leading', 'meant', 'mean', 'means',
        'meaning', 'kept', 'keep', 'keeps', 'keeping', 'left', 'leave',
        'leaves', 'leaving', 'let', 'lets', 'letting', 'put', 'puts',
        'putting', 'set', 'sets', 'setting', 'cut', 'cuts', 'cutting',
        'hit', 'hits', 'hitting', 'hurt', 'hurts', 'hurting', 'cost',
        'costs', 'costing', 'spread', 'spreads', 'spreading', 'rose',
        'rise', 'rises', 'rising', 'risen', 'shook', 'shake', 'shakes',
        'shaking', 'shaken', 'stole', 'steal', 'steals', 'stealing',
        'stolen', 'forgot', 'forget', 'forgets', 'forgetting', 'forgotten',
        'forgave', 'forgive', 'forgives', 'forgiving', 'forgiven', 'hid',
        'hide', 'hides', 'hiding', 'hidden', 'bit', 'bite', 'bites',
        'biting', 'bitten', 'shone', 'shine', 'shines', 'shining', 'sank',
        'sink', 'sinks', 'sinking', 'sunk', 'swung', 'swing', 'swings',
        'swinging', 'stuck', 'stick', 'sticks', 'sticking', 'spun', 'spin',
        'spins', 'spinning', 'crept', 'creep', 'creeps', 'creeping',
        'slept', 'sleep', 'sleeps', 'sleeping', 'swept', 'sweep', 'sweeps',
        'sweeping', 'wept', 'weep', 'weeps', 'weeping', 'fed', 'feed',
        'feeds', 'feeding', 'fled', 'flee', 'flees', 'fleeing', 'hung',
        'hang', 'hangs', 'hanging', 'taught', 'teach', 'teaches',
        'teaching', 'sold', 'sell', 'sells', 'selling', 'bought', 'buy',
        'buys', 'buying', 'caught', 'catch', 'catches', 'catching',
        'fought', 'fight', 'fights', 'fighting', 'sought', 'seek', 'seeks',
        'seeking', 'built', 'build', 'builds', 'building', 'lent', 'lend',
        'lends', 'lending', 'spent', 'spend', 'spends', 'spending', 'sent',
        'send', 'sends', 'sending', 'dealt', 'deal', 'deals', 'dealing',
        'won', 'win', 'wins', 'winning', 'held', 'hold', 'holds', 'holding',
        'dug', 'dig', 'digs', 'digging', 'bound', 'bind', 'binds',
        'binding', 'bent', 'bend', 'bends', 'bending', 'lit', 'light',
        'lights', 'lighting', 'lighted', 'slid', 'slide', 'slides',
        'sliding', 'shut', 'shuts', 'shutting', 'split', 'splits',
        'splitting', 'quit', 'quits', 'quitting', 'bet', 'bets',
        'betting', 'cast', 'casts', 'casting', 'thrust', 'thrusts',
        'thrusting', 'burst', 'bursts', 'bursting', 'broadcast',
        'broadcasts', 'broadcasting', 'misled', 'mislead', 'misleads',
        'misleading', 'upset', 'upsets', 'upsetting', 'withstood',
        'withstand', 'withstands', 'withstanding', 'overtook', 'overtake',
        'overtakes', 'overtaking', 'overtaken', 'mistook', 'mistake',
        'mistakes', 'mistaking', 'mistaken', 'proved', 'prove', 'proves',
        'proving', 'proven', 'provided', 'provide', 'provides', 'providing',
        'required', 'require', 'requires', 'requiring', 'supposed',
        'suppose', 'supposes', 'supposing', 'used', 'use', 'uses', 'using',
        'tried', 'try', 'tries', 'trying', 'wanted', 'want', 'wants',
        'wanting', 'needed', 'need', 'needs', 'needing', 'called', 'call',
        'calls', 'calling', 'asked', 'ask', 'asks', 'asking', 'answered',
        'answer', 'answers', 'answering', 'worked', 'work', 'works',
        'working', 'lived', 'live', 'lives', 'living', 'died', 'die',
        'dies', 'dying', 'killed', 'kill', 'kills', 'killing', 'loved',
        'love', 'loves', 'loving', 'hated', 'hate', 'hates', 'hating',
        'helped', 'help', 'helps', 'helping', 'hoped', 'hope', 'hopes',
        'hoping', 'feared', 'fear', 'fears', 'fearing', 'cried', 'cry',
        'cries', 'crying', 'laughed', 'laugh', 'laughs', 'laughing',
        'smiled', 'smile', 'smiles', 'smiling', 'shouted', 'shout',
        'shouts', 'shouting', 'whispered', 'whisper', 'whispers',
        'whispering', 'promised', 'promise', 'promises', 'promising',
        'agreed', 'agree', 'agrees', 'agreeing', 'refused', 'refuse',
        'refuses', 'refusing', 'allowed', 'allow', 'allows', 'allowing',
        'ordered', 'order', 'orders', 'ordering', 'begged', 'beg', 'begs',
        'begging', 'warned', 'warn', 'warns', 'warning', 'advised',
        'advise', 'advises', 'advising', 'suggested', 'suggest', 'suggests',
        'suggesting', 'explained', 'explain', 'explains', 'explaining',
        'described', 'describe', 'describes', 'describing', 'counted',
        'count', 'counts', 'counting', 'measured', 'measure', 'measures',
        'measuring', 'mixed', 'mix', 'mixes', 'mixing', 'cooked', 'cook',
        'cooks', 'cooking', 'baked', 'bake', 'bakes', 'baking', 'boiled',
        'boil', 'boils', 'boiling', 'fried', 'fry', 'fries', 'frying',
        'washed', 'wash', 'washes', 'washing', 'cleaned', 'clean', 'cleans',
        'cleaning', 'dried', 'dry', 'dries', 'drying', 'burned', 'burn',
        'burns', 'burning', 'burnt', 'melted', 'melt', 'melts', 'melting',
        'flowed', 'flow', 'flows', 'flowing', 'poured', 'pour', 'pours',
        'pouring', 'filled', 'fill', 'fills', 'filling', 'emptied', 'empty',
        'empties', 'emptying', 'tied', 'tie', 'ties', 'tying', 'loosed',
        'loose', 'looses', 'loosing', 'freed', 'free', 'frees', 'freeing',
        'hunted', 'hunt', 'hunts', 'hunting', 'planted', 'plant', 'plants',
        'planting', 'harvested', 'harvest', 'harvests', 'harvesting',
        'buried', 'bury', 'buries', 'burying', 'covered', 'cover', 'covers',
        'covering', 'wrapped', 'wrap', 'wraps', 'wrapping', 'folded',
        'fold', 'folds', 'folding', 'stretched', 'stretch', 'stretches',
        'stretching', 'reached', 'reach', 'reaches', 'reaching', 'touched',
        'touch', 'touches', 'touching', 'pressed', 'press', 'presses',
        'pressing', 'crushed', 'crush', 'crushes', 'crushing', 'trembled',
        'tremble', 'trembles', 'trembling', 'glowed', 'glow', 'glows',
        'glowing', 'darkened', 'darken', 'darkens', 'darkening',
        'brightened', 'brighten', 'brightens', 'brightening', 'cleared',
        'clear', 'clears', 'clearing', 'rained', 'rain', 'rains',
        'raining', 'snowed', 'snow', 'snows', 'snowing', 'thundered',
        'thunder', 'thunders', 'thundering',
        # Common nouns/adjectives from definitions
        'breakfast', 'meal', 'sustenance', 'rising', 'something', 'someone',
        'place', 'person', 'thing', 'water', 'fire', 'earth', 'air',
        'house', 'home', 'tree', 'stone', 'mountain', 'river', 'sea',
        'sun', 'moon', 'star', 'sky', 'night', 'day', 'morning', 'evening',
        'year', 'month', 'week', 'time', 'life', 'death', 'love', 'hate',
        'good', 'bad', 'big', 'small', 'long', 'short', 'high', 'low',
        'hot', 'cold', 'warm', 'cool', 'hard', 'soft', 'fast', 'slow',
        'new', 'old', 'young', 'beautiful', 'ugly', 'happy', 'sad',
        'strong', 'weak', 'rich', 'poor', 'clean', 'dirty', 'true', 'false',
        'right', 'wrong', 'dark', 'light', 'heavy', 'thin', 'thick',
        'wide', 'narrow', 'deep', 'shallow', 'full', 'empty', 'whole',
        'part', 'half', 'many', 'few', 'much', 'little', 'more', 'less',
        'most', 'least', 'all', 'some', 'any', 'no', 'every', 'each',
        'other', 'another', 'same', 'different', 'first', 'last', 'next',
        'previous', 'present', 'past', 'future', 'early', 'late', 'soon',
        'now', 'then', 'here', 'there', 'where', 'when', 'why', 'how',
        'what', 'who', 'which', 'whose', 'whom',
        # Words extracted from IDIEZ definitions
        'take', 'takes', 'taking', 'took', 'taken',
        'grab', 'grabs', 'grabbing', 'grabbed',
        'community', 'members', 'collective', 'task', 'participan',
        'comunidad', 'colectiva', 'tarea',
    }

    cleaned = {}
    removed = 0

    for key, value in entries.items():
        key_lower = key.lower().strip()

        # For IDIEZ entries with metadata, extract the English definition
        if isinstance(value, dict):
            eng_def = value.get("english", "")
        else:
            eng_def = value

        # Ensure eng_def is a string for string operations
        eng_def_str = " ".join(eng_def) if isinstance(eng_def, list) else (eng_def or "")

        # Rule 1: Skip if key is a common English word
        if key_lower in english_stop:
            removed += 1
            continue

        # Rule 2: Skip if key appears inside the English definition
        if len(key_lower) > 2 and key_lower in eng_def_str.lower():
            removed += 1
            continue

        # Rule 3: Skip if key starts with non-letter (numbers, punctuation)
        if key and not key[0].isalpha():
            removed += 1
            continue

        # Rule 4: Skip if key is too short (less than 2 letters)
        if len(key_lower) < 2:
            removed += 1
            continue

        # Rules 5-7: Only apply to Karttunen (IDIEZ entries can have spaces/commas)
        if not is_idiez:
            # Rule 5: Skip if value looks like a full definition sentence
            if ',' in eng_def or '/' in eng_def or len(eng_def) > 50:
                removed += 1
                continue

            # Rule 6: Skip if value contains spaces (likely a definition, not a word)
            if ' ' in value:
                removed += 1
                continue

            # Rule 7: Skip if key is a single letter (except valid Nahuatl particles)
            if len(key_lower) == 1 and key_lower not in ('a', 'i', 'o', 'e', 'u'):
                removed += 1
                continue

        cleaned[key] = value

    print(f"  Dictionary validation: removed {removed} bad entries, kept {len(cleaned)}")
    return cleaned


def _invert_single_def(english_def, meta, word_map, phrase_map, is_verb=False):
    """Invert a single English definition.

    For verbs: use POS tagging (spaCy or heuristic) to find the real verb,
    then extract verb + first noun/adj as phrase.
    For nouns/adjectives: extract individual content words + short phrase.
    """
    english_lower = english_def.lower().strip()
    words = english_lower.split()

    # Extract content words (skip STOP_WORDS)
    content_words = []
    for w in words:
        w_clean = re.sub(r'[^a-záéíóúüñ]', '', w)
        if w_clean and w_clean not in STOP_WORDS and len(w_clean) > 2:
            content_words.append(w_clean)

    if not content_words:
        return

    if is_verb:
        # Try spaCy first
        verb = None
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
            doc = nlp(english_lower)
            for token in doc:
                if token.pos_ == "VERB":
                    verb = token.lemma_
                    break
                if token.pos_ == "AUX" and verb is None:
                    # "be sufficient" → look for complement
                    for t2 in doc:
                        if t2.i > token.i and t2.pos_ in ("ADJ", "NOUN", "VERB"):
                            verb = f"be {t2.lemma_}"
                            break
        except (ImportError, OSError):
            pass

        # Fallback heuristic
        if not verb:
            AUX_VERBS = {"be", "have", "do", "get", "make", "let", "come", "go"}
            for i, w in enumerate(words):
                w_clean = re.sub(r'[^a-záéíóúüñ]', '', w)
                if w_clean == "to" and i + 1 < len(words):
                    next_word = re.sub(r'[^a-záéíóúüñ]', '', words[i + 1])
                    if next_word and next_word not in STOP_WORDS and len(next_word) > 2:
                        if next_word == "be":
                            for j in range(i + 2, len(words)):
                                cand = re.sub(r'[^a-záéíóúüñ]', '', words[j])
                                if cand and cand not in STOP_WORDS and len(cand) > 2:
                                    if cand not in AUX_VERBS:
                                        verb = f"be {cand}"
                                        break
                        else:
                            verb = next_word
                        break
            if not verb:
                verb = content_words[0]

        # Store verb alone
        verb_key = verb.split()[0]
        if verb_key not in word_map:
            word_map[verb_key] = dict(meta)

        # Find anchor (first non-verb content word)
        verb_words_set = set(verb.split())
        anchor = None
        for cw in content_words:
            if cw not in verb_words_set:
                anchor = cw
                break

        if anchor:
            phrase = f"{verb} {anchor}"
            if phrase not in phrase_map:
                phrase_map[phrase] = dict(meta)
    else:
        # For nouns/adjectives: extract content words
        for word in content_words:
            if word not in word_map:
                word_map[word] = dict(meta)
        # Keep short full definitions as phrases (≤4 words)
        if len(content_words) <= 4:
            if english_lower not in phrase_map:
                phrase_map[english_lower] = dict(meta)


def _invert_tlach_overlap(definitions, meta, word_map, phrase_map):
    """Invert a verb with multiple definitions using semantic overlap.

    1. Find content words that appear in 2+ definitions (the semantic core)
    2. For each definition: extract verb + overlap word (or first noun)
    3. Also extract verb alone as fallback
    """
    from collections import Counter

    # Try to load spaCy for POS tagging; fall back to heuristics
    _spacy_nlp = None
    try:
        import spacy
        _spacy_nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    except (ImportError, OSError):
        pass

    def _find_verb_spacy(text):
        """Use spaCy POS tagging to find the real infinitive verb.
        
        Strategy: find the first VERB token (not AUX). If the only verb
        is "be", return "be" + adjective/complement as the phrase.
        """
        doc = _spacy_nlp(text.lower())
        for token in doc:
            if token.pos_ == "VERB":
                return token.lemma_  # infinitive form (e.g., "arrive", "take")
        # Fallback: if no VERB found, find first AUX
        for token in doc:
            if token.pos_ == "AUX":
                # "be sufficient" → return "be sufficient"
                next_content = None
                for t2 in doc:
                    if t2.i > token.i and t2.pos_ in ("ADJ", "NOUN", "VERB"):
                        next_content = t2.lemma_
                        break
                if next_content:
                    return f"be {next_content}"
                return None
        return None

    def _find_verb_heuristic(content_words, all_words):
        """Fallback without spaCy: find verb after 'to' with POS awareness."""
        if not content_words:
            return None
        # Find 'to' and check if next word is a real verb
        AUX_VERBS = {"be", "have", "do", "get", "make", "let", "come", "go"}
        for i, w in enumerate(all_words):
            if w == "to" and i + 1 < len(all_words):
                next_word = re.sub(r'[^a-záéíóúüñ]', '', all_words[i + 1])
                if next_word and next_word not in STOP_WORDS and len(next_word) > 2:
                    # If it's "be", look for the adjective/noun complement
                    if next_word == "be":
                        # Find next content word after "be"
                        for j in range(i + 2, len(all_words)):
                            cand = re.sub(r'[^a-záéíóúüñ]', '', all_words[j])
                            if cand and cand not in STOP_WORDS and len(cand) > 2:
                                # Skip if it's an auxiliary/modal
                                if cand not in AUX_VERBS:
                                    return f"be {cand}"
                    return next_word
        return content_words[0]

    # Extract content words AND all words per definition
    def_word_sets = []
    def_all_words = []
    for d in definitions:
        words = re.findall(r'[a-záéíóúüñ]+', d.lower())
        content = [w for w in words if w not in STOP_WORDS and len(w) > 2]
        def_word_sets.append(content)
        def_all_words.append(words)

    # Find overlap: words appearing in 2+ definitions
    all_counts = Counter()
    for ws in def_word_sets:
        all_counts.update(set(ws))
    overlap = {w for w, c in all_counts.items() if c >= 2}

    for content_words, all_words in zip(def_word_sets, def_all_words):
        if not content_words:
            continue

        # Find verb using spaCy or heuristic
        if _spacy_nlp:
            full_text = ' '.join(all_words)
            verb = _find_verb_spacy(full_text)
        else:
            verb = _find_verb_heuristic(content_words, all_words)

        if not verb:
            continue

        # Extract verb alone
        # For multi-word verbs like "be sufficient", extract the full phrase
        verb_key = verb.split()[0]  # first word for lookup
        if verb_key not in word_map:
            word_map[verb_key] = dict(meta)

        # Find overlap word in this definition
        anchor = None
        for cw in content_words:
            if cw in overlap and cw != verb_key and cw not in verb.split():
                anchor = cw
                break

        # If no overlap, use first non-verb content word
        if not anchor:
            verb_words = verb.split()
            for cw in content_words:
                if cw not in verb_words:
                    anchor = cw
                    break

        if anchor:
            phrase = f"{verb} {anchor}"
            if phrase not in phrase_map:
                phrase_map[phrase] = dict(meta)


def invert_dictionary(nahuatl_to_english):
    """Invert Nahuatl→English to English→Nahuatl.

    Dispatches to _invert_idiez() or _invert_karttunen() based on entry format.
    """
    idiez_entries = {}
    karttunen_entries = {}

    for nahuatl, entry in nahuatl_to_english.items():
        if isinstance(entry, dict) and entry.get("cat"):
            # IDIEZ entries have metadata
            idiez_entries[nahuatl] = entry
        else:
            # Karttunen entries: bare strings or null cat
            karttunen_entries[nahuatl] = entry

    # Invert each type separately
    word_map = {}
    phrase_map = {}

    _invert_idiez(idiez_entries, word_map, phrase_map)
    _invert_karttunen(karttunen_entries, word_map, phrase_map)

    merged = {}
    merged.update(word_map)
    merged.update(phrase_map)
    return merged


def _invert_idiez(entries, word_map, phrase_map):
    """Invert IDIEZ entries (have metadata: cat, verb_class, list of defs)."""
    for nahuatl, entry in entries.items():
        english_data = entry.get("english", "")
        cat = entry.get("cat", None)
        verb_class = entry.get("verb_class", None)

        definitions = english_data if isinstance(english_data, list) else [english_data] if english_data else []
        if not definitions:
            continue

        meta = {"nah": nahuatl, "cat": cat, "verb_class": verb_class}

        if cat == "tlach" and len(definitions) > 1:
            _invert_tlach_overlap(definitions, meta, word_map, phrase_map)
        elif cat == "tlach":
            _invert_single_def(definitions[0], meta, word_map, phrase_map, is_verb=True)
        else:
            for defn in definitions:
                _invert_single_def(defn, meta, word_map, phrase_map, is_verb=False)


def _invert_karttunen(entries, word_map, phrase_map):
    """Invert Karttunen entries (bare strings or dicts with null cat).
    
    Karttunen entries are ALL CAPS with hyphens like "ACHICAHUAL-LI".
    Definitions are often short like "a downpour" or "a cold thing".
    Extract content words + keep short phrases intact.
    """
    for nahuatl, entry in entries.items():
        if isinstance(entry, dict):
            english_def = entry.get("english", "")
            cat = entry.get("cat", None)
            verb_class = entry.get("verb_class", None)
        else:
            english_def = entry
            cat = None
            verb_class = None

        english_lower = english_def.lower().strip()
        if not english_lower:
            continue

        meta = {"nah": nahuatl, "cat": cat, "verb_class": verb_class}

        # Extract content words
        words = re.findall(r'[a-záéíóúüñ]+', english_lower)
        for word in words:
            if len(word) > 2 and word not in STOP_WORDS and word not in word_map:
                word_map[word] = dict(meta)

        # Keep short full definitions as phrases (≤4 words)
        word_count = len(english_lower.split())
        if word_count <= 4:
            if english_lower not in phrase_map:
                phrase_map[english_lower] = dict(meta)


def build_dictionary(pdf_paths):
    """Main function: parse PDFs, build SEPARATE dictionaries.
    
    Creates:
      - dictionary_idiez.json (Modern Huasteca)
      - dictionary_karttunen.json (Classical Nahuatl)
    """
    idiez_entries = {}
    karttunen_entries = {}

    for pdf_path in pdf_paths:
        if not os.path.exists(pdf_path):
            print(f"WARNING: File not found: {pdf_path}")
            continue

        text = extract_text_from_pdf(pdf_path)

        # Detect dictionary type and use appropriate parser
        if 'tlach' in text.lower() and 'IDIEZ' in text:
            print("  Detected: IDIEZ Nahuatl-Spanish-English dictionary")
            # Skip page 1 (intro/explanatory text, no dictionary entries)
            text = extract_text_from_pdf(pdf_path, start_page=1)
            entries = parse_idiez_entries(text)
            # Validate IDIEZ entries (lenient - only remove English words from definitions)
            entries = validate_dictionary_entries(entries, is_idiez=True)
            idiez_entries.update(entries)
        else:
            print("  Detected: Karttunen-style dictionary")
            entries = parse_karttunen_entries(text)
            # Validate Karttunen entries (strict - remove bad parses)
            entries = validate_dictionary_entries(entries, is_idiez=False)
            karttunen_entries.update(entries)

    print(f"\n  IDIEZ entries: {len(idiez_entries)}")
    print(f"  Karttunen entries: {len(karttunen_entries)}")

    # Invert and save IDIEZ dictionary
    print("Inverting IDIEZ dictionary to English→Nahuatl...")
    idiez_dict = invert_dictionary(idiez_entries)
    # Validate inverted IDIEZ dictionary
    idiez_dict = validate_dictionary_entries(idiez_dict, is_idiez=True)
    idiez_path = os.path.join(SCRIPT_DIR, "dictionary_idiez.json")
    with open(idiez_path, 'w', encoding='utf-8') as f:
        json.dump(idiez_dict, f, ensure_ascii=False, indent=2)
    print(f"  IDIEZ dictionary saved: {idiez_path} ({len(idiez_dict)} entries)")

    # Invert and save Karttunen dictionary
    print("Inverting Karttunen dictionary to English→Nahuatl...")
    karttunen_dict = invert_dictionary(karttunen_entries)
    # Validate inverted Karttunen dictionary
    karttunen_dict = validate_dictionary_entries(karttunen_dict, is_idiez=False)
    karttunen_path = os.path.join(SCRIPT_DIR, "dictionary_karttunen.json")
    with open(karttunen_path, 'w', encoding='utf-8') as f:
        json.dump(karttunen_dict, f, ensure_ascii=False, indent=2)
    print(f"  Karttunen dictionary saved: {karttunen_path} ({len(karttunen_dict)} entries)")

    # Also save merged dictionary for backward compatibility
    print("\nCreating merged dictionary (IDIEZ priority)...")
    merged = {}
    merged.update(karttunen_dict)   # Karttunen first (lower priority)
    merged.update(idiez_dict)        # IDIEZ overwrites (higher priority)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"  Merged dictionary saved: {OUTPUT_FILE} ({len(merged)} entries)")

    print("\nSample IDIEZ entries:")
    for i, (eng, entry) in enumerate(sorted(idiez_dict.items())):
        if i >= 10:
            break
        if isinstance(entry, dict):
            nah = entry.get("nah", "?")
            cat = entry.get("cat", "")
            vc = entry.get("verb_class", "")
            vc_str = f" (class {vc})" if vc else ""
            cat_str = f" [{cat}{vc_str}]" if cat else ""
            print(f"  {eng!r} → {nah}{cat_str}")
        else:
            print(f"  {eng!r} → {entry}")

    print("\nSample Karttunen entries:")
    for i, (eng, entry) in enumerate(sorted(karttunen_dict.items())):
        if i >= 10:
            break
        if isinstance(entry, dict):
            nah = entry.get("nah", "?")
            cat = entry.get("cat", "")
            vc = entry.get("verb_class", "")
            vc_str = f" (class {vc})" if vc else ""
            cat_str = f" [{cat}{vc_str}]" if cat else ""
            print(f"  {eng!r} → {nah}{cat_str}")
        else:
            print(f"  {eng!r} → {entry}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_files = sys.argv[1:]
    else:
        pdf_files = [IDIEZ_PDF, KARTTUNEN_PDF]

    print("=" * 50)
    print("Nahuatl Dictionary Builder")
    print("=" * 50)
    build_dictionary(pdf_files)
