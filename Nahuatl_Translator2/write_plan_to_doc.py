import json
from google.oauth2.credentials import Credentials as OAuthCreds
from google.oauth2.service_account import Credentials as SACredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SA_KEY     = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
TOKEN_PATH = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json'
DOC_ID     = '15wEbCHRmjW09T5KgMLhHiGjyp4YcCRrNpBunnAiQURs'
SA_EMAIL   = 'ws-financial-analysis@qwen-project-492821.iam.gserviceaccount.com'

SA_SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive',
]

sa_creds = SACredentials.from_service_account_file(SA_KEY, scopes=SA_SCOPES)
docs_service = build('docs', 'v1', credentials=sa_creds)

# ── create doc if needed ───────────────────────────────────────────────────────

if DOC_ID is None:
    with open(TOKEN_PATH) as f:
        tok = json.load(f)
    oauth_creds = OAuthCreds(
        token=tok['token'], refresh_token=tok['refresh_token'],
        token_uri=tok['token_uri'], client_id=tok['client_id'],
        client_secret=tok['client_secret'], scopes=tok['scopes'],
    )
    if oauth_creds.expired and oauth_creds.refresh_token:
        oauth_creds.refresh(Request())
    user_drive = build('drive', 'v3', credentials=oauth_creds)
    created = user_drive.files().create(
        body={'name': 'Nahuatl Translator 2 — Project Plan',
              'mimeType': 'application/vnd.google-apps.document'},
        fields='id'
    ).execute()
    DOC_ID = created['id']
    user_drive.permissions().create(
        fileId=DOC_ID,
        body={'type': 'user', 'role': 'writer', 'emailAddress': SA_EMAIL},
    ).execute()
    print(f'Created: https://docs.google.com/document/d/{DOC_ID}/edit')
else:
    print(f'Updating: https://docs.google.com/document/d/{DOC_ID}/edit')

# ── section registry ───────────────────────────────────────────────────────────

TOC_HEADER = 'Table of Contents'

SECTIONS = [
    'WHAT IS THIS PROJECT?',
    'WHY BUILD THIS?',
    'SYSTEM ARCHITECTURE',
    'KEY DATA SOURCES',
    'TOOLS & PACKAGES — WITH RATIONALE',
    'BUILD SEQUENCE',
    'CURRENT STATE (as of 2026-09-21)',
    'KEY CONSTRAINTS & DECISIONS',
    'OPEN QUESTIONS / NEXT STEPS',
]

HEADING_3_PREFIXES = (
    'Workstream A',
    'Workstream B',
    'Workstream C',
    'Workstream D',
    'Workstream E',
    'Step A',
    'Step B',
    'Step C',
    'Step D',
    'Step E',
)

# ── document content ───────────────────────────────────────────────────────────
# TOC section comes first (after title). Each section name here becomes a link.
# The actual section headings below receive HEADING_2 style + pageBreakBefore.

