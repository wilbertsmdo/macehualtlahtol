import json
from google.oauth2.credentials import Credentials as OAuthCreds
from google.oauth2.service_account import Credentials as SACredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SA_KEY     = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
TOKEN_PATH = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json'
DOC_ID     = '1EaSMcyl24HsZ-YySRUc0LWSx4gCmRRjHt5qArxTSuVk'
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
        body={'name': 'Mayaihcuilolliztli — Project Plan',
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
    'HOW THE PIPELINE WORKS',
    'GLYPH RESOURCES',
    'TOOLS & PACKAGES — WITH RATIONALE',
    'PHASE STATUS',
    'CURRENT STATE',
    'OPEN QUESTIONS / NEXT STEPS',
]

HEADING_3_PREFIXES = (
    'Phase 1',
    'Phase 2',
    'Phase 3',
    'Phase 4',
    'Phase 5',
)

# ── document content ───────────────────────────────────────────────────────────

CONTENT = """\
Mayaihcuilolliztli — Maya Syllabary Transliterator
Project Plan · 2026-09-21

Table of Contents

WHAT IS THIS PROJECT?
WHY BUILD THIS?
HOW THE PIPELINE WORKS
GLYPH RESOURCES
TOOLS & PACKAGES — WITH RATIONALE
PHASE STATUS
CURRENT STATE
OPEN QUESTIONS / NEXT STEPS

WHAT IS THIS PROJECT?

Mayaihcuilolliztli is a Maya syllabary transliterator: it takes any Spanish or English word, breaks it into syllables, maps each syllable to an authentic Classic Maya syllabogram, and renders the result as a PNG image strip. It is live and public at https://huggingface.co/spaces/wilbertsmdo/Mayaihcuilolliztli — no login required.

The name "Mayaihcuilolliztli" is Nahuatl for "the act of Maya writing." The app targets phonetic transliteration, not translation: it does not convert meaning, only sound. "Chocolate" → cho · ko · la · te → four authentic Maya syllabogram glyphs.

WHY BUILD THIS?

Classic Maya glyphs are not reliably renderable via Unicode as of 2026. The Unicode block for Maya Hieroglyphs (U+10000 range) exists but font support is nearly nonexistent — pasting Maya Unicode produces blank boxes on virtually every device. The only practical way to display Maya syllabograms is through image assets.

No existing tool lets a user type a modern word and see it rendered in Maya script. Mayaihcuilolliztli fills that gap: it combines a curated glyph image library (sourced from Wikimedia Commons) with a rule-based syllable mapper and a Pillow-based image compositor, deployed as a Gradio web app.

Cultural value: it makes Classic Maya writing tangible and interactive for people with no background in epigraphy. Educational value: it demonstrates the synharmony convention and the phoneme inventory differences between Maya, Spanish, and English.

HOW THE PIPELINE WORKS

The transliteration pipeline has four stages:

Stage 1 — Syllabification
  syllabifier_es.py takes a Spanish word and splits it into CV syllables using rule-based Spanish orthography. Handles: digraphs (ch, ll, rr, qu, gu before e/i), diphthongs (weak+strong, strong+weak, weak+weak), triphthongs, hiatus (strong+strong and accented weak vowels), inseparable onset clusters (bl, br, tr, pl, etc.), terminal y→i normalization.
  18 unit tests, all passing.

Stage 2 — Phoneme Mapping
  phoneme_mapper.py maps each syllable to a Maya CV sign using the Landa alphabet consonant substitution table:
    r→l | f→p | d→t | z→s | v→b | ll→y | rr→l | qu→k
  Context-sensitive: c/g change based on following vowel (ce/ci→s/j; ca/co/cu→k/k).
  Synharmony rule: each CVC syllable produces an extra dummy CV sign with a silent final vowel.
  Fallback: known syllabary gaps (be→bi, pe→pi, so→su) with exact=False flag for amber border rendering.
  36 unit tests, all passing.

Stage 3 — Glyph Image Selection
  renderer_linear.py picks the best JPG variant per CV key from mappings.json:
    exact name → _1 variant → non-prefix/suffix → any available
  Scales all glyphs to 150px height. Pastes left-to-right with white backing.
  Amber border on fallback (approximate) signs; gray placeholder for unknown signs.
  Caption below each glyph shows the romanized syllable key.

Stage 4 — Image Compositing + Web UI
  Pillow composites the selected glyph images into a single horizontal PNG strip.
  Gradio app (app.py) accepts a Spanish word, runs the full pipeline, and returns the PNG inline via base64. Syllable breakdown and sign keys are shown below. Three collapsible info sections explain the concept, methodology, and sources.

GLYPH RESOURCES

Source: Wikimedia Commons — Classic Maya syllabary glyph images (Knorosov catalog)
Format: JPG per syllabogram, keyed by CV value (e.g., ba.jpg, cha.jpg, ku_1.jpg)
Coverage: 235 files across 114 unique CV keys
Mapping file: data/mappings.json — structure: {base_cv_key: [{variant_key, local_file, drive_id, wikimedia_title, url}, …]}
Multiple variants per key are normal (e.g., "cha" has cha.jpg, cha_1.jpg, cha_2.jpg)

Download script: download_glyphs.py
  Uses requests (not subprocess/wget — subprocess.run is broken on PRoot/Android)
  5s sleep between files for polite rate limiting (Wikimedia 429s after rapid requests)
  Idempotent: skips existing files; handles 429 with exponential backoff
  Wrote 220 files to Google Drive folder: https://drive.google.com/drive/folders/1sgWEMmTVoIKT9n_JRnnMWrtaJNzqv1NL

Primary reference: Knorosov syllabary grid (~130 core CV signs + 5 vowel signs)
Secondary reference: The New Catalog of Maya Hieroglyphs (Macri & Looper, 2003)
Attribution: FAMSI (Foundation for the Advancement of Mesoamerican Studies), Wikimedia contributors

Known syllabary gaps: be, pe, so, wu, xe — fallback to nearest vowel variant with amber border in output

TOOLS & PACKAGES — WITH RATIONALE

1. Pillow (PIL)
   What: Python image processing library. Loads, resizes, and composites images.
   Why needed: The core rendering engine. Given a list of glyph JPG files, Pillow opens each, scales it to a uniform height (150px), and pastes them left-to-right onto a white canvas to produce the final PNG strip. No alternative pure-Python library can do this.
   Why Pillow specifically: Pure Python, no compiled C extensions beyond libjpeg — installable on Termux ARM without issues.
   Installed: Termux Python via pip3

2. Gradio
   What: Python library for building ML demo web UIs. Native runtime for HuggingFace Spaces.
   Why needed: The app needs a public web interface. Gradio is natively supported by HuggingFace Spaces (SDK: Gradio) — no Docker container or custom build step required. Users type a word, click a button, see the glyph PNG inline.
   Why not Flask: Flask was the original framework. HuggingFace Spaces supports Flask only via a custom Docker container, which requires a paid tier. Gradio runs on the free tier with ZeroGPU.
   Why not Streamlit: Streamlit requires pandas and pyarrow, which have no aarch64 wheels for Python 3.13 on Termux — not installable.
   Installed: Termux Python via pip3; runs on HuggingFace ZeroGPU free tier

3. requests
   What: HTTP client library for Python.
   Why needed: download_glyphs.py fetches glyph JPG files from Wikimedia Commons. requests handles streaming downloads, 429 rate-limit detection, and retry logic cleanly. subprocess/wget was the original approach but subprocess.run(capture_output=True) raises OSError on PRoot/Android (pipe() syscall unavailable).
   Already installed: Termux Python (part of workspace manifest)

4. huggingface_hub
   What: HuggingFace Python SDK for repository operations (upload, download, model management).
   Why needed: HuggingFace git push was rejected for .jpg binary files (HF now routes binaries through Xet storage, breaking standard git). huggingface_hub's api.upload_folder() bypasses git entirely and uploads the full project directory (235 glyph JPGs included) directly to the Space repo.
   Install note: install with --no-deps to skip hf-xet, which requires Rust/maturin (not available on Termux ARM). Pure upload API still works without it.
   Installed: Termux Python via pip3 install huggingface_hub --no-deps

5. spaces (HuggingFace ZeroGPU)
   What: HuggingFace library for GPU-accelerated Spaces.
   Why needed: HuggingFace ZeroGPU requires at least one @spaces.GPU-decorated function or the container shuts down at startup. The transliterate() function uses @spaces.GPU(duration=0) — duration=0 tells ZeroGPU the function needs GPU for zero seconds, satisfying the requirement without actually requesting a GPU. This is a workaround for running a CPU-only app on ZeroGPU hardware.
   Available in HuggingFace Spaces environment automatically

PHASE STATUS

Phase 1 — Foundation & Data Layer [DONE]
  Syllabary mapping table (data/mappings.json): 114 CV keys, 235 variants
  Glyph image assets: 235 JPG files in glyphs/ (downloaded from Wikimedia Commons)
  Spanish syllabifier (syllabifier_es.py): rule-based, 18 unit tests passing
  Phoneme mapper (phoneme_mapper.py): Landa substitutions + synharmony, 36 unit tests passing

Phase 2 — Linear Glyph Renderer [DONE]
  renderer_linear.py: Pillow-based, 150px height normalization, left-to-right compositing
  app.py (Gradio): full web UI with syllable breakdown, sign keys, 3 info accordions
  End-to-end test: "chocolate" → cho · ko · la · te → four authentic Maya glyph images ✓
  Deployed to HuggingFace Spaces (https://huggingface.co/spaces/wilbertsmdo/Mayaihcuilolliztli)

Phase 3 — English Support [PENDING]
  syllabifier_en.py: not yet built
  Plan: CMU Pronouncing Dictionary (NLTK cmudict) for phonemic transcription + rule-based fallback
  Extended phoneme mapper for English phonemes (IPA-based mapping)

Phase 4 — Maya-Style Agglutinated Glyph Blocks [PENDING]
  compositor.py: not yet built
  Goal: group syllabograms into ~square Maya-style glyph blocks (main sign + prefix/suffix positions)
  Research needed: block composition rules from actual inscriptions

Phase 5 — Web / App Interface [DONE — via Phase 2]
  Gradio app deployed to HuggingFace Spaces; public URL; free tier; no login required

CURRENT STATE

App status: LIVE at https://huggingface.co/spaces/wilbertsmdo/Mayaihcuilolliztli
GitHub repo: https://github.com/wilbertsmdo/mayaihcuilolliztli (249 files, 235 glyph JPGs)
HuggingFace cold start: ~30s after inactivity, then runs normally on ZeroGPU free tier

Glyph assets:
  235 JPG files in glyphs/; 114 unique CV keys in data/mappings.json
  Known gaps: be, pe, so, wu, xe — fallback to nearest vowel variant (amber border in output)

Test suite:
  54 unit tests passing — 18 syllabifier + 36 phoneme mapper
  End-to-end: "chocolate" → cho·ko·la·te → 4 glyphs confirmed authentic ✓

Active scripts (local, Termux):
  syllabifier_es.py, phoneme_mapper.py, renderer_linear.py, app.py,
  download_glyphs.py, write_plan_to_doc.py

Pending phases: Phase 3 (English) and Phase 4 (block compositor) — no timeline set

OPEN QUESTIONS / NEXT STEPS

1. Manual QA — test a wider range of Spanish words in the live HuggingFace app; look for mapping errors (wrong glyph selected), layout issues (wrong spacing), and missing glyphs.

2. Syllabary gap review — decide whether to supplement be, pe, so, wu, xe from alternative SVG sources or accept current fallbacks. FAMSI has higher-quality images; license check needed.

3. Phase 3 — English support — implement syllabifier_en.py using CMU Pronouncing Dictionary (NLTK cmudict) + rule-based fallback for unknown words. Extend phoneme_mapper.py for English-specific IPA phonemes (th→t/s, ng→n, etc.).

4. Variant selector — _pick_file() in renderer_linear.py always picks the canonical variant. Consider exposing a dropdown in the Gradio UI to cycle through glyph variants for aesthetics.

5. Phase 4 — Glyph block compositor — build compositor.py to pack syllabograms into proper Maya-style square blocks (main sign + prefix/suffix). Requires studying actual inscriptions to derive composition rules.

6. Allographic variation — each CV sign has multiple variant forms (cha.jpg, cha_1.jpg, cha_2.jpg). A future "style" toggle could select between Classic, Late Classic, or regional variants.

7. Proper noun / loanword handling — words with phonemes far outside Maya inventory (English "strength", "sphinx") produce approximate output. Consider adding a warning label when approximation quality is low.
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

# ── phase 2: apply heading styles ─────────────────────────────────────────────

doc = docs_service.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])

style_reqs = []
for element in body:
    para = element.get('paragraph')
    if not para:
        continue
    text  = para_text(element)
    start = element.get('startIndex', 0)
    end   = element.get('endIndex', 0)

    if text == 'Mayaihcuilolliztli — Maya Syllabary Transliterator':
        style_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': 'HEADING_1'},
            'fields': 'namedStyleType',
        }})
    elif text in (TOC_HEADER,) or text in SECTIONS:
        style_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': 'HEADING_2'},
            'fields': 'namedStyleType',
        }})
    elif any(text.startswith(p) for p in HEADING_3_PREFIXES):
        style_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': 'HEADING_3'},
            'fields': 'namedStyleType',
        }})

batch(docs_service, DOC_ID, style_reqs)
print('Phase 2: heading styles applied')

# ── phase 3: page breaks + collect heading IDs ────────────────────────────────

doc = docs_service.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])

seen_texts     = set()
page_break_reqs = []
heading_id_map  = {}
toc_entry_ranges = {}

for element in body:
    para = element.get('paragraph', {})
    style = para.get('paragraphStyle', {})
    named = style.get('namedStyleType', '')
    heading_id = style.get('headingId')
    text  = para_text(element)
    start = element.get('startIndex', 0)
    end   = element.get('endIndex', 0)

    if named != 'HEADING_2':
        continue

    if text == TOC_HEADER:
        page_break_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'pageBreakBefore': True},
            'fields': 'pageBreakBefore',
        }})
        continue

    if text in SECTIONS:
        if text not in seen_texts:
            toc_entry_ranges[text] = (start, end)
            seen_texts.add(text)
        else:
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

# ── phase 4: hyperlinks on TOC entries ────────────────────────────────────────

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
