NAHUATL TRANSLATOR 2 — APP DESIGN SCHEMATIC
============================================
Last updated: 2026-06-07
Approach: Claude API few-shot translation with self-improving rule base
Target dialect: Modern Huasteca Nahuatl (IDIEZ)


A. DICTIONARY BUILD PIPELINE   (one-time; dictionaries/)
=========================================================

   [IDIEZ PDF source]
        |
        v  parser.py -> normalizer.py -> enricher.py -> inverter.py
        |  (scripts archived in OUT FILES/ — pipeline already complete)
        v
  enriched_idiez.json    NAH headwords + ES definitions (6,241 entries)
        |                used as vocabulary hints injected per sentence
  dictionary_idiez.json  EN->NAH lookup (6,345 entries)
        |                primary reference dictionary
        v
  merger.py  (PENDING — run once to merge IDIEZ + Karttunen)
        |
        v
  dictionary.json  (not yet generated)

  Note: Karttunen = classical Nahuatl (archived). IDIEZ = Huasteca, primary.


B. DATA COLLECTION PIPELINE   (per source document)
=====================================================

  [Source PDF on Google Drive]
        |
        v  transcribe_*_to_sheet.py  (scripts archived in OUT FILES/)
        |
        v
  Google Sheet (one per book)
  +-------+-------------------+------------------+----------+---------+
  | Col A | Col B             | Col C            | Col D    | Col E   |
  | Label | Nahuatlahtolli    | Coyotlahtolli    | Notes    | Claude  |
  |       | (Nahuatl source)  | (gold Spanish)   | (manual) | draft   |
  +-------+-------------------+------------------+----------+---------+

  Current sheets:
    Crispin  (12ebNz0hxWwoXEpDcXITuRN1q9Q2dlVXwiaJd2YQWUP4)
      4,037 rows; col B complete; col C done rows 4-488
    Eduardo  (1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw)
      1,512 rows; col B complete; col C empty


C. TRANSLATION + LEARNING LOOP   (translate_and_learn.py)
==========================================================

  On each run:

  1. LOAD
       translation_rules.json  <- shared rules (human-verified first)
       enriched_idiez.json     <- vocabulary hints
       top-BLEU rows from col F  <- dynamic few-shot examples

  2. FOR EACH ROW:

       Col B (Nahuatl)
            |
            v  Claude API (claude-haiku-4-5)
            |  system prompt: base instructions + rules from translation_rules.json
            |  few-shot: top-BLEU pairs from col F
            |  per-sentence: IDIEZ vocabulary hints from enriched_idiez.json
            v
       Col E  Claude draft translation (Spanish)

       If col C (gold) exists:
            |
            v  BLEU(col C, col E)
            v
       Col F  BLEU score  (0-1; higher = closer to human gold)

            |
            v  Claude API (single call, JSON output)
            v
       Col G  Tlatocopa: key difference between E and C
       Col H  Tlahtol Auto: generalised rule derived from the error

       Col I  Tlahtol Human: LEFT EMPTY for human correction in sheet

  3. Config flags:
       PROCESS_START / PROCESS_END  — row range
       OVERWRITE = False            — skips already-filled rows (safe resume)


D. RULE EXTRACTION + SHARING   (extract_rules.py)
==================================================

  Run after each translate_and_learn.py pass:

  Google Sheet cols H + I  (all source documents)
        |
        v  extract_rules.py
        |  deduplicates, prefers col I (human) over col H (auto)
        |  sorts: human-verified first, then by BLEU descending
        v
  translation_rules.json
        |
        +---> read by translate_and_learn.py on every run, any document
              top MAX_RULES (10) injected into Claude system prompt

  Rule evidence grows across documents:
    Crispin rules -> translation_rules.json -> applied to Eduardo
    Eduardo rules -> translation_rules.json -> applied to Crispin + future books


E. ML TRAINING PATH   (future)
================================

  Step 1 — NOW (Claude API few-shot, no training required)
    translate_and_learn.py  ->  col E drafts  ->  human corrects to col C
    translation_rules.json improves Claude quality run-over-run

  Step 2 — MEDIUM TERM (NLLB-200 fine-tune)
    Training corpus:
      col B (Nahuatl)  +  col C (corrected Spanish)  ->  NAH<->ES pairs
      parallel_sentences.json  ->  1,693 EN<->NAH pairs (ready now)
      BLEU col F used as quality filter (exclude low-scoring rows)
    Model: facebook/nllb-200-distilled-600M  (supports nah_Latn natively)
    Bottleneck: volume of corrected col C rows

    Current training data available:
      Crispin rows 4-488:  ~485 NAH<->ES pairs (gold)
      parallel_sentences.json:  1,693 EN<->NAH pairs

  Step 3 — LONG TERM (morphological analyzer)
    Nahuatl is agglutinative: nitlatequitiz = ni + tla + tequiti + z
    Pre-processing step: decompose word forms before dictionary lookup
    Position: between vocabulary hint lookup and Claude API call


F. DATA FILES REFERENCE
========================

  Active:
    translate_and_learn.py       main translation + learning loop
    extract_rules.py             harvest rules from sheets -> JSON
    translation_rules.json       shared rule base (all documents)
    dictionaries/
      enriched_idiez.json        vocabulary hints for Claude (6,241 entries)
      dictionary_idiez.json      EN->NAH dictionary (6,345 entries)
      merger.py                  pending: merge IDIEZ + Karttunen
    parallel_sentences.json      1,693 EN<->NAH pairs (training data)
    inspect_docs.py              Drive/Sheet preview utility
    count_words_colB.py          word count utility

  Archived (OUT FILES/):
    grammar_rules.py / translator.py / verb_conjugator.py
      -> old rule-based EN->NAH engine (superseded by Claude API)
    data/
      -> lookup tables for old rule-based engine
    dictionaries/parser, normalizer, enricher, inverter, sandbox
      -> one-time IDIEZ build pipeline (already run)
    output/*.pdf
      -> bilingual PDF outputs from old engine


G. KNOWN GAPS
==============

  1. Morphological analyzer (see Step 3 above)
       nitlatequitiz won't match 'tlatequiti' in enriched_idiez.json
       Biggest source of missed vocabulary hints

  2. col C incomplete for rows 489-4037 (Crispin) and all of Eduardo
       Each corrected row = one NAH<->ES training pair for NLLB-200
       Human correction pass is the highest-leverage current task

  3. merger.py not yet run
       dictionary.json (master EN->NAH) not yet generated
       Low priority under Claude API approach

  4. translation_rules.json has 0 human-verified rules (as of 2026-06-07)
       All 479 rules are auto-derived from col H
       First priority: review col H in Crispin sheet, add corrections to col I,
       then re-run extract_rules.py