CONTENT = """\
Nahuatl Translator 2 — English to Huasteca Nahuatl
Project Plan · 2026-09-21

Table of Contents

WHAT IS THIS PROJECT?
WHY BUILD THIS?
SYSTEM ARCHITECTURE
KEY DATA SOURCES
TOOLS & PACKAGES — WITH RATIONALE
BUILD SEQUENCE
CURRENT STATE (as of 2026-09-21)
KEY CONSTRAINTS & DECISIONS
OPEN QUESTIONS / NEXT STEPS

WHAT IS THIS PROJECT?

Nahuatl Translator 2 is a machine translation system that converts English text into Modern Huasteca Nahuatl (IDIEZ dialect). It is built on a pipeline that combines a large bilingual dictionary, translation rules derived from real Nahuatl literature, and a fine-tuned neural machine translation model (NLLB-200). The output is intended for practical use with the Chicontepec variety of Huasteca Nahuatl, as documented by IDIEZ (Instituto de Docencia e Investigación Etnológica de Zacatecas).

The name "Macehualtlahtol" — the parent folder — means "the language of the common people" in Nahuatl, reflecting the project's focus on living spoken Nahuatl rather than Classical or literary registers.

WHY BUILD THIS?

Huasteca Nahuatl has almost no machine translation resources. No commercial or open-source model is trained on it. The NLLB-200 model (Meta, 2022) nominally includes Nahuatl (nah_Latn) but was trained on nearly zero Huasteca Nahuatl data, producing poor output. This project builds the missing training corpus from primary sources and uses it to fine-tune NLLB-200, making it meaningfully better on Huasteca Nahuatl text.

Beyond the model, the project serves as a structured platform for reading and analyzing Nahuatl literature: two complete Nahuatl texts (Crispín Martínez Rosas 2021, Eduardo de la Cruz Cruz 2017) are transcribed and aligned with Spanish translations in Google Sheets, creating a growing parallel corpus for both training and research.

SYSTEM ARCHITECTURE

The system has two layers:

Layer 1 — Translation pipeline (Claude API, rule-based):
  translate_and_learn.py
    • morphology.py — decomposes agglutinative Nahuatl verb forms
    • Hint tier 1: nah_es_glossary.json — ~8 human-verified NAH→ES terms (highest priority)
    • Hint tier 2: dictionary_idiez.json — 6,345 EN→NAH / IDIEZ entries
    • Hint tier 3: normalized_sullivan.json — 9,782 Sullivan 2016 NAH→NAH entries
    • translation_rules.json (5,602 rules) — auto + human-verified grammar rules
    • Claude API (claude-haiku-4-5) — few-shot NAH→ES translation

Layer 2 — NLLB-200 fine-tuned model (GPU, on laptop):
  finetune_nllb.py
    • Base model: facebook/nllb-200-distilled-600M
    • Training corpus: nah_es_pairs.json (4,260 clean pairs)
    • Output: models/nllb-nah-es-final/

  eval_nllb_d5.py
    • Evaluates fine-tuned model vs Claude API baseline; writes BLEU scores to sheets

Device split:
  Android Tablet (ARM / Termux) ←─── Tailscale VPN ───→ Windows Laptop (x86_64 / WSL2)
  Primary dev environment                                  NVIDIA RTX 3060 (CUDA)
  translate_and_learn.py                                   finetune_nllb.py
  Google Sheets access                                     eval_nllb_d5.py

  Laptop SSH: ssh wslinux@100.68.100.23 (Tailscale: tcp-partners.com)
  Backup SSH: ssh ws@100.99.213.23 (Windows OpenSSH)

KEY DATA SOURCES

1. IDIEZ Dictionary (EN→NAH, 6,345 entries)
   File: dictionaries/dictionary_idiez.json
   Built by a 4-step pipeline: parse → normalize → enrich (spaCy) → invert
   Primary dictionary for translation hints; Chicontepec Huasteca Nahuatl dialect

2. Sullivan 2016 — Tlahtolxitlauhcayotl Chicontepec (NAH→NAH, 9,782 entries)
   File: dictionaries/normalized_sullivan.json
   Monolingual Nahuatl dictionary; same dialect as IDIEZ; supplementary context layer
   Es fields currently empty (enrichment planned via NLLB or Claude API)

3. Crispin_Carlos Sheet — Tlallamiquiliztli inelhuayo (Crispín Martínez Rosas, 2021)
   Spreadsheet ID: 1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg, worksheet: Crispin
   207-page Huasteca Nahuatl prose fiction; 4,037 rows
   Col B: Nahuatl (complete) | Col C: Spanish gold (complete) | Col E: Claude draft | Col H: auto rules
   Provides ~4,030 NAH↔ES parallel sentence pairs for training

4. Eduardo Sheet — Cenyactoc cintli tonacayo (Eduardo de la Cruz Cruz, 2017)
   Spreadsheet ID: 1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw, worksheet: Eduardo
   78-page Nahuatl text; 301 rows (288 with content)
   Col B: Nahuatl (complete) | Col C: Spanish gold (complete) | Col E: Claude draft
   Provides ~282 NAH↔ES parallel sentence pairs for training

5. parallel_sentences.json (NAH↔EN, 282 pairs)
   Local file; IDIEZ-origin English-Nahuatl sentence pairs

TOOLS & PACKAGES — WITH RATIONALE

1. Claude API (claude-haiku-4-5)
   What: Anthropic's fast, cheap large language model.
   Why needed: Nahuatl has no ready-made translation model. Claude is used as a few-shot translator: given a system prompt with translation rules, dictionary hints, and 5–10 example NAH→ES sentence pairs, it produces draft Spanish translations (col E) for each Nahuatl sentence. It also derives a grammar rule from each high-error pair (cols G and H).
   Why haiku-4-5: Cost. Processing 4,037 rows with haiku costs ~$0.60–0.80 total.
   Used in: translate_and_learn.py

2. NLLB-200-distilled-600M (facebook/nllb-200-distilled-600M)
   What: Meta's multilingual seq2seq translation model, 600M parameters, 200 language pairs.
   Why needed: Claude API is expensive at inference time. A fine-tuned NLLB model runs locally for free. Fine-tuning teaches NLLB the NAH→ES mapping using the 4,260 parallel pairs built from the Crispin + Eduardo sheets.
   Why NLLB: It includes nah_Latn as a language code and was designed for low-resource pairs.
   Status (D5): Avg BLEU 0.3492 on 4,260 pairs. Best on full prose; weakest on nominalizations (-liztli), complex agglutinative verbs, and proper names.

3. HuggingFace Transformers + Datasets
   What: Open-source NLP library; model loading, tokenization, training loop.
   Why needed: NLLB-200 is a HuggingFace model. Transformers provides the tokenizer, model class, and trainer. Datasets handles train/val split and Arrow-format on-disk storage.
   Installed: Laptop WSL2, ~/nllb-env, via pip

4. PyTorch (CUDA build)
   What: Deep learning framework.
   Why needed: NLLB-200 is a PyTorch model. CUDA build enables GPU acceleration on the laptop's RTX 3060. CPU-only training takes ~8–20 hours; GPU reduces this to ~30–60 minutes.
   Installed: Laptop WSL2, ~/nllb-env, pip install torch --index-url https://download.pytorch.org/whl/cu121

5. gspread + google-auth
   What: Python client for Google Sheets API.
   Why needed: All training data lives in Google Sheets. Scripts read col B+C for training pairs, write Claude translations to col E, write NLLB translations to col J, and write BLEU scores to cols F and K.
   Auth: Service account key (ws-financial-analysis@qwen-project-492821.iam.gserviceaccount.com)

6. morphology.py (custom module)
   What: Nahuatl morphological decomposer.
   Why needed: Nahuatl is highly agglutinative. A word like nitlatequitiz (I will work) contains 5 morphemes: ni + tla + tequiti + z. morphology.py splits surface forms into root and affixes for dictionary lookup.
   Status: Implemented and wired into translate_and_learn.py (E1+E2 complete).

7. sacrebleu
   What: Standard BLEU score implementation for MT evaluation.
   Why needed: Used to rank rows by quality, identify worst-performing pairs for human review, compare NLLB vs Claude, and track improvement across training rounds.
   Installed: Laptop WSL2, ~/nllb-env, via pip

8. tmux (on laptop WSL2)
   What: Terminal multiplexer — keeps processes running after SSH disconnect.
   Why needed: NLLB fine-tuning takes 30–60 minutes on GPU. tmux keeps the training session alive across SSH disconnects. Used for all long-running laptop processes.

BUILD SEQUENCE

Workstream A — Rule Quality (Human)

Step A1 — Human: review Crispin_Carlos Deltas tab [PENDING]
  Open sheet → "Deltas" tab → filter col H = real_error
  Fill: Col I (Error Type), Col J (Rule/Note), Col K (Human Correction), Col L → done
  2,767 real_error rows ready for review; 0 human-verified rules so far — biggest quality gap

Step A2 — Run extract_rules.py [Depends on A1]
  Harvests col I corrections into translation_rules.json

Workstream B — Crispin Training Data

Step B3 — Translate rows 489–1,821 [DONE]
  All 1,817 gold rows in Crispin sheet fully translated (cols E, F, G, H complete)

Step B5 — Run extract_rules.py on rows 489–1,821 [DONE]
  5,602 rules harvested into translation_rules.json

Workstream C — Eduardo Sheet [DONE]
  All 282 Eduardo rows translated (col E complete); wired into training corpus

Workstream D — NLLB-200 Fine-Tune

Step D4 — Fine-tune NLLB-200 on 4,260 pairs [DONE]
  Model saved at: ~/WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator/models/nllb-nah-es-final/
  Training: 10 epochs, fp16, RTX 3060, ~60 min

Step D5 — Evaluate fine-tuned model [DONE]
  Avg BLEU: 0.3492 (4,260 pairs, skip-excluded)
  NLLB translations written to col J; BLEU to col K in both sheets
  Error breakdown: 2,767 real_error | 743 diacritics | 111 proper names | 358 headings

Step D6 — Re-fine-tune on human-corrected pairs [PENDING — depends on A1]
  Build apply_corrections.py → re-run finetune_nllb.py with augmented corpus

Workstream E — Morphological Analyzer

Step E1 — Build morphology.py [DONE]
  Decomposes Nahuatl surface forms → root + affixes; confirmed on 10 test words

Step E2 — Wire into translate_and_learn.py [DONE]
  dict_hints() uses morphological decomposition for IDIEZ and Sullivan lookups

CURRENT STATE (as of 2026-09-21)

Training corpus:
  nah_es_pairs.json: 4,260 clean pairs (Crispin_Carlos 4,030 + Eduardo 282; 52 SKIP rows removed)
  nah_en_pairs.json: 282 pairs (parallel_sentences.json)
  Total: 4,542 pairs

Fine-tuned model (D4 — DONE):
  Location: laptop ~/WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator/models/nllb-nah-es-final/
  D5 avg BLEU: 0.3492

Translation rules: 5,602 (all auto-derived, 0 human-verified — biggest quality gap)

Deltas tab: populated in both sheets; 2,767 real_error rows await human review

Active scripts (tablet — Termux):
  translate_and_learn.py, extract_rules.py, export_training_data.py, morphology.py,
  generate_deltas.py, write_plan_to_doc.py

Scripts on laptop (WSL2, ~/nllb-env):
  finetune_nllb.py, prep_training_data.py, eval_nllb_d5.py

KEY CONSTRAINTS & DECISIONS

Termux Python (ARM) vs laptop Python (x86_64)
  All Google Sheets / Claude API scripts use Termux Python on the Android tablet (/data/data/com.termux/files/usr/bin/python3). Heavy ML workloads (NLLB fine-tune, eval) run on the laptop WSL2 via SSH. Scripts use platform-agnostic path resolution.

nah_Latn language code
  NLLB-200's nah_Latn code covers Nahuatl in Latin script but was trained on nearly no Huasteca Nahuatl data. Fine-tuning on the 4,260 project pairs teaches the model the dialect from scratch. This is expected and intended — the model improves with each training round.

No human-verified translation rules (BIGGEST QUALITY GAP)
  The 5,602 rules in translation_rules.json are all auto-derived by Claude from high-error pairs. They are plausible but unchecked. Correcting even 100 rules in the Deltas tab would meaningfully improve translation quality on the next D6 fine-tune.

Classical Nahuatl contamination
  Rows 173–239 in Crispin_Carlos contain Classical Nahuatl (Sahagún 1579 maize section) — not Huasteca Nahuatl. Flagged as SKIP and removed from nah_es_pairs.json. The Karttunen dictionary (Classical NAH→EN) is kept as a tertiary fallback only.

Google Sheets auth
  Service account (ws-financial-analysis@qwen-project-492821.iam.gserviceaccount.com) is used for all sheet writes. Any new spreadsheet must be shared with this address (Editor role). Key at Financial_Analysis_App/python/service_account.json — gitignored, never committed.

Tailscale VPN
  Tablet ↔ laptop communication runs through the tcp-partners.com Tailscale tailnet.
  Tablet: wsmdo-tab-s10-25 (100.96.244.82) | Laptop WSL2: ws-2023 (100.68.100.23) | Laptop Windows: ws-2023-1 (100.99.213.23)

OPEN QUESTIONS / NEXT STEPS

1. Human review of Deltas (A1) — The single highest-leverage action. Open Crispin_Carlos sheet → Deltas tab → filter real_error → fill cols I/J/K/L.

2. apply_corrections.py (to build) — Reads Deltas col K (Human Correction, status=done) and exports corrected pairs as supplementary training data for D6.

3. D6 fine-tune — Re-train NLLB-200 on 4,260 original pairs + human corrections from A1. Expected to improve BLEU on nominalization and verb morphology errors.

4. enrich_sullivan.py (to build) — Use fine-tuned NLLB to translate Sullivan's Nahuatl definitions → Spanish, filling 3,718 empty es fields in normalized_sullivan.json.

5. Eduardo expansion — When more col C gold is added beyond row 301, re-run translate_and_learn.py and update the training corpus.

6. Sullivan inverter — Once es fields are filled, run an inverter to produce ES→NAH mappings from Sullivan, then merge into master dictionary.json via merger.py.

7. Morphological analyzer improvements — Current morphology.py uses prefix/suffix stripping heuristics. A Nahuatl FST (finite-state transducer) would improve decomposition of complex verb forms. Long-term research task.
"""

