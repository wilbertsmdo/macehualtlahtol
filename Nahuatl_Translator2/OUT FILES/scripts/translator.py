#!/usr/bin/env python3
"""
translator.py — Translate an English PDF to Nahuatl (Huasteca) side-by-side PDF.

Usage:
    python translator.py input.pdf
    python translator.py input.pdf -o output.pdf
    python translator.py input.pdf --dict custom_dict.json

Output: Side-by-side PDF with English (left) and Nahuatl (right).
        Unknown words listed at the end.
"""

import json
import os
import re
import sys
import argparse
import shutil
import subprocess

# Auto-install missing dependencies
def _ensure_deps():
    missing = []
    for mod in ['pypdf', 'reportlab']:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
        print("Done installing dependencies.\n")

_ensure_deps()

# Import pypdf first (it checks PIL version)
from pypdf import PdfReader

# Mock PIL for reportlab (we don't use images) — skip if PIL already available
try:
    import PIL
except ImportError:
    class _MockImage:
        pass
    class _MockPIL:
        Image = _MockImage
        __version__ = "0.0.0"
    sys.modules['PIL'] = _MockPIL
    sys.modules['PIL.Image'] = _MockImage

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# Import grammar rules — all translation logic lives in grammar_rules.py
from grammar_rules import translate_with_grammar, clean_nahuatl_text

# Import unknown words tracker
from unknown_words import load_known_words, save_unknown_words, print_unknown_summary, filter_unknown_words

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DICT = os.path.join(SCRIPT_DIR, "dictionaries", "dictionary.json")
DICT_IDIEZ = os.path.join(SCRIPT_DIR, "dictionaries", "dictionary_idiez.json")
DICT_KARTTUNEN = os.path.join(SCRIPT_DIR, "dictionaries", "dictionary_karttunen.json")
PARALLEL_SENTENCES_PATH = os.path.join(SCRIPT_DIR, "parallel_sentences.json")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

# Layout constants
PAGE_WIDTH = letter[0]
MARGIN = 0.35 * inch
COL_GAP = 0.1 * inch
COL_WIDTH = (PAGE_WIDTH - 2 * MARGIN - COL_GAP) / 2


def load_dictionary(dict_path):
    """Load English->Nahuatl dictionary from JSON file."""
    if not os.path.exists(dict_path):
        print(f"ERROR: Dictionary not found: {dict_path}")
        print("Run build_dict.py first to generate dictionary.json")
        sys.exit(1)
    with open(dict_path, 'r', encoding='utf-8') as f:
        dictionary = json.load(f)
    print(f"Loaded {len(dictionary)} dictionary entries from {os.path.basename(dict_path)}")
    return dictionary


