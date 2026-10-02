NAHUATL TRANSLATOR 2 — APP DESIGN SCHEMATIC
============================================


A. OFFLINE — DICTIONARY BUILD PIPELINE   (run once; dictionaries/)
====================================================================

   [IDIEZ PDF]               [Karttunen PDF]
        |  (PRIMARY)               |  (secondary / classical)
        v                          v
    parser.py               parser.py
        |                          |
        v                          v
  raw_idiez.json          raw_karttunen.json
        |                          |
        v                          v
  normalizer.py           normalizer.py
   clean artifacts,        clean artifacts,
   split ES/EN defs        split ES/EN defs
        |                          |
        v                          v
  normalized_idiez.json   normalized_karttunen.json
        |                          |
        v                          v
  enricher.py (spaCy)     enricher.py (spaCy)
   extract lemmas/roots    extract lemmas/roots
        |                          |
        v                          v
  enriched_idiez.json     enriched_karttunen.json
        |                          |
        v                          v
  inverter.py             inverter.py
   flip NAH->EN to          flip NAH->EN to
   EN->NAH + scoring         EN->NAH + scoring
        |                          |
        v                          v
  dictionary_idiez.json   dictionary_karttunen.json
    (6,345 entries)          (secondary)
        |                          |
        +----------+---------------+
                   |
                   v
               merger.py
                   |
                   v
            dictionary.json
          (master EN->NAH, IDIEZ priority)


B. RUNTIME — TRANSLATION PIPELINE   (translator.py)
=====================================================

  [input.pdf]
       |
       v
  translator.py  (orchestrator)
  +------------------------------------------------------------------+
  |                                                                  |
  |  1. load_dictionaries()                                          |
  |       dictionary_idiez.json       <- priority                    |
  |       dictionary_karttunen.json   <- fallback                    |
  |       merged into one dict (IDIEZ wins on conflict)              |
  |                                                                  |
  |  2. extract_text_from_pdf()  [pypdf]                             |
  |       -> pages_english[]                                         |
  |                                                                  |
  |  3. load_known_words()  [unknown_words.json]                     |
  |       user-supplied translations — HIGHEST priority              |
  |                                                                  |
  |  4. test_translation_quality()  [parallel_sentences.json]        |
  |       1,693 EN<->NAH pairs -> quality score printed at startup   |
  |                                                                  |
  |  5. translate_text()  <- per page                                |
  |       |                                                          |
  |       +-- grammar_rules.translate_with_grammar()                 |
  |                                                                  |
  |             WORD LOOKUP ORDER (per token):                       |
  |             1. known_words  (user edits, highest priority)       |
  |             2. dictionary   (IDIEZ -> Karttunen merged)          |
  |             3. verb_conjugator.py                                |
  |                  detect EN tense -> infinitive                   |
  |                  -> lookup root in dict                          |
  |                  -> apply Nahuatl subject prefixes               |
  |                     (ni-, ti-, -, ti-...pl, an-, -)              |
  |                     + tense suffix                               |
  |             4. synonyms.py  (SYNONYMS map)                       |
  |             5. data/function_words.json                          |
  |                  pronouns, prepositions, articles, conjunctions  |
  |             6. data/common_phrases.json                          |
  |                  multi-word EN -> NAH patterns                   |
  |             7. data/direct_en_nah.json                           |
  |                  hardcoded direct fallback table                 |
  |             8. data/en_to_es.json -> Spanish -> NAH              |
  |                  intermediate pivot via Spanish                  |
  |             9. -> UNKNOWN  (marked with ++ if verb)              |
  |                                                                  |
  |       +-- clean_nahuatl_text()                                   |
  |             strip diacritics, fix ALL-CAPS, sentence-case        |
  |                                                                  |
  |       -> pages_nahuatl[]  +  unknown_words{}                     |
  |                                                                  |
  |  6. create_side_by_side_pdf()  [reportlab]                       |
  |       title page                                                 |
  |       English (left col, italic) | Nahuatl (right col)           |
  |       sentence-paired rows per page                              |
  |       unknown words appendix (3-column list)                     |
  |       -> output/translated.pdf                                   |
  |       -> copy to /storage/emulated/0/Download/                   |
  |                                                                  |
  |  7. save_unknown_words()                                         |
  |       -> unknown_words.json  (for user review)                   |
  +------------------------------------------------------------------+


C. FEEDBACK LOOP — UNKNOWN WORDS
==================================

  run translator
       |
       v
  unknown_words.json  <-- auto-populated (267 words pending)
       |
       |  user manually adds Nahuatl translations
       |
       +-----------> next run: loaded as step 1 (highest priority)


D. DATA FILES QUICK REFERENCE
================================

  data/
    function_words.json    pronouns, prepositions, articles, conjunctions
    irregular_verbs.json   English irregular forms -> root (went->go, etc.)
    common_phrases.json    multi-word EN->NAH phrase patterns
    direct_en_nah.json     direct word-level fallback table
    en_to_es.json          EN->ES pivot for Spanish intermediate path

  dictionaries/
    raw_idiez.json              step 1 output  (6,241 entries)
    normalized_idiez.json       step 2 output
    enriched_idiez.json         step 3 output
    dictionary_idiez.json       step 4 output  (6,345 EN->NAH)  <- main
    dictionary_karttunen.json   step 4 output  (classical, fallback)
    dictionary.json             step 5 output  (master, IDIEZ priority)

  root/
    parallel_sentences.json     1,693 EN<->NAH pairs (quality testing)
    unknown_words.json          267 words pending user translation
    synonyms.py                 inline SYNONYMS dict


E. KNOWN GAP  (see IMPROVEMENTS.md)
======================================

  Missing: morphological analyzer

    Current:  word  ->  dict lookup
              (misses nitlatequitiz, nimitzillia, etc.)

    Needed:   word  ->  decompose prefixes / root / suffixes
                    ->  lookup root in dictionary

    Impact:   biggest single source of UNKNOWN words;
              Nahuatl is agglutinative — complex forms are
              built from roots + subject/object/tense affixes.

    Position if added:  between steps 2 and 3 in lookup order.