# ── helpers ────────────────────────────────────────────────────────────────────

def para_text(element):
    para = element.get('paragraph', {})
    return ''.join(
        r.get('textRun', {}).get('content', '')
        for r in para.get('elements', [])
    ).strip()

def batch(service, doc_id, reqs):
    if reqs:
        service.documents().batchUpdate(
            documentId=doc_id, body={'requests': reqs}
        ).execute()

# ── phase 1: clear and insert content ─────────────────────────────────────────

doc = docs_service.documents().get(documentId=DOC_ID).execute()
body_content = doc.get('body', {}).get('content', [])
end_index = body_content[-1].get('endIndex', 1) if body_content else 1

reqs = []
if end_index > 2:
    reqs.append({'deleteContentRange': {'range': {'startIndex': 1, 'endIndex': end_index - 1}}})
reqs.append({'insertText': {'location': {'index': 1}, 'text': CONTENT}})
batch(docs_service, DOC_ID, reqs)
print('Phase 1: content inserted')

# ── phase 2: apply heading styles + pageBreakBefore ───────────────────────────

doc = docs_service.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])

style_reqs = []
for element in body:
    para = element.get('paragraph')
    if not para:
        continue
    text = para_text(element)
    start = element.get('startIndex', 0)
    end   = element.get('endIndex', 0)

    if text == 'Nahuatl Translator 2 — English to Huasteca Nahuatl':
        style_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': 'HEADING_1'},
            'fields': 'namedStyleType',
        }})

    elif text == TOC_HEADER or text in SECTIONS:
        is_toc_entry = (text in SECTIONS)
        # Both TOC header and section headings get HEADING_2 …
        style_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': 'HEADING_2'},
            'fields': 'namedStyleType',
        }})
        # … but pageBreakBefore only on TOC header and each section (not the TOC entry lines)
        # We distinguish TOC entries from actual section headings in phase 3 after reading back.

    elif any(text.startswith(p) for p in HEADING_3_PREFIXES):
        style_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': 'HEADING_3'},
            'fields': 'namedStyleType',
        }})