def load_parallel_sentences():
    """Load parallel sentences for testing."""
    if not os.path.exists(PARALLEL_SENTENCES_PATH):
        return []
    with open(PARALLEL_SENTENCES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_translation_quality(dictionary, known_words=None):
    """Test translation quality using parallel sentences.
    
    Returns:
        (score, results) where score is 0-100 and results is list of test results
    """
    sentences = load_parallel_sentences()
    if not sentences:
        return 0, []
    
    results = []
    correct = 0
    
    for s in sentences:
        nah_expected = s['nahuatl']
        eng = s['english']
        
        # Translate English to Nahuatl
        result, unknown, ctx = translate_text(eng, dictionary, known_words)
        
        # Check if expected Nahuatl appears in result
        nah_expected_clean = nah_expected.lower().strip('.!?')
        result_clean = result.lower()
        
        # Simple matching: check if expected word/phrase is in result
        match = nah_expected_clean in result_clean or nah_expected_clean.split()[0] in result_clean
        
        if match:
            correct += 1
            results.append({
                'english': eng,
                'expected': nah_expected,
                'got': result.strip(),
                'correct': True
            })
        else:
            results.append({
                'english': eng,
                'expected': nah_expected,
                'got': result.strip(),
                'correct': False
            })
    
    score = (correct / len(sentences)) * 100 if sentences else 0
    return score, results


def load_dictionaries():
    """Load both IDIEZ and Karttunen dictionaries.
    
    Returns:
        (idiez_dict, karttunen_dict, merged_dict)
        IDIEZ has priority, Karttunen is fallback.
    """
    idiez_dict = {}
    karttunen_dict = {}

    # Load IDIEZ
    if os.path.exists(DICT_IDIEZ):
        with open(DICT_IDIEZ, 'r', encoding='utf-8') as f:
            idiez_dict = json.load(f)
        print(f"📖 IDIEZ dictionary: {len(idiez_dict)} entries")
    else:
        print("⚠️  IDIEZ dictionary not found (run build_dict.py)")

    # Load Karttunen
    if os.path.exists(DICT_KARTTUNEN):
        with open(DICT_KARTTUNEN, 'r', encoding='utf-8') as f:
            karttunen_dict = json.load(f)
        print(f"📖 Karttunen dictionary: {len(karttunen_dict)} entries")
    else:
        print("⚠️  Karttunen dictionary not found (run build_dict.py)")

    # Merge: IDIEZ priority, Karttunen fallback
    merged = {}
    merged.update(karttunen_dict)
    merged.update(idiez_dict)

    if merged:
        print(f"📚 Merged dictionary: {len(merged)} entries (IDIEZ priority)")

    return idiez_dict, karttunen_dict, merged


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF, page by page."""
    reader = PdfReader(pdf_path)
    pages_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'  +', ' ', text)
        pages_text.append(text.strip())
    return pages_text


def translate_text(text, dictionary, known_words=None):
    """Translate English text to Nahuatl.
    
    Lookup order per word:
      1. User translations (known_words from unknown_words.json)
      2. IDIEZ dictionary (Modern Huasteca)
      3. Karttunen dictionary (Classical Nahuatl)
      4. Verb conjugation (detect tense → conjugate)
      5. Synonyms
      6. Grammar rules (function words, phrases, numbers, body parts)
      7. EN → ES → NAH fallback
      8. Unknown → saved to unknown_words.json
    
    Args:
        text: English text
        dictionary: merged English→Nahuatl dictionary (IDIEZ priority)
        known_words: dict of {word: nahuatl} from user translations
    
    Returns:
        (translated_text, unknown_words_set, context_map)
    """
    if known_words:
        # User translations have HIGHEST priority — override everything
        dictionary = {**dictionary, **known_words}

    translated, unknown = translate_with_grammar(text, dictionary)

    # Mark verbs that failed conjugation/synonym lookup with "++"
    # This helps identify which verbs need dictionary entries
    from grammar_rules import find_verb_info
    from synonyms import SYNONYMS
    
    marked_unknown = set()
    for word in unknown:
        # Check if it's a verb form
        infinitive, tense = find_verb_info(word)
        if infinitive:
            # Check if infinitive or any synonym is in dictionary
            if infinitive not in dictionary:
                has_synonym = False
                if infinitive in SYNONYMS:
                    for syn in SYNONYMS[infinitive]:
                        if syn in dictionary:
                            has_synonym = True
                            break
                if not has_synonym:
                    marked_unknown.add(word + "++")
                else:
                    marked_unknown.add(word)
            else:
                marked_unknown.add(word)
        else:
            marked_unknown.add(word)

    # Clean up Nahuatl text: remove hyphens, lowercase caps, sentence case
    translated = clean_nahuatl_text(translated)

    # Build context map for unknown words
    context_map = {}
    sentences = re.split(r'[.!?]+\s*', text)
    for word in marked_unknown:
        base_word = word.replace("++", "")
        contexts = []
        for sent in sentences:
            if re.search(r'\b' + re.escape(base_word) + r'\b', sent, re.IGNORECASE):
                contexts.append(sent.strip())
        if contexts:
            context_map[word] = contexts

    return translated, marked_unknown, context_map


def escape_html(text):
    """Escape HTML entities for safe use in reportlab Paragraph."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    return text


def create_side_by_side_pdf(pages_english, pages_nahuatl, unknown_words, output_path):
    """Generate a side-by-side PDF with English left, Nahuatl right."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
        fontSize=18, textColor=HexColor('#1a1a2e'), spaceAfter=8,
        alignment=TA_CENTER, fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
        fontSize=10, textColor=HexColor('#666666'), spaceAfter=12,
        alignment=TA_CENTER, fontName='Helvetica-Oblique')
    col_header_style = ParagraphStyle('ColHeader', parent=styles['Normal'],
        fontSize=10, textColor=HexColor('#16213e'), fontName='Helvetica-Bold',
        alignment=TA_CENTER)
    english_style = ParagraphStyle('EnglishBody', parent=styles['Normal'],
        fontSize=7, leading=9, fontName='Helvetica-Oblique', alignment=TA_LEFT,
        textColor=HexColor('#444444'), spaceAfter=1)
    nahuatl_style = ParagraphStyle('NahuatlBody', parent=styles['Normal'],
        fontSize=7, leading=9, fontName='Helvetica', alignment=TA_LEFT, spaceAfter=1)
    page_sep_style = ParagraphStyle('PageSep', parent=styles['Normal'],
        fontSize=8, textColor=HexColor('#aaaaaa'), alignment=TA_CENTER,
        fontName='Helvetica-Oblique', spaceBefore=6, spaceAfter=6)
    unknown_header_style = ParagraphStyle('UnknownHeader', parent=styles['Heading1'],
        fontSize=14, textColor=HexColor('#c0392b'), fontName='Helvetica-Bold',
        spaceBefore=20, spaceAfter=10)
    unknown_word_style = ParagraphStyle('UnknownWord', parent=styles['Normal'],
        fontSize=9, leading=13, fontName='Helvetica', spaceAfter=1)

    doc = SimpleDocTemplate(output_path, pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)

    story = []

    # Title page
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph("English \u2192 Nahuatl Translation", title_style))
    story.append(Paragraph("Modern Huasteca Variant \u2014 Classical Orthography", subtitle_style))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(f"Pages translated: {len(pages_english)}", subtitle_style))
    story.append(PageBreak())

    # Side-by-side content
    for i, (eng_text, nah_text) in enumerate(zip(pages_english, pages_nahuatl)):
        header_data = [[
            Paragraph("English", col_header_style),
            Paragraph("Nahuatl", col_header_style)
        ]]
        header_table = Table(header_data, colWidths=[COL_WIDTH, COL_WIDTH])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), HexColor('#e8e8e8')),
            ('BACKGROUND', (1, 0), (1, 0), HexColor('#d5e8d4')),
            ('BOX', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('LINEBELOW', (0, 0), (-1, 0), 1, HexColor('#999999')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(header_table)

        # Split both English and Nahuatl into sentences and pair them 1:1
        eng_sentences = re.split(r'(?<=[.!?])\s+', eng_text.strip()) if eng_text.strip() else ['']
        nah_sentences = re.split(r'(?<=[.!?])\s+', nah_text.strip()) if nah_text.strip() else ['']

        # Clean up sentences
        eng_sentences = [s.strip() for s in eng_sentences if s.strip()]
        nah_sentences = [s.strip() for s in nah_sentences if s.strip()]

        # Pair sentences: each English sentence with its Nahuatl translation
        max_sentences = max(len(eng_sentences), len(nah_sentences))

        for j in range(max_sentences):
            eng_sent = eng_sentences[j] if j < len(eng_sentences) else ''
            nah_sent = nah_sentences[j] if j < len(nah_sentences) else ''

            if not eng_sent and not nah_sent:
                continue

            eng_p = Paragraph(escape_html(eng_sent), english_style) if eng_sent else Spacer(1, 8)
            nah_p = Paragraph(escape_html(nah_sent), nahuatl_style) if nah_sent else Spacer(1, 8)

            row_table = Table([[eng_p, nah_p]], colWidths=[COL_WIDTH, COL_WIDTH])
            row_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LINEBELOW', (0, 0), (-1, -1), 0.25, HexColor('#eeeeee')),
            ]))
            story.append(row_table)

        if i < len(pages_english) - 1:
            story.append(Spacer(1, 8))
            story.append(Paragraph(f"\u2014 Page {i + 2} \u2014", page_sep_style))
            story.append(Spacer(1, 4))

    # Unknown words
    if unknown_words:
        story.append(PageBreak())
        story.append(Paragraph("Words not found in dictionary", unknown_header_style))
        sorted_unknown = sorted(unknown_words)
        cols = 3
        col_items = [[] for _ in range(cols)]
        for idx, word in enumerate(sorted_unknown):
            col_items[idx % cols].append(word)

        max_col_len = max(len(c) for c in col_items) if col_items else 0
        table_data = []
        for j in range(max_col_len):
            row = []
            for c in range(cols):
                if j < len(col_items[c]):
                    row.append(Paragraph(escape_html(col_items[c][j]), unknown_word_style))
                else:
                    row.append(Spacer(1, 12))
            table_data.append(row)

        col_w_unknown = (PAGE_WIDTH - 2 * MARGIN) / cols
        table = Table(table_data, colWidths=[col_w_unknown] * cols)
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        story.append(table)

        story.append(Spacer(1, 16))
        count_style = ParagraphStyle('Count', parent=subtitle_style, alignment=TA_LEFT)
        story.append(Paragraph(f"Total unknown words: {len(sorted_unknown)}", count_style))

    doc.build(story)
    print(f"\nPDF saved to: {output_path}")

    # Copy to Android Downloads folder
    downloads_dir = "/storage/emulated/0/Download"
    if os.path.isdir(downloads_dir):
        dest_path = os.path.join(downloads_dir, os.path.basename(output_path))
        shutil.copy2(output_path, dest_path)
        print(f"PDF copied to: {dest_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Translate an English PDF to Nahuatl (Huasteca) side-by-side PDF"
    )
    parser.add_argument("input_pdf", nargs="?", help="Path to the English PDF file")
    parser.add_argument("-o", "--output", help="Output PDF path (default: output/translated.pdf)")
    parser.add_argument("--dict", help="Dictionary JSON path (default: dictionary.json)")
    args = parser.parse_args()

    # Prompt for filename if not provided via command line
    if args.input_pdf:
        input_filename = args.input_pdf
    else:
        input_filename = input("Enter the PDF filename (must be in the script directory): ").strip()

    # Ensure the file is in SCRIPT_DIR and is a PDF
    if not input_filename.lower().endswith('.pdf'):
        print("ERROR: File must be a PDF (.pdf extension required)")
        sys.exit(1)

    input_pdf = os.path.join(SCRIPT_DIR, input_filename)
    if not os.path.exists(input_pdf):
        print(f"ERROR: File not found: {input_pdf}")
        print(f"Make sure '{input_filename}' is in: {SCRIPT_DIR}")
        sys.exit(1)

    dict_path = os.path.abspath(args.dict) if args.dict else DEFAULT_DICT

    # Determine output path
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        # Prompt user for output filename
        output_filename = input("Enter output filename (default: translated.pdf): ").strip()
        if not output_filename:
            output_filename = "translated.pdf"
        if not output_filename.lower().endswith('.pdf'):
            output_filename += '.pdf'
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        output_path = os.path.abspath(output_path)

    print("=" * 50)
    print("English -> Nahuatl Translator")
    print("=" * 50)

    # Load separate dictionaries (IDIEZ priority, Karttunen fallback)
    idiez_dict, karttunen_dict, dictionary = load_dictionaries()

    # If user specified a custom dict, use that instead
    if args.dict:
        dict_path = os.path.abspath(args.dict)
        dictionary = load_dictionary(dict_path)

    print(f"\nExtracting text from: {input_pdf}")
    pages_english = extract_text_from_pdf(input_pdf)
    print(f"Extracted {len(pages_english)} pages")

    # Load known words from previous sessions
    known_words = load_known_words()
    if known_words:
        print(f"📖 Loaded {len(known_words)} known word translations")

    # Test translation quality
    print("\n🧪 Testing translation quality...")
    score, results = test_translation_quality(dictionary, known_words)
    print(f"   Quality score: {score:.1f}%")
    
    # Show failed translations
    failed = [r for r in results if not r['correct']]
    if failed:
        print(f"   Failed: {len(failed)}/{len(results)} sentences")
        print("\n   Sample failures:")
        for r in failed[:5]:
            print(f"   EN: {r['english']}")
            print(f"   Expected: {r['expected']}")
            print(f"   Got: {r['got']}")
            print()

    print("\nTranslating...")
    pages_nahuatl = []
    all_unknown = set()
    all_context = {}

    for i, eng_text in enumerate(pages_english):
        nah_text, unknown, context = translate_text(eng_text, dictionary, known_words)
        pages_nahuatl.append(nah_text)
        all_unknown.update(unknown)

        # Merge context maps
        for word, contexts in context.items():
            if word not in all_context:
                all_context[word] = []
            all_context[word].extend(contexts)

    print(f"Translated {len(pages_nahuatl)} pages")

    # Filter out proper names from unknown words
    all_unknown_filtered, _ = filter_unknown_words(all_unknown, all_context)
    print(f"Unknown words found: {len(all_unknown_filtered)} (filtered out {len(all_unknown) - len(all_unknown_filtered)} proper names)")

    # Save unknown words for review
    if all_unknown_filtered:
        save_unknown_words(all_unknown_filtered, all_context)
        print_unknown_summary()

    print("\nGenerating side-by-side PDF...")
    create_side_by_side_pdf(pages_english, pages_nahuatl, all_unknown_filtered, output_path)
    print("\nDone!")


if __name__ == "__main__":
    main()