batch(docs_service, DOC_ID, style_reqs)
print('Phase 2: heading styles applied')

# ── phase 3: read back → identify real section headings vs TOC entries ─────────
# After applying HEADING_2, actual section headings have headingId; TOC entries don't yet.
# We apply pageBreakBefore only to actual section headings (not TOC entry lines).

doc = docs_service.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])

# Collect all HEADING_2 paragraphs and check whether they are in the TOC region.
# Strategy: the first time we see a section name as HEADING_2 it is the TOC header region
# or the actual heading. We detect the boundary by position — TOC entries come before
# the section heading with the same text.
seen_texts = set()
page_break_reqs = []
heading_id_map = {}   # section_text → headingId (for actual headings, not TOC entries)
toc_entry_ranges = {} # section_text → (startIndex, endIndex) for the TOC entry paragraph

for element in body:
    para = element.get('paragraph', {})
    style = para.get('paragraphStyle', {})
    named = style.get('namedStyleType', '')
    heading_id = style.get('headingId')
    text = para_text(element)
    start = element.get('startIndex', 0)
    end   = element.get('endIndex', 0)

    if named != 'HEADING_2':
        continue

    if text == TOC_HEADER:
        # TOC header itself gets a page break (puts TOC on its own page after title)
        page_break_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'pageBreakBefore': True},
            'fields': 'pageBreakBefore',
        }})
        continue

    if text in SECTIONS:
        if text not in seen_texts:
            # First occurrence = TOC entry (inside the TOC section, before the real heading)
            toc_entry_ranges[text] = (start, end)
            seen_texts.add(text)
        else:
            # Second occurrence = actual section heading → page break + collect headingId
            page_break_reqs.append({'updateParagraphStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'paragraphStyle': {'pageBreakBefore': True},
                'fields': 'pageBreakBefore',
            }})
            if heading_id:
                heading_id_map[text] = heading_id

batch(docs_service, DOC_ID, page_break_reqs)
print(f'Phase 3: pageBreakBefore applied to {len(page_break_reqs)} headings')
print(f'         headingIds collected: {list(heading_id_map.keys())}')

# ── phase 4: apply hyperlinks to TOC entry lines ──────────────────────────────

link_reqs = []
BLUE = {'red': 0.07, 'green': 0.33, 'blue': 0.80}

for section in SECTIONS:
    if section not in toc_entry_ranges:
        print(f'  WARNING: TOC entry not found for "{section}"')
        continue
    if section not in heading_id_map:
        print(f'  WARNING: headingId not found for "{section}"')
        continue

    start, end = toc_entry_ranges[section]
    hid = heading_id_map[section]
    # endIndex includes the newline — exclude it from the link range
    link_reqs.append({'updateTextStyle': {
        'range': {'startIndex': start, 'endIndex': end - 1},
        'textStyle': {
            'link': {'headingId': hid},
            'underline': True,
            'foregroundColor': {'color': {'rgbColor': BLUE}},
        },
        'fields': 'link,underline,foregroundColor',
    }})

batch(docs_service, DOC_ID, link_reqs)
print(f'Phase 4: {len(link_reqs)} TOC hyperlinks applied')
print(f'\nDone — https://docs.google.com/document/d/{DOC_ID}/edit')
