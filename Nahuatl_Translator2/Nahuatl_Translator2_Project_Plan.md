# Nahuatl Translator 2 — Project Plan

## Last checkpoint: 2026-09-28

---

## Project overview

English → Modern Huasteca Nahuatl (IDIEZ) PDF translator.
Produces bilingual side-by-side PDF output.
Primary dictionary: IDIEZ (6,345 EN→NAH entries).

---

## Current state

### Repository
- Local: `/storage/self/primary/PY_Projects/Nahuatl_Translator2`
- GitHub: `wilbertsmdo/Nahuatl_Translator` (private)
- Branch: `main`
- Sparse-checkout excludes: `.venv/`, `dictionaries/sources/` (raw PDFs — large), `node_modules/`, `__pycache__/`

### Key files
| File | Purpose |
|------|---------|
| `translator.py` | Main orchestrator, PDF generation |
| `grammar_rules.py` | Translation engine (refactored from 3,124 → 1,022 lines; data tables extracted to `data/`) |
| `verb_conjugator.py` | English verb conjugation |
| `synonyms.py` | Fallback synonym map |
| `unknown_words.py` | Unknown word tracking |
| `dictionaries/dictionary_idiez.json` | Final EN→NAH dictionary (6,345 entries) |
| `parallel_sentences.json` | 1,693 EN↔NAH sentence pairs for quality testing |
| `unknown_words.json` | 267 pending unknown words |

### IDIEZ dictionary pipeline (complete)
| Step | Script | Output |
|------|--------|--------|
| 1 | `dictionaries/parser.py` | `raw_idiez.json` |
| 2 | `dictionaries/normalizer.py` | `normalized_idiez.json` |
| 3 | `dictionaries/enricher.py` (spaCy) | `enriched_idiez.json` |
| 4 | `dictionaries/inverter.py` | `dictionary_idiez.json` |
| 5 | `dictionaries/merger.py` | `dictionary.json` (pending) |

**Inverter scoring system** (step 4):
- +25 literal match, +15 root priority, +10 grammatical alignment, +10 brevity bonus
- +5 keyword in definition
- -10 noise penalty (generic words: "person", "thing", etc.)

Note: Karttunen pipeline files (`dictionary_karttunen.json` etc.) exist but are classical Nahuatl — secondary/fallback only.

---

## Crispin text project (Google Sheet)

### Source
- PDF: **Tlallamiquiliztli inelhuayo** (Crispín Martínez Rosas, 2021)
  - 207 pages — Huasteca Nahuatl prose fiction/short stories
  - Google Drive file ID: `1d64U8NF-AKugpaVwUB8T2EyYxdg3rCza`

### Google Sheet
- **Nahuatl Tequitl - Crispin**
- Spreadsheet ID: `12ebNz0hxWwoXEpDcXITuRN1q9Q2dlVXwiaJd2YQWUP4`
- Worksheet: `Crispin`
- Columns: A (section label) | B (Nahuatlahtolli) | C (Coyotlahtolli/Spanish) | D (Questions/Vocab notes) | E (empty)

### Transcription status (as of 2026-05-23)
| Rows | Col B | Col C | Notes |
|------|-------|-------|-------|
| 4–488 | Nahuatl ✓ | Spanish ✓ | Front matter + early chapters |
| 489–659 | Nahuatl ✓ | Spanish pending | Manually transcribed, no Spanish yet |
| 660–4036 | Nahuatl ✓ | Spanish pending | **Auto-transcribed this session** (PDF pages 34–207) |

Total sheet rows: **4,036** (659 existing + 3,377 auto-transcribed).

### Transcription conventions (must match for any future work)
- One sentence per row in col B
- Dialogue `—` at start → `- `; internal attribution `—` → ` - `; closing `—.` → `.`
- `¿` `¡` stripped; `«` → `<`, `»` → `>`
- Attribution tag (`- quiillia…`) stays on same row as its dialogue sentence
- Hyphenated word-breaks from PDF are rejoined

### Scripts used (in `Nahuatl_Translator2/`)
| Script | Purpose |
|--------|---------|
| `inspect_docs.py` | Read-only preview of Drive PDF + Sheet |
| `inspect_sheet_detail.py` | Sheet structure analysis |
| `transcribe_pdf_to_sheet.py` | **Main transcription script** — PDF pages → Sheet col B |
| `parse_drive_pdf_to_sheets.py` | Earlier draft (superseded) |

---

## App design

Full schematic saved to `APP_DESIGN.md` (nano-readable plain ASCII).
Covers: dictionary build pipeline (A), runtime translation pipeline (B),
unknown-words feedback loop (C), data files reference (D), known gaps (E).

---

## ML training strategy (decided 2026-05-23)

Goal: train a model to translate English → Huasteca Nahuatl.

### Recommended sequence

**Step 1 — Now (no training required)**
Wire `dictionary_idiez.json` + `parallel_sentences.json` into a Claude API
call: relevant dict entries + 5–10 few-shot examples injected as context per
request. Immediate quality improvement over the current rule-based system.

**Step 2 — Medium term (fine-tune NLLB-200)**
- Model: `facebook/nllb-200-distilled-600M` (already supports `nah_Latn`)
- Fine-tune on parallel data rather than train from scratch
- Training data sources:

  | Source | Pairs | Quality |
  |--------|-------|---------|
  | `parallel_sentences.json` | 1,693 | High (IDIEZ) |
  | Crispin sheet col B↔C rows 4–488 | ~480 | Medium (NAH↔ES) |
  | Dictionary entries as synthetic pairs | ~6,345 | Low (word-level) |

- **Key unlock**: finishing col C for rows 489–4,036 adds ~3,500 NAH↔ES
  sentence pairs — the single highest-leverage data task for ML.

**Step 3 — Long term (morphological analyzer)**
- Pre-processing step before the translator
- Decompose `nitlatequitiz` → `ni + tla + tequiti + z`
- Required for any model to handle unseen verb forms correctly
- Sits between lookup steps 2 and 3 in the current pipeline

### Bottleneck
Data volume, not compute. Every translated sentence in the Crispin sheet
(col C) is more valuable than any model architecture choice.

---

## Open work items

### Priority 1 — Crispin sheet
- [ ] Verify auto-transcription quality: spot-check ~20 rows across different chapters
- [ ] Fill col C (Spanish translation) for rows 489–4036 — this is manual or LLM-assisted work
- [ ] Fill col D (vocabulary/grammar notes) as reading progresses

### Priority 2 — ML training path
- [ ] Wire `dictionary_idiez.json` + `parallel_sentences.json` into Claude API (few-shot, Step 1)
- [ ] Complete Crispin sheet col C rows 489–4,036 (NAH↔ES pairs — key training data)
- [ ] Fine-tune `facebook/nllb-200-distilled-600M` once col C is sufficiently filled (Step 2)
- [ ] Build morphological analyzer as pre-processing step (Step 3, long term)

### Priority 3 — Translator pipeline
- [ ] Integrate `dictionary_idiez.json` into `translator.py` / `grammar_rules.py`
- [ ] Run quality tests with `parallel_sentences.json` (1,693 pairs)
- [ ] Improve unknown word review workflow — replace manual JSON editing with a CLI or web UI that can suggest translations via LLM
- [ ] Expand phrase dictionary (`data/common_phrases.json`) — multi-word EN→NAH patterns like "in order to", "as soon as", "because of" (currently only a handful hardcoded)
- [ ] Add missing grammar rules to `grammar_rules.py`: object prefixes, applicatives, causatives, plurals

### Priority 4 — Dictionary pipeline
- [ ] Run `merger.py` to produce final `dictionary.json` combining all sources

---

## Checkpoint — 2026-05-23 (session 4)

### Work completed this session
- **Built `few_shot_translate.py`** — Claude API NAH→ES translation script for the Crispin sheet
  - Uses OAuth token (same as transcription scripts) to read/write the sheet
  - Loads few-shot examples from col B+C of a specified row range in the sheet itself
  - Looks up IDIEZ dictionary hints per sentence (`enriched_idiez.json`) and injects up to 8 Spanish definitions as context
  - Calls `claude-haiku-4-5` with system prompt + few-shot turns + dict hints per sentence
  - Writes Claude's draft translation to col E; prints NAH / gold (col C) / Claude side-by-side for review
  - Configured for test run: rows 15–24 (test), rows 5–9 (few-shot examples)
- **Confirmed `anthropic` SDK installed** (v0.97.0 via Termux pip)
- **Identified blocker**: Anthropic API requires a paid account — API key not set in environment
- **Discussed cost**: haiku-4-5 pricing makes full 3,500-row batch ≈ $0.05–0.10 total; discussed free alternatives (Gemini free tier, Ollama local)

### Current state
- `few_shot_translate.py` is complete and ready to run — only blocked by missing `ANTHROPIC_API_KEY`
- Script has been verified to load correctly through sheet auth and dictionary load steps
- Translation pipeline design is solid: few-shot from sheet + IDIEZ dict hints + Claude → col E
- Crispin sheet: 4,036 rows; col B complete; col C done rows 4–488; col E empty

### Next steps
1. Set `ANTHROPIC_API_KEY` (get from console.anthropic.com, fund account)
2. Run test: `! export ANTHROPIC_API_KEY=... && /data/data/com.termux/files/usr/bin/python3 few_shot_translate.py`
3. Review 10 rows: compare col E (Claude) vs col C (gold) in the sheet — spot-check quality
4. If quality is acceptable, extend script to run on full rows 4–488 (gold range) for baseline error measurement
5. Then extend to rows 489–4,036 (fill col E for all pending Spanish)
6. Begin correction pass: edit col E → col C (creates training data for NLLB-200)

### Notes
- **Model choice**: `claude-haiku-4-5` used for cost efficiency — upgrade to `claude-sonnet-4-6` if translation quality is too low
- **Free alternative**: Google Gemini API has a free tier (Gemini 1.5 Flash) — would need to rewrite `client.messages.create()` calls if going that route
- **Dict lookup limitation**: current tokenizer does exact lowercase match against `enriched_idiez.json` keys; many tokens will miss (Nahuatl is agglutinative — "niquintalazcamatilia" won't match "tlazcamatilia"). Still useful for standalone words. Improve later with prefix/suffix stripping.
- **`ANTHROPIC_API_KEY` persistence**: add to Termux `~/.bashrc` so it survives session restarts: `echo 'export ANTHROPIC_API_KEY=sk-...' >> ~/.bashrc`

---

## Session history

| Date | Summary |
|------|---------|
| 2026-05-04 | Initial setup: git init + sparse-checkout, pulled from GitHub. IDIEZ pipeline (steps 1–4) confirmed fully populated (6,345 EN→NAH entries). Established IDIEZ-only focus (Karttunen = classical fallback). |
| 2026-05-23 | Auto-transcribed Crispin PDF pages 34–207 into Google Sheet (rows 660–4,036, col B). Decided ML training strategy (Step 1: Claude API few-shot → Step 2: NLLB-200 fine-tune → Step 3: morphological analyzer). |

---

## Reference documents
| File | Contents |
|------|---------|
| `APP_DESIGN.md` | Full app architecture schematic (nano-readable) |
| `dictionaries/sources/nahuatl_nnc_structure_yale.pdf` | Nahuatl Noun-Noun Compound (NNC) morphology chart — Yale study group. One-page formal slot diagram: prefix positions, person markers, absolute/possessive states, monadic/dyadic possession, three stem types (base/affinity/distributive), GU root stem transformation rules for tl-class nouns. Critical reference for morphological analyzer FST and neologism generator combining-form rules. Verb morphology chart pending (same source). |
| `dictionaries/sources/sullivan_2016.pdf` | Sullivan 2016 — Tlahtolxitlauhcayotl Chicontepec (NAH→NAH monolingual dictionary, 9,782 entries) |

---

## Environment notes

### Python interpreter
Always use Termux Python — do NOT use PRoot `/usr/bin/python3` (missing packages):
```bash
/data/data/com.termux/files/usr/bin/python3 your_script.py
```

### Installing packages
- **Pure-Python** (requests, gspread, anthropic, etc.): `pip3 install <package>`
- **Compiled** (numpy, pandas, scipy): must use Termux pkg — no aarch64 wheels on PyPI
  ```bash
  ! pkg install python-numpy python-pandas   # run from Claude Code prompt
  ```
- Installed compiled packages: `numpy` 2.4.4

### Google credentials
| File | Purpose |
|------|---------|
| `../Financial_Analysis_App/python/service_account.json` | Sheets write access (service account) |
| `../Financial_Analysis_App/python/token.json` | Drive read access (OAuth, used by transcription scripts) |

- Service account email: `ws-financial-analysis@qwen-project-492821.iam.gserviceaccount.com`
- Any new spreadsheet must be shared with that email (Editor) before scripts can write to it
- Never commit credential files (gitignored)

---

## Checkpoint — 2026-08-10

### Work completed this session

- **Reconnected Tailscale on tablet** — fixed SSH timeouts that blocked the previous session (root cause: tablet was offline 24+ days)
- **SSH'd into laptop** — confirmed connection to WSL2 at `100.68.100.23` (wslinux@ws-2023, Ubuntu 24.04.4)
- **Diagnosed zombie process** — PID 9 `[sh] <defunct>` owned by root; confirmed harmless WSL2 system artifact, not a blocker
- **Located repo on laptop** — folder is named `Nahuatl_Translator` (not `Nahuatl_Translator2`); found at `~/WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator/`; `find` with the name `Nahuatl_Translator2` returned nothing — must search for `Nahuatl_Translator`
- **Launched D4 (NLLB fine-tune)** — activated venv, started training in tmux session `d4`; last seen downloading NLLB-200-distilled-600M safetensors model at 43 MB/s (33% complete); training will begin automatically once download finishes
- **Confirmed tmux detach works** — training continues in background after detaching; can re-attach from tablet at any time
- **Added `find` command to WS Knowledge Base** — documented in `WS_Knowledge_base.md`

### Current state

- **D4 is running** on the laptop in tmux session `d4`; NLLB model was downloading when last observed; training on 4,594 pairs (10 epochs, fp16) should begin automatically after download
- All pipeline code unchanged since commit `f943c90` (2026-07-13)
- 4 untracked files still pending commit: `dictionaries/compare_sullivan_idiez.py`, `normalized_sullivan_enriched.json`, `dictionaries/sources/sullivan_2016.pdf`, `sullivan_pending_enrichment.json`
- Project plan has uncommitted checkpoints from 2026-07-14 and 2026-08-07/08 sessions

### Next steps

1. **Check D4 progress** — SSH in and attach to tmux to see training loss / completion:
   ```bash
   ssh wslinux@100.68.100.23        # from Termux (Tailscale must be connected)
   tmux attach -t d4
   ```
2. **Wait for D4 to finish** — training will print loss per batch; on GPU ~30 min–2 hrs; CPU only ~8–20 hrs
3. **D5 — Evaluate fine-tuned NLLB** — run held-out sentences through `models/nllb-nah-es-final/`; record BLEU scores vs vanilla NLLB baseline
4. **Install Ollama on laptop** — `curl -fsSL https://ollama.ai/install.sh | sh` in WSL2; pull `ollama pull llama3.1:8b`
5. **Swap `translate_and_learn.py` client** — replace Anthropic API call with Ollama HTTP endpoint; test on 10 Crispin rows
6. **Build NLLB + LLaMA cascade** — NLLB produces rough draft; LLaMA refines with rules + dictionary hints
7. **`enrich_sullivan.py`** — use fine-tuned NLLB to fill 9,782 empty `es` fields in `normalized_sullivan.json`
8. **Commit untracked files** — skip `sullivan_2016.pdf` if too large; commit the other 3
9. **A1 (Human)** — review Crispin_Carlos col H auto rules; add corrections to col I (0 human-verified rules is the biggest quality gap)

### Notes — reconnecting to D4

**To check training from the tablet at any time:**
```bash
# Step 1 — ensure Tailscale is connected on tablet (open Tailscale app → Connect)
# Step 2 — SSH from Termux:
ssh wslinux@100.68.100.23
# Step 3 — attach to training session:
tmux attach -t d4
# Step 4 — detach without stopping training:
# Press Ctrl+B, then D
```

---

## Checkpoint — 2026-08-13

### Work completed this session

- **Confirmed D4 did NOT complete last time** — tmux session `d4` was gone; `models/` folder absent; no `.safetensors` file anywhere on laptop. Training had silently crashed (likely during model download) with no log to show it.
- **Confirmed Crispin_Carlos sheet is fully populated** — all 4,030 rows have both Nahuatl (col B) and Spanish (col C). Previous assumption that rows 489–4,036 were empty was wrong. Re-ran `export_training_data.py` — confirmed 4,312 NAH↔ES pairs (same as July export; sheet unchanged).
- **Built D5 eval script (`eval_nllb_d5.py`)** — reads `training_data/nah_es_pairs.json`, runs fine-tuned NLLB on all 4,312 Nahuatl sentences, computes sentence BLEU vs gold Spanish (col C), writes translations to col J and BLEU scores to col K. Cols B–I untouched.
- **Fixed `finetune_nllb.py` for modern transformers (v5.15.0)** — four API breaking changes patched: `as_target_tokenizer()` → `text_target=`, `evaluation_strategy` → `eval_strategy`, `tokenizer=` removed from `Seq2SeqTrainer`, `NllbTokenizer` → `AutoTokenizer`. Added preflight package check and version print at startup.
- **Relaunched D4** — training confirmed running in tmux session `d4` on RTX 3060 GPU; 0% | 19/4860 steps visible; ~12 hrs estimated. Moved into tmux before tablet closed.
- **Added 7 terms to WS Knowledge Base** — BLEU, fine-tuning, tmux, torch, transformers, venv, weights.

### Current state

- **D4 is running** in tmux session `d4` on laptop; training 3,881 pairs over 10 epochs with fp16 on RTX 3060; estimated ~12 hrs from start
- `eval_nllb_d5.py` ready to run once D4 completes — needs `service_account.json` copied to `~/service_account.json` on laptop first
- All fixes pushed to GitHub (`main`, commit `db9cbc2` and after)

### Next steps

1. **Check D4 progress** — SSH in and attach:
   ```bash
   ssh wslinux@100.68.100.23
   tmux attach -t d4
   ```
2. **Once D4 done — copy service account key to laptop:**
   ```bash
   scp /storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json wslinux@100.68.100.23:~/service_account.json
   ```
3. **Run D5 eval on laptop:**
   ```bash
   source .venv/bin/activate
   python3 eval_nllb_d5.py 2>&1 | tee d5_eval.log
   ```
4. **Review sheet** — cols J (NLLB translation) + K (NLLB BLEU) in Crispin_Carlos sheet; compare against col E (Claude) and col F (Claude BLEU)
5. **Commit untracked files** — `dictionaries/compare_sullivan_idiez.py`, `normalized_sullivan_enriched.json`, `sullivan_pending_enrichment.json` (skip `sullivan_2016.pdf` — too large)

**Tailscale node reference:**
| Node | Tailscale IP | Platform | SSH command |
|------|-------------|----------|-------------|
| `ws-2023` (WSL2) | `100.68.100.23` | Linux | `ssh wslinux@100.68.100.23` |
| `ws-2023-1` (Windows) | `100.99.213.23` | Windows | `ssh ws@100.99.213.23` |
| `wsmdo-tab-s10-25` | `100.96.244.82` | Android (tablet) | initiates SSH, doesn't receive it |

---

## Checkpoint — 2026-08-13 (session 2)

### Work completed this session

- **Discovered D4 crashed at first checkpoint save (epoch 1, step 486/4860)** — training ran 1 hr 12 min before failing; error: `ValueError: Some generation parameters are set in the model config` caused by `forced_bos_token_id` being set on `model.config` instead of `model.generation_config`
- **Found log and models directory** — `d4_train.log` and `models/` folder ARE present at `~/WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator/` (repo is one level deeper than previously documented)
- **Fixed `forced_bos_token_id` placement** — changed `model.config.forced_bos_token_id` → `model.generation_config.forced_bos_token_id` in `finetune_nllb.py`
- **Corrected laptop repo path** — actual path is `~/WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator/` (not `Nahuatl_Translator/` alone); updated all references in this plan
- **Fixed tmux launch command** — added explicit `cd` + `source .venv/bin/activate` to the tmux command so it always runs from the right directory with the right Python
- **All fixes pushed** — commit `2774f02` on `main`

### Current state

- D4 has NOT successfully completed — crashed at epoch 1 save; no final model in `models/nllb-nah-es-final/`; intermediate checkpoints may exist in `models/nllb-nah-es/`
- `finetune_nllb.py` is now fixed and ready to re-run
- `eval_nllb_d5.py` ready for after D4 completes

### Next steps

1. **Relaunch D4 with correct tmux command:**
   ```bash
   ssh wslinux@100.68.100.23
   cd ~/WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator
   git pull
   tmux new-session -d -s d4 "cd ~/WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator && source .venv/bin/activate && python3 finetune_nllb.py 2>&1 | tee d4_train.log"
   tmux attach -t d4
   # Ctrl+B then D to detach
   ```
2. **Wait for D4 to finish** (~10–12 hrs on GPU from scratch)
3. **Copy service account key to laptop then run D5:**
   ```bash
   scp .../Financial_Analysis_App/python/service_account.json wslinux@100.68.100.23:~/service_account.json
   python3 eval_nllb_d5.py 2>&1 | tee d5_eval.log
   ```
4. **Review sheet cols J + K** (NLLB translation + BLEU) vs col E + F (Claude)
5. **Commit untracked files** — `dictionaries/compare_sullivan_idiez.py`, `normalized_sullivan_enriched.json`, `sullivan_pending_enrichment.json`

### Notes

- Repo on laptop is nested: `WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator/` — always `cd` to the inner folder
- Always activate venv before running any training/eval script: `source .venv/bin/activate`
- `models/nllb-nah-es/` may contain epoch-1 checkpoint from the crashed run — safe to delete before restarting, or leave it (trainer will overwrite)

**Repo path on laptop (WSL2):**
```
~/WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator/
```
Note: folder is named `Nahuatl_Translator` not `Nahuatl_Translator2` — use this in any `find` or `cd` commands.

**venv path on laptop:**
```bash
source ~/nllb-env/bin/activate
```

**torch version note:** A `ValueError` about torch < v2.6 appeared during model load — this is non-fatal. The library automatically falls back to safetensors format. No action needed.

### gspread boilerplate
```python
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(
    '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json',
    scopes=SCOPES
)
gc = gspread.authorize(creds)
sh = gc.open_by_key('SPREADSHEET_ID')
ws = sh.worksheet('Crispin')
```

---

## Checkpoint — 2026-08-16

### Work completed this session

- **Reviewed Tlahtolxitlauhcayotl 2016.pdf** — 644-page monolingual Nahuatl dictionary (NAH→NAH definitions) by John Sullivan / IDIEZ; same dialect as IDIEZ (Chicontepec Huasteca Nahuatl); found at `/storage/emulated/0/Download/`
- **Confirmed Sullivan pipeline already substantially complete** — all parsing was done in a prior session; no new code written this session
  - Step 1 (`parse_sullivan.py` → `raw_sullivan.json`): ✅ 9,483 entries
  - Step 2 (`normalize_sullivan.py` → `normalized_sullivan.json`): ✅ 9,250 entries
  - Step 3 (IDIEZ xref enrichment → `normalized_sullivan_enriched.json`): 🔶 5,532/9,250 have Spanish gloss; 3,718 still empty
- **Decided to wait for D4** before running enrichment — plan is to use fine-tuned NLLB to fill the 3,718 empty `es` fields via `enrich_sullivan.py` (to be built after D5 eval)

### Current state

- D4 is running on the laptop in tmux session `d4` (relaunched 2026-08-13); awaiting completion
- Sullivan enrichment is blocked on D4/D5 — no action needed on tablet until fine-tuned model is ready
- `normalized_sullivan_enriched.json` has 3,718 entries with empty `es` field; `sullivan_pending_enrichment.json` lists them

### Next steps

1. **Check D4 progress** — SSH in and attach to tmux `d4`
2. **Once D4 done — run D5 eval** (see 2026-08-13 checkpoint for commands)
3. **Build `enrich_sullivan.py`** — use fine-tuned NLLB to translate each Nahuatl definition → Spanish for the 3,718 pending entries; write back to `normalized_sullivan_enriched.json`
4. **Build Sullivan inverter** — once `es` fields are filled, produce ES→NAH mappings (similar to `dictionaries/inverter.py` for IDIEZ)
5. **Run `merger.py`** — merge Sullivan into master `dictionary.json` (Sullivan at lower priority than IDIEZ)
6. **Commit untracked files** — `dictionaries/compare_sullivan_idiez.py`, `normalized_sullivan_enriched.json`, `sullivan_pending_enrichment.json`

### Available slash commands

**Custom commands** (defined in `/storage/self/primary/PY_Projects/.claude/commands/`):

| Command | What it does |
|---------|-------------|
| `/checkpoint-write` | Appends a dated checkpoint to the project plan — work done, current state, next steps |
| `/catch-up` | Reads the project plan and returns a concise status summary (5–10 bullets) |
| `/catchup-read` | Reads ALL `.md` files in the project folder for a fuller catch-up |
| `/google-access` | Reads credentials and spreadsheet IDs before starting any Sheets/Drive work |
| `/add-term` | Adds a term definition to `WS_Knowledge_base.md` |

**Built-in Claude Code skills** (invoke with `/skill-name`):

| Skill | What it does |
|-------|-------------|
| `claude-api` | Build/debug Claude API and Anthropic SDK code — use when writing the few-shot translation script |
| `loop` | Run a prompt or command on a recurring interval |
| `schedule` | Set up a scheduled remote agent (cron-style) |
| `review` | Review a pull request |
| `security-review` | Security review of pending branch changes |
| `simplify` | Review changed code for quality and efficiency |
| `fewer-permission-prompts` | Add allowlist to reduce repeated permission prompts |
| `update-config` | Configure Claude Code settings.json (hooks, permissions, env vars) |
| `init` | Initialize or update a CLAUDE.md file |

Note: `/search` does not exist as a command in this environment.

### Device paths
| Resource | Path |
|----------|------|
| PY_Projects | `/storage/self/primary/PY_Projects/` |
| Internal storage | `/storage/emulated/0/` |
| Screenshots | `/storage/emulated/0/DCIM/Screenshots/` |
| PDF output copy | `/storage/emulated/0/Download/` |

---

## Checkpoint — 2026-05-23 (session 3)

### Work completed this session
- **Consolidated all doc files into the project plan** — merged `Nahuatl_Translator_log.md`, `IMPROVEMENTS.md`, and `QWEN.md` into `Nahuatl_Translator2_Project_Plan.md`, then deleted all three
- **Expanded environment notes** — added Python interpreter rules, pip vs pkg install guide, Google credentials (service account + OAuth paths), gspread boilerplate, and device paths (pulled from parent `CLAUDE.md`)
- **Fixed slash commands** — discovered custom commands exist at `PY_Projects/.claude/commands/` but were not accessible because Claude Code does not inherit parent-level commands; created `Nahuatl_Translator2/.claude/commands/` and copied all 5 commands in
- **Updated `checkpoint-write.md`** — added Step 2 to auto-bootstrap the commands folder and `settings.local.json` in any new project when `/checkpoint-write` is first called
- **Fixed naming conflict** — updated `catch-up.md`, `catchup-read.md`, and `checkpoint-write.md` to look for `<FolderName>_Project_Plan.md` first, `PROJECT_PLAN.md` as fallback
- **Fixed stale reference** — updated parent `CLAUDE.md` to point to project plan instead of deleted log file
- **Designed translation data workflow** — decided on Google Sheet column layout: col B (Nahuatl), col C (final Spanish/gold), col E (Claude draft), col F (error flag); discussed Claude API few-shot approach for NAH→ES auto-translation

### Current state
- Project plan is the single consolidated reference — no separate log or roadmap files
- Custom commands (`/checkpoint-write`, `/catch-up`, `/catchup-read`, `/google-access`, `/add-term`) are installed and will be active from next session onward
- ML strategy is decided: Claude API few-shot (now) → NLLB-200 fine-tune (medium) → morphological analyzer (long term)
- Crispin sheet has 4,036 rows; col B complete throughout; col C done only for rows 4–488

### Next steps
1. Restart Claude Code session to activate the custom slash commands
2. Spot-check Crispin sheet auto-transcription quality — read ~20 rows across different chapters
3. Build Claude API few-shot script: blind NAH→ES translation of rows 4–488 → write to col E
4. Review col E vs col C for rows 4–488 to measure Claude's baseline error rate and error types
5. Extend script to rows 489–4,036 — auto-fill col E for the full pending batch
6. Begin correction pass: col E → col C (corrected pairs = training data for NLLB-200)

### Notes
- Custom commands are copied — if the parent commands are ever updated, re-run the `cp *.md` command or trigger `/checkpoint-write` in a fresh session (it will re-sync automatically)
- The `normalized_idiez.json` / `enriched_idiez.json` files (NAH headwords with ES definitions) are the right dictionary inputs for NAH→ES translation — not `dictionary_idiez.json` (which is inverted to EN→NAH)
- `/search` does not exist as a command in this environment

---

## Checkpoint — 2026-06-01 (sessions 1–4)

SSH/Tailscale setup work — full notes moved to `PY_Projects/Laptop_SSH_Tailscale_Setup.md`.

**Summary:** Direct LAN SSH blocked by router AP Isolation → chose Tailscale on Windows as solution → full automation plan designed (systemd, scheduled tasks, portproxy script) but not yet executed. Requires physical laptop access to run.

**Next step for Nahuatl:** once SSH is working, set `ANTHROPIC_API_KEY` and run `few_shot_translate.py` test (rows 15–24).

---

## Checkpoint — 2026-06-01 (session 5)

SSH/Tailscale setup continued — full notes in `PY_Projects/Laptop_SSH_Tailscale_Setup.md`.

**Summary:** Full remote SSH access now working. Tablet can SSH into laptop WSL2 via `ssh wslinux@100.68.100.23` from any network. Auto-login, WSL2 auto-start, Tailscale, and SSH all confirmed working after reboot. Sleep disabled to keep connection alive.

**Next step for Nahuatl:** SSH is working — set `ANTHROPIC_API_KEY` on the laptop and run `few_shot_translate.py` test (rows 15–24) remotely from the tablet.

---

## Checkpoint — 2026-06-02

### Work completed this session
- **Created `count_words_colB.py`** — script to count words in col B of the Crispin sheet for a given row range
  - Initial version used service account auth → failed with 403 (sheet not shared with service account)
  - Fixed to use OAuth (`token.json`) — same auth method as the transcription scripts
  - Reads col B via `ws.col_values(2)`, slices from row 555 onward, counts `len(cell.split())` per non-empty cell
- **Ran word count for col B rows 555 → 4037**: 21,924 words across 3,483 rows (all non-empty)
- **Clarified scope**: the 21,924 figure covers rows 555–4037 only, not the full column B

### Current state
- Crispin sheet: 4,037 rows; col B complete throughout (rows 4–4037)
- Col C (Spanish/gold): complete rows 4–488 only; rows 489–4037 pending
- `few_shot_translate.py`: complete and ready — blocked only by missing `ANTHROPIC_API_KEY`
- SSH into laptop WSL2 is working (Tailscale: `ssh wslinux@100.68.100.23`)

### Next steps
1. Get full col B word count (all rows 4–4037) for reference — optional but useful for scope tracking
2. Set `ANTHROPIC_API_KEY` on laptop via SSH and run `few_shot_translate.py` test (rows 15–24)
3. Review col E output vs col C gold for quality assessment
4. If quality acceptable, extend to full rows 4–488, then 489–4037 (fills col E)
5. Begin correction pass: col E → col C (produces clean NAH↔ES training pairs)

### Notes
- `count_words_colB.py` is a utility script — reuse it by changing the slice index for any row range
- OAuth token may expire; if auth fails, re-run the OAuth flow that generated `token.json`

---

## Checkpoint — 2026-06-07

### Work completed this session

- **Confirmed `ANTHROPIC_API_KEY` already set** in Termux `~/.bashrc` and current environment — no SSH to laptop needed
- **Ran `few_shot_translate.py` test (rows 15–24)** — 10/10 rows translated to col E; quality assessed as acceptable
- **Transcribed Eduardo de la Cruz Cruz (2017) PDF into new Google Sheet**
  - PDF: `De la Cruz 2017 Cenyactoc cintli tonacayo.pdf` (Drive ID: `1WKOPvuEO2qh9M5q5bWWC2YL-VEbD6xtw`)
  - New sheet: "Cenyahtoc Cintli Tonacayo - Eduardo" (ID: `1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw`, worksheet: `Eduardo`)
  - Script: `transcribe_eduardo_to_sheet.py` — pages 6–78, ToC page skipped, print artifacts stripped, Roman numeral running headers stripped
  - Result: 1,509 rows written (14 section headers in col A + 1,495 Nahuatl sentences in col B), starting at row 4
- **Designed and built `translate_and_learn.py`** — self-improving NAH→ES translation loop
  - Replaces `few_shot_translate.py` with a full learning architecture
  - **Column layout** (cols A–I):
    - E: Claude draft translation (auto)
    - F: BLEU score vs col C gold (auto)
    - G: Tlatocopa — key difference between E and C (auto, Claude)
    - H: Tlahtol Auto — generalised translation rule derived from delta (auto, Claude)
    - I: Tlahtol Human — human-corrected rule (manual, left empty for sheet editing)
  - **Dynamic few-shot**: selects top-BLEU rows from col F each run; falls back to fixed rows when no data
  - **Dynamic rules**: reads col I (human) first, then col H (auto), injects up to 10 rules into system prompt
  - **Retry logic**: exponential backoff (4 attempts, 5s/10s/20s/40s) on all network calls
  - **Sheet headers**: writes col labels to row 3 (A–I) on each run
  - JSON parsing fix: strips markdown code fences before parsing Claude's analysis response
- **Ran `translate_and_learn.py` on rows 4–488** (full gold range)
  - Script crashed at row 158 due to network reset (`ConnectionResetError 104`) → added retry logic → resumed from row 158
  - **Currently running in background** — at row ~302 of 488 as of checkpoint, ~12 min remaining
  - Cost estimate: ~$0.60–$0.80 total for full 485-row run

### Current state
- `translate_and_learn.py` is running in background — rows 4–157 complete, rows 158–488 in progress
- Crispin sheet: cols E, F, G, H filled for rows 4–157; rows 158–488 being filled now
- Eduardo sheet: col B complete (1,509 rows), cols C–I empty
- `ANTHROPIC_API_KEY` is set in Termux `~/.bashrc` — persistent across sessions
- Self-improvement loop is functional: next run will use top-BLEU rows as few-shot examples and inject col H rules into system prompt

### Next steps
1. **Wait for current run to finish** (rows 158–488, ~12 min from checkpoint)
2. **Review col H** (auto rules) in Crispin sheet — add corrections/refinements to col I where needed
3. **Re-run `translate_and_learn.py` rows 4–488** with col I populated — measure BLEU improvement
4. **Extend to rows 489–4037** — set `PROCESS_START=489`, `PROCESS_END=4038`; col C empty so only E, G, H written (no BLEU)
5. **Begin correction pass**: col E → col C for rows 489–4037 (creates NAH↔ES training pairs)
6. **Apply pipeline to Eduardo sheet** once col C is filled via translation or manual input
7. **Run `merger.py`** to produce final `dictionary.json` combining all sources (Priority 4)

### Notes
- `translate_and_learn.py` config: change `PROCESS_START` / `PROCESS_END` for different row ranges; set `OVERWRITE=True` only to reprocess already-filled rows
- BLEU scores for NAH→ES are inherently low (0.1–0.5 typical) due to word order and vocabulary differences — this is expected; use for relative ranking, not absolute quality measurement
- Col I (human rules) takes precedence over col H (auto rules) in system prompt injection — fill col I for any rules where Claude's auto-derivation is wrong or too vague
- Eduardo sheet will need the same column headers (E–I) added before running `translate_and_learn.py` on it — update `SPREADSHEET_ID` and `WORKSHEET` constants at top of script

---

## Checkpoint — 2026-06-07 (workstreams)

### Work completed this session (continued)
- **Folder cleanup** — archived superseded rule-based engine files (`grammar_rules.py`, `translator.py`, `verb_conjugator.py`, `synonyms.py`, `unknown_words.*`, `data/`, `output/`, `package*.json`, old transcription scripts, dictionary pipeline scripts, Karttunen files) to `OUT FILES/`
- **Rewrote `APP_DESIGN.md`** — updated from old rule-based schematic to current Claude API + learning loop architecture; old version archived as `OUT FILES/APP_DESIGN-5-26.md`
- **Built `extract_rules.py`** — harvests rules from col H/I of all source sheets, deduplicates, sorts human-verified first, writes to `translation_rules.json`
- **Created `translation_rules.json`** — shared cross-document rule base; populated with 479 auto-derived rules from Crispin sheet (0 human-verified as of this checkpoint)
- **Updated `translate_and_learn.py`** — now reads rules from `translation_rules.json` (shared) instead of per-sheet col H/I; falls back to per-sheet if file not found
- **Confirmed NLLB-200 compatibility** — col B (NAH) + col C (gold ES) pairs are the exact training corpus format needed; `parallel_sentences.json` (1,693 EN↔NAH pairs) ready now
- **Mapped all next workstreams** — detailed below

### Current state
- Active folder is clean: `translate_and_learn.py`, `extract_rules.py`, `translation_rules.json`, `APP_DESIGN.md`, `dictionaries/` (IDIEZ only), `parallel_sentences.json`, utility scripts
- Crispin sheet: cols E–H filled for rows 4–488 only; col I empty (no human rules yet)
  - **Actual gold range: rows 4–1,821** (~1,817 NAH↔ES pairs — previous assumption of 4–488 was wrong)
  - Rows 489–1,821: col C gold exists, col E–H empty — 1,333 rows ready for full learning
  - Rows 1,822–4,037: col C empty — skip until human fills
- Eduardo sheet: col B complete (1,512 rows); cols C–I empty; ON HOLD (user still translating manually)
- `translation_rules.json`: 479 auto rules, 0 human-verified
- Training data available now: ~1,817 NAH↔ES pairs (Crispin gold) + 1,693 EN↔NAH pairs (`parallel_sentences.json`) = ~3,510 pairs total

---

## Next Steps — Workstreams (revised 2026-06-07)

### Crispin sheet actual state

| Range | Col B | Col C | Col E–H | Action |
|-------|-------|-------|---------|--------|
| 4–488 | ✓ | ✓ Gold | ✓ Done | Re-run after A2 to apply human rules (B1) |
| **489–1,821** | ✓ | **✓ Gold** | **✗ Empty** | **Run full learning now (B3) — 1,333 rows** |
| 1,822–4,037 | ✓ | ✗ Empty | ✗ Empty | Skip until human fills col C |

---

### Workstream A — Rule Quality (Human)

| Step | Task | Owner | Dependency |
|------|------|-------|------------|
| A1 | Review Crispin col H (479 auto rules), type corrections into col I | **Human** | None — do now |
| A2 | Run `extract_rules.py` → merge col I into `translation_rules.json` | LLM | After A1 |
| A3 | Review top rules in `translation_rules.json` — flag document-specific ones | **Human** | After A2 |

**Why it matters:** 0 human-verified rules currently. Every col I entry improves all future runs on all documents.

---

### Workstream B — Crispin Training Data (Human + LLM)

| Step | Task | Owner | Dependency |
|------|------|-------|------------|
| B3 | Run `translate_and_learn.py` rows 489–1,821 — full E,F,G,H (gold exists) | LLM | **Can run NOW in parallel with A1** |
| B5 | Run `extract_rules.py` — harvest rules from rows 489–1,821 | LLM | After B3 |
| B1 | Re-run rows 4–488 with human-verified rules — measure BLEU lift | LLM | After A2 |
| B2 | Compare new vs old BLEU — confirm rule quality improvement | LLM | After B1 |
| B4 | Human correction: col E → col C for rows 1,822+ (as col C fills progressively) | **Human** | Ongoing |
| B6 | Extend `translate_and_learn.py` to newly gold-covered rows beyond 1,821 | LLM | After each B4 batch |

**Training pairs after B3:** ~1,817 gold pairs (Crispin) + 1,693 (`parallel_sentences.json`) = ~3,510 — sufficient for NLLB-200 fine-tune.

---

### Workstream C — Eduardo Sheet (ON HOLD)

Eduardo is paused — user is still filling col C manually. Do not run machine translation until user signals ready.

| Step | Task | Owner | Dependency |
|------|------|-------|------------|
| C1 | Configure `translate_and_learn.py` for Eduardo sheet | LLM | User signals ready |
| C2 | Run translation loop on Eduardo rows with gold in col C only | LLM | After C1 + A2 |
| C3 | Correction pass: col E → col C for Eduardo | **Human** | After C2 |
| C4 | Run `extract_rules.py` with Eduardo added to SOURCES | LLM | After C3 |

---

### Workstream D — NLLB-200 Fine-Tune (LLM + Compute)

| Step | Task | Owner | Dependency |
|------|------|-------|------------|
| D1 | Build training data export script (col B + col C, all sheets) | LLM | Can build now |
| D2 | Filter by BLEU col F (exclude low-quality rows) | LLM | After B3 |
| D3 | Combine with `parallel_sentences.json` (1,693 pairs) | LLM | After D1 |
| D4 | Fine-tune `facebook/nllb-200-distilled-600M` | LLM + GPU | After D3 (~3,510 pairs available after B3) |
| D5 | Evaluate fine-tuned model vs Claude API | LLM | After D4 |

**D4 can proceed after B3 completes** — ~3,510 pairs exceeds the ~1,000 minimum threshold.

---

### Workstream E — Morphological Analyzer (LLM, Long Term)

| Step | Task | Owner | Dependency |
|------|------|-------|------------|
| E1 | Build decomposer: `nitlatequitiz` → `ni + tla + tequiti + z` | LLM | None — independent |
| E2 | Wire into `translate_and_learn.py` as pre-processing step | LLM | After E1 |
| E3 | Measure vocabulary hint hit rate improvement | LLM | After E2 |

---

### Execution sequence

```
NOW (parallel) ───────────────────────────────────────────────────
  Human : A1 (col I rule corrections, Crispin)
  LLM   : B3 (Crispin rows 489–1,821 — full E,F,G,H)
  LLM   : D1 (build training export script)
  LLM   : E1 (morphological analyzer)

AFTER B3 ─────────────────────────────────────────────────────────
  LLM   : B5 (extract_rules.py, rows 489–1,821)
  LLM   : D3 → D4 (NLLB-200 fine-tune — ~3,510 pairs ready)

AFTER A1+A2 ──────────────────────────────────────────────────────
  LLM   : B1 → B2 (re-run 4–488 with human rules, measure lift)

PROGRESSIVE (human-paced) ────────────────────────────────────────
  Human : B4 (col E → col C, Crispin rows 1,822+, batch by batch)
  LLM   : B6 (extend to each new gold batch)

EDUARDO (when user signals ready) ────────────────────────────────
  LLM   : C1 → C2
  Human : C3
  LLM   : C4
```

**Immediate priority:** B3 can start now — 1,333 rows with gold, full BLEU scoring, no dependency on A1.

---

## Checkpoint — 2026-06-07 (session 2 — B3 + D1)

### Work completed this session

- **Started B3**: ran `translate_and_learn.py` on Crispin rows 489–1,821
  - Processed rows 489–768 (280 rows) before network dropout (`httpx.ConnectError — No address associated with hostname`)
  - OVERWRITE=False: all 280 completed rows are safe; resume needed from row 769
  - Script loaded 479 rules from `translation_rules.json` and top-BLEU few-shot examples (best BLEU 0.797 from rows 4–488)
- **Built `export_training_data.py`** (D1)
  - Exports NAH↔ES pairs from Crispin col B+C rows 4–1,821 and NAH↔EN pairs from `parallel_sentences.json`
  - Outputs three JSON files to `training_data/`: `nah_es_pairs.json`, `nah_en_pairs.json`, `export_summary.json`
  - Config: `BLEU_FILTER_ENABLED=False` (default), `MIN_BLEU=0.0`
  - **Note:** `parallel_sentences.json` has 282 records (not 1,693 as previously estimated) — script reports actual count at runtime
  - Not yet run — script is written and ready
- **E1 (morphological analyzer)**: attempted launch but blocked; not started

### Current state

- Crispin sheet: cols E–H filled for rows 4–488 and 489–768; rows 769–1,821 still empty
- `translation_rules.json`: 479 auto rules, 0 human-verified; rules being applied in B3
- `export_training_data.py`: written, not yet run
- `morphology.py`: not yet built

### Next steps

1. **Resume B3** — update `PROCESS_START = 769` in `translate_and_learn.py` and re-run (1,053 rows remaining)
2. **Run `export_training_data.py`** — generate training corpus to `training_data/`; verify counts
3. **Build `morphology.py`** (E1) — Nahuatl morphological decomposer to improve vocabulary hint coverage
4. **After B3 complete**: run `extract_rules.py` (B5) to harvest rules from rows 489–1,821
5. **Human (A1)**: review Crispin col H, add corrections to col I — 0 human rules is the biggest quality gap
6. **After A1**: run `extract_rules.py` (A2), then re-run rows 4–488 with human rules (B1) to measure BLEU lift
7. **After D1 confirmed**: combine with `parallel_sentences.json` (D3) → fine-tune NLLB-200 (D4)

### Notes

- B3 resume command: set `PROCESS_START = 769`, `PROCESS_END = 1822`, `OVERWRITE = False` then run
- Network dropouts are the main operational risk — retry logic handles transient failures but not full disconnects; run in Termux foreground or with a watchdog if possible
- `parallel_sentences.json` record count discrepancy (282 vs 1,693 estimated): confirm actual structure before D4 planning — the 1,693 figure may have been from an older or different version of the file
- E1 (morphology.py) is independent — can be built and tested without any sheet access

---

## Script reference — `export_training_data.py`

**Purpose:** Harvest all parallel sentence pairs built so far and package them into JSON files ready for NLLB-200 fine-tuning.

### Two data sources

1. **Crispin Google Sheet (NAH↔ES)** — reads col B (Nahuatl) + col C (Spanish gold) for rows 4–1,821. Only rows where both cells are non-empty are kept. Col F (BLEU score) is also read and stored alongside each pair, but by default the BLEU filter is **off** — every valid pair is included regardless of quality. Set `BLEU_FILTER_ENABLED = True` and `MIN_BLEU = 0.3` (or any threshold) to exclude low-quality rows.

2. **`parallel_sentences.json` (NAH↔EN)** — reads the local file. Each record needs `"nahuatl"` and `"english"` keys; records missing either are skipped.

### Three output files (written to `training_data/`)

| File | Contents |
|------|---------|
| `nah_es_pairs.json` | List of `{nahuatl, spanish, source, row, bleu}` dicts |
| `nah_en_pairs.json` | List of `{nahuatl, english, source}` dicts |
| `export_summary.json` | Counts, filter settings, timestamp |

### Auth

Uses the same OAuth `token.json` as the transcription scripts (not the service account). Auto-refreshes the token if expired.

### Key config knobs (top of file)

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATA_ROW_START` / `DATA_ROW_END` | 4 / 1821 | Which Crispin rows to pull |
| `BLEU_FILTER_ENABLED` | `False` | Enable/disable quality gate |
| `MIN_BLEU` | `0.0` | Minimum BLEU to include (only when filter enabled) |

### Current limitation

Not yet run. Once B3 finishes (rows 769–1,821), run `extract_rules.py` (B5) first, then run this script. Rows 769–1,821 will be included but with `bleu: null` until B3 fills col F for those rows.

---

## Checkpoint — 2026-06-08

### Work completed this session

- **Documented `translation_rules.json`** — explained structure and purpose for future reference

### Current state

`translation_rules.json` is a shared, cross-document rule bank injected into Claude's system prompt by `translate_and_learn.py` to improve NAH→ES translations over time.

**Structure:** Each entry contains:
- `rule` — a Spanish-language translation guideline (e.g. "Cahuitl means 'hora', not 'día'")
- `source_doc` / `source_row` — origin in the source sheet
- `bleu` — BLEU score of the source row (proxy for rule reliability)
- `human_verified` — whether confirmed via col I
- `evidence_count` — how many times the pattern appeared

**Current contents:**
- 479 rules, all auto-derived from Crispin sheet col H
- 0 human-verified rules
- BLEU range 0.0–0.797, sorted highest-first
- Topics: vocabulary clarifications (word roots, false friends), grammar patterns (prefixes, demonstratives, tense markers), Spanish output style

**How it's used:** At runtime, `translate_and_learn.py` injects up to 10 rules into the system prompt before each translation. Human-verified rules (col I → file) take precedence over auto rules. `extract_rules.py` rebuilds the file from all source sheets.

### Next steps

1. **Resume B3** — set `PROCESS_START = 769`, `PROCESS_END = 1822`, `OVERWRITE = False` and run `translate_and_learn.py` (1,053 rows remaining)
2. **Run `export_training_data.py`** — generate training corpus to `training_data/`; verify actual record counts
3. **Human (A1)** — review Crispin col H, add corrections/confirmations to col I; 0 human-verified rules is the biggest quality gap
4. **After A1**: run `extract_rules.py` (A2) to merge col I into `translation_rules.json`
5. **After B3**: run `extract_rules.py` (B5) to harvest rules from rows 489–1,821
6. **Build `morphology.py`** (E1) — independent of sheet work, can start any time

### Notes

- `parallel_sentences.json` has 282 actual records, not 1,693 as previously estimated — verify structure before D4 (NLLB-200 fine-tune) planning
- Network dropouts remain the main operational risk for long translation runs

---

## Checkpoint — 2026-06-07 (session 3 — B3 complete)

### Work completed this session

- **Resumed and completed B3**: `translate_and_learn.py` rows 769–1,821
  - Updated `PROCESS_START = 769` in `translate_and_learn.py` after previous dropout at row 768
  - Ran to completion: **1,053 rows translated, 1,052 BLEU scored, 0 skipped**
  - Cols E, F, G, H now filled for the entire Crispin gold range (rows 4–1,821)
- **B3 total coverage**: rows 4–488 (prior session) + 489–768 (session 2) + 769–1,821 (this session) = **1,817 rows complete**

### Current state

- Crispin sheet: cols E–H filled for **all 1,817 gold rows (4–1,821)** — full learning loop data in place
- `translation_rules.json`: 479 auto rules, 0 human-verified
- `translate_and_learn.py`: `PROCESS_START` currently set to 769 — reset to correct value before next run
- `export_training_data.py`: written (D1), not yet run
- `morphology.py`: not yet built (E1)
- B3 is done — B5 (extract_rules.py on rows 489–1,821) is the immediate next LLM step

### Next steps

1. **B5 — Run `extract_rules.py`** to harvest new rules from rows 489–1,821 into `translation_rules.json`
2. **Run `export_training_data.py`** (D1) to generate `training_data/` JSON files; verify actual counts
3. **Human (A1)** — review Crispin col H (all 1,817 rows), add corrections to col I; 0 human-verified rules is the biggest quality gap
4. **After A1**: run `extract_rules.py` (A2) to merge col I → `translation_rules.json`
5. **B1** — re-run rows 4–488 with human-verified rules to measure BLEU lift
6. **E1** — build `morphology.py` (independent, can start any time)
7. **D4** — fine-tune NLLB-200 once D1 data confirmed and sufficient pairs assembled

### Notes

- Before next `translate_and_learn.py` run: reset `PROCESS_START` to the correct starting row (currently 769 — will skip already-done rows due to OVERWRITE=False, but correct value avoids confusion)
- B5 is low-cost: `extract_rules.py` is a read-only sheet operation + local file write, no API calls
- After B5, `translation_rules.json` will have rules from the full 1,817-row gold corpus — significant quality improvement over the current 479-rule subset from rows 4–488 only

---

## Checkpoint — 2026-06-29

### Work completed this session

- **Session was infrastructure-only — no Nahuatl translation work done**
- **Replaced Tailscale (free trial expired) with self-hosted Headscale on the Oracle VPS**
  - Installed Headscale v0.29.1 on `finapp-vnic` (Ubuntu 22.04, `163.176.183.234`)
  - Updated `/etc/headscale/config.yaml`: `server_url` → `https://163-176-183-234.sslip.io`, `trusted_proxies` → `127.0.0.1/32`, `dns.base_domain` → `vpn.internal`
  - Created `/etc/nginx/sites-available/headscale` — nginx proxies `163-176-183-234.sslip.io:443` → `localhost:8080` (WebSocket-aware, 24h timeout)
  - Obtained a free Let's Encrypt TLS cert for `163-176-183-234.sslip.io` via certbot (auto-renews; expires 2026-09-27)
  - Created Headscale user `wilbertsmdo` (ID: 1); generated reusable pre-auth key (valid 24h from session end)
  - Headscale is running as a systemd service alongside `finapp`

### Current state

- Headscale server is live at `https://163-176-183-234.sslip.io` — no devices registered yet
- Pre-auth key generated but devices (Android/Termux + Windows laptop) not yet connected
- All Nahuatl project work items unchanged from last checkpoint (B3 complete, B5 next)

### Next steps

1. **Connect Android/Termux** — in Termux (not Claude Code): `pkg install tailscale && tailscaled & && tailscale up --login-server https://163-176-183-234.sslip.io --authkey <new-key>`
2. **Connect Windows laptop** — PowerShell (admin): `tailscale login --login-server https://163-176-183-234.sslip.io --authkey <new-key>`
3. **Verify** — on VPS: `sudo headscale nodes list` — both devices should show `100.64.x.x` addresses
4. **Generate a fresh pre-auth key** if the 24h window passed: `ssh ubuntu@163.176.183.234 -i ~/.ssh/finapp_oracle "sudo headscale preauthkeys create --user 1 --reusable --expiration 24h"`
5. **Resume Nahuatl B5** — run `extract_rules.py` to harvest rules from Crispin rows 489–1,821 into `translation_rules.json`
6. **Run `export_training_data.py`** — generate `training_data/` JSON files; verify actual record counts
7. **Human A1** — review Crispin col H, add corrections to col I (0 human-verified rules is the biggest quality gap)

### Notes

- Headscale replaces Tailscale coordination server only — Tailscale clients remain unchanged on all devices
- The `163-176-183-234.sslip.io` domain is a free DNS alias (no registration required); resolves to the VPS IP via sslip.io public DNS
- TLS cert auto-renews via certbot systemd timer — no manual action needed
- Headscale runs alongside `finapp` (gunicorn on 8000, nginx on 80/443, headscale on 8080 localhost)
- To manage Headscale: `ssh ubuntu@163.176.183.234 -i ~/.ssh/finapp_oracle "sudo headscale <command>"`

---

## Checkpoint — 2026-07-01

### Work completed this session

- **Attempted to connect Android/Termux to Headscale** — discovered `tailscale` is not in the Termux package repository; `pkg install tailscale` fails with "Unable to locate package tailscale" both from PRoot and from the Termux host shell
- **Confirmed root cause**: Tailscale has never been added to Termux's apt repo; the `!` prefix trick (Termux host shell) cannot help here
- **Decided on Play Store app** for Android side — the official Tailscale Android app supports custom coordination servers and is the correct install path for Android

### Current state

- Headscale server is live at `https://163-176-183-234.sslip.io` — no devices connected yet
- Pre-auth key generated (72h from 2026-06-29 session end); may have expired — regenerate before connecting
- Windows laptop: Tailscale installed, not yet pointed at Headscale
- Android tablet: Tailscale not yet installed; Play Store app is the path forward

### Next steps

1. **Android** — install Tailscale from Play Store; in app: account icon → "Change server" → `https://163-176-183-234.sslip.io`; log in with pre-auth key
2. **Generate fresh pre-auth key if needed**: `ssh -i ~/.ssh/finapp_oracle ubuntu@163.176.183.234 "sudo headscale preauthkeys create --user 1 --reusable --expiration 72h"`
3. **Windows** — PowerShell (admin): `tailscale logout` then `tailscale login --login-server https://163-176-183-234.sslip.io --authkey <key>`
4. **Verify both connected**: `ssh -i ~/.ssh/finapp_oracle ubuntu@163.176.183.234 "sudo headscale nodes list"`
5. **Resume Nahuatl B5** — run `extract_rules.py` to harvest rules from Crispin rows 489–1,821
6. **Run `export_training_data.py`** — generate `training_data/` JSON files
7. **Human A1** — review Crispin col H, add corrections to col I

### Notes

- Tailscale Play Store app version must be ≥ 1.80 (Headscale v0.29.1 minimum client requirement)
- In older Tailscale app versions the custom server setting may be under: three dots → Preferences → "Use custom coordination server"
- After both devices connect, SSH from tablet to laptop: `ssh wslinux@<laptop-100.64.x.x>`

---

## Checkpoint — 2026-07-02

### Work completed this session

- **Tailscale resolved** — confirmed Android tablet is already connected to Tailscale via `ws@tcp-partners.com` (tcp-partners tailnet, v1.98.2). Tablet shows as `wsmdo-tab-s10-25` at `100.96.244.82`. Headscale self-hosted setup is unnecessary — the work account covers this. Laptop (`ws-2023`, `100.68.100.23`) is currently offline/inaccessible.
- **Confirmed Crispin_Carlos sheet is complete** — ran `translate_and_learn.py` (PROCESS_START=3408, PROCESS_END=4038); all 630 rows were already filled (0 translated, 630 skipped). Col E is complete end-to-end for the Crispin_Carlos sheet (rows 4–4037).
- **Added Crispin_Carlos to `extract_rules.py` SOURCES** — added entry: sheet ID `1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg`, worksheet `Crispin`, rows 4–4037.
- **Ran `extract_rules.py`** — `translation_rules.json` grew from 479 → 5,321 rules (4,842 new: 1,325 from original Crispin rows 4–1821, 3,517 from Crispin_Carlos rows 4–4037). All auto-derived, 0 human-verified.

### Current state

- **Crispin_Carlos sheet** (`1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg`, worksheet `Crispin`): col B + col C gold complete through row 4037; col E (Claude draft) complete through row 4037; cols F/G/H filled for gold rows.
- **translation_rules.json**: 5,321 rules (all auto, 0 human-verified).
- **export_training_data.py**: still pointing at original Crispin sheet (ID `12ebNz0hxWwoXEpDcXITuRN1q9Q2dlVXwiaJd2YQWUP4`, rows 4–1821) — needs update before running.
- **B5** (extract_rules.py on original Crispin rows 489–1821) was running in a separate session at start of this session; output now merged via this session's extract_rules run.

### Next steps

1. **Update `export_training_data.py`** — change SHEET_ID to `1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg` and DATA_ROW_END to 4037; run to generate full training corpus in `training_data/`
2. **Human A1** — review Crispin_Carlos col H (auto rules), type corrections/confirmations into col I; 0 human-verified rules is the biggest remaining quality gap
3. **After A1**: run `extract_rules.py` (A2) to merge col I rules into `translation_rules.json`
4. **Re-run translate_and_learn.py rows 4–488** (B1) with human-verified rules to measure BLEU lift
5. **Eduardo sheet** — once user signals col C is sufficiently filled, configure and run `translate_and_learn.py` for Eduardo (C1–C2)
6. **NLLB-200 fine-tune (D4)** — after export_training_data.py confirms sufficient pairs, proceed with fine-tune on `facebook/nllb-200-distilled-600M`
7. **Laptop SSH** — reconnect when laptop is available; Tailscale is already working on the tablet via tcp-partners.com

### Notes

- Headscale VPS setup (`163-176-183-234.sslip.io`) is now redundant — tablet is already on a working Tailscale tailnet. Can decommission or repurpose the Headscale service on the Oracle VPS.
- `translate_and_learn.py` PROCESS_START is currently set to 3408 — reset to correct starting row before any future run.
- `parallel_sentences.json` has 282 actual records (not 1,693 as earlier estimated) — verify structure before D4 planning.
- Crispin_Carlos appears to be the definitive, most complete version of the Crispin data — treat it as the primary source going forward.

---

## Checkpoint — 2026-07-13

### Work completed this session

- **Pulled laptop commit `c15f84d`** — platform-agnostic path resolution in all 7 scripts (Termux + WSL2)
- **Added `catchup.md` skill** to `.claude/commands/` (combined catch-up + checkpoint-write) and pushed
- **Committed full architecture cleanup** — old rule-based engine (`translator.py`, `grammar_rules.py`, etc.) officially removed from git; new scripts (`translate_and_learn.py`, `extract_rules.py`, `export_training_data.py`, `morphology.py`, `count_words_colB.py`) added; `translation_rules.json` and `training_data/` committed
- **Fixed `.bashrc`** — removed stale `npm install -g google/gemini-cli@0.2.2` line that ran on every shell startup; replaced revoked `ANTHROPIC_API_KEY` with new valid key
- **Eduardo sheet setup (C1)** — wrote Crispin_Carlos column headers to Eduardo sheet row 3 (cols A–I)
- **Ran `translate_and_learn.py` on Eduardo rows 4–301** — col E (Claude draft) and BLEU filled for all rows with col C gold; SKIP/SALTAR rows handled correctly
- **Added SKIP/SALTAR skip logic** to `translate_and_learn.py` — rows with these markers in col C are skipped entirely (no translation, no BLEU, no analysis)
- **Wired `morphology.py` into `translate_and_learn.py`** (E1+E2) — `dict_hints()` now uses morphological decomposition before exact match; improves vocabulary hint coverage for agglutinative Nahuatl forms; self-test confirmed working on 10 test words
- **Set `PROCESS_END=302`** in `translate_and_learn.py` for Eduardo — content ends at row 301
- **Added Eduardo to `extract_rules.py` SOURCES** — harvested 281 new rules; `translation_rules.json` grew from 5,321 → 5,602 rules
- **Refactored `export_training_data.py`** to multi-source — added Eduardo as second NAH↔ES source; SKIP/SALTAR rows filtered out; per-source counts in summary
- **Re-ran `export_training_data.py`** — training corpus updated to **4,594 total pairs** (Crispin_Carlos: 4,030 + Eduardo: 282 + parallel_sentences: 282)
- **All changes pushed to `origin/main`** (latest: `e78d20c`)

### Current state

- `translate_and_learn.py`: configured for Eduardo (rows 4–301, PROCESS_END=302); SKIP/SALTAR aware; uses morphological dict hints
- `extract_rules.py`: SOURCES = Crispin + Crispin_Carlos + Eduardo; 5,602 auto rules, 0 human-verified
- `export_training_data.py`: multi-source (Crispin_Carlos + Eduardo); outputs to `training_data/`
- `training_data/`: 4,594 pairs — sufficient for NLLB-200 fine-tune
- Eduardo sheet: col E complete rows 4–301; col C (gold) complete rows 4–301 (288 actual, rest SKIP/SALTAR)
- `morphology.py`: fully implemented and tested; wired into translation pipeline
- `wsauto` laptop: Tailscale working via tcp-partners.com tailnet; SSH `ssh wslinux@100.68.100.23`; repo pulled to `e78d20c`

### Next steps

1. **D4 — Fine-tune `facebook/nllb-200-distilled-600M`** on `training_data/` (4,594 pairs) — needs GPU (laptop via SSH or Google Colab)
2. **A1 (Human)** — review Crispin_Carlos col H, add corrections to col I; 0 human-verified rules is the biggest quality gap
3. **A2** — after A1: run `extract_rules.py` to merge col I → `translation_rules.json`
4. **B1** — re-run `translate_and_learn.py` rows 4–488 (Crispin_Carlos) with human-verified rules; measure BLEU lift
5. **B4 (Human, ongoing)** — fill col E → col C for Crispin rows 1,822+ as reading progresses
6. **Eduardo expansion** — when more col C gold is added beyond row 301, update `PROCESS_END` and re-run

### Notes

- `translate_and_learn.py` is currently configured for Eduardo (`PROCESS_END=302`); reset `SPREADSHEET_ID`, `WORKSHEET`, `PROCESS_START`, `PROCESS_END`, `GOLD_END` before running on Crispin_Carlos again
- Two dev environments now active: tablet (Termux) and laptop (wsauto/WSL2) — always `git pull` before starting work on either
- `ANTHROPIC_API_KEY` updated in `/home/wsuser/.bashrc` — new key active
- BLEU 0.0 clusters in Eduardo run were caused by SKIP/SALTAR in col C — now filtered correctly on future runs

---

## Checkpoint — 2026-07-13 (session 2 — Sullivan pipeline + NLLB prep)

### Work completed this session

- **Scaffolded `nah_es_glossary.json`** — 8 seed entries with human-verified NAH→ES mappings (tlapannextiliztli→presentación, xihuitl→año, xochitlapohualiztli→literatura, rohuenteh→duende/ser sobrenatural, chamaniz→brotar/germinar, etc.); wired into `translate_and_learn.py` as highest-priority hint tier
- **Built Sullivan 2016 dictionary pipeline** (new source: "Tlahtolxitlauhcayotl Chicontepec" — Huasteca Nahuatl monolingual NAH→NAH dictionary, 644 pages)
  - `dictionaries/parse_sullivan.py` — downloads PDF from Drive (ID `1R4Xjxmi13GQ8Nf1hDQVAG3sx4pwEhc81`), extracts text, strips running page headers, detects entry boundaries via `UPPERCASE_HEADWORD. category.` regex, extracts panoc/achi/miaq/example sub-fields, handles disambiguation numbers (ĀAHCI1 ≠ ĀAHCI2), stores both `headword_diac` (with macrons) and `headword_norm` (stripped, no digits) per entry
  - Output `raw_sullivan.json`: 9,782 main entries + 238 xiquitta cross-refs across 9,483 unique headword keys
  - Category breakdown: tlat 3,970 | tlach3 2,359 | tlach2 1,976 | tlach1 937 | pil 233 | tlaeli 132 | tlaten 85 | tlach 45 | tlach4 45
  - Field coverage: example 82.3% | achi 88.1% | panoc 46.1% | miaq 8.1%
  - `dictionaries/normalize_sullivan.py` — converts raw JSON into same schema as `dictionary_idiez.json` (keyed by `headword_norm`, `definitions[{"es": "", "nah": <Nahuatl body>}]`); `es` field left empty as placeholder for future enrichment; xrefs written to `normalized_sullivan_xref.json`
  - Output `normalized_sullivan.json`: 9,782 main entries across 9,250 unique keys; `normalized_sullivan_xref.json`: 235 cross-reference redirects
- **Wired Sullivan into `translate_and_learn.py`** as third hint tier
  - Added `SULLIVAN_PATH`, `load_sullivan()`, `sullivan_hints()` (uses `morphology.decompose()` for fuzzy match)
  - Hint priority order in each translation prompt:
    1. `[Glosario verificado]` — human-verified Spanish terms (highest)
    2. `[Diccionario IDIEZ]` — IDIEZ Spanish definitions via morphological decomposition
    3. `[Sullivan 2016 — Huasteca Nahuatl]` — Sullivan Nahuatl-definition body (new)
  - Sullivan returns up to 4 hints per sentence; provides Nahuatl-language context Claude can read
- **Committed all Sullivan pipeline files** to `origin/main` (commit `8678b6c`)

### Current state

- Sullivan 2016 fully parsed and wired in as supplementary hint source
- `normalized_sullivan.json`: 9,782 entries; `es` fields empty (ready for enrichment step)
- Hint stack in `translate_and_learn.py`: Glossary → IDIEZ → Sullivan (three tiers)
- `translate_and_learn.py` still configured for Eduardo (`PROCESS_END=302`); must reconfigure for Crispin_Carlos before next Crispin run
- Training corpus: 4,594 pairs in `training_data/` — sufficient for NLLB-200 fine-tune

### Next steps

#### Immediate — laptop fine-tuning setup (D4)

The laptop (WSL2, `ssh wslinux@100.68.100.23`) needs to be prepared for NLLB-200 fine-tuning. Do these steps in order:

**Step 0 — git pull (on laptop)**
```bash
cd ~/path/to/Nahuatl_Translator2 && git pull origin main
```
Ensures `training_data/nah_es_pairs.json` (4,312 pairs) is present.

**Step 1 — Check GPU**
```bash
python3 -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```
If `False`: use Google Colab (free T4 GPU) instead — upload `training_data/nah_es_pairs.json` to Drive and run the notebook there.

**Step 2 — Install packages (WSL2)**
```bash
pip install transformers datasets accelerate sentencepiece sacrebleu
pip install torch --index-url https://download.pytorch.org/whl/cu118   # CUDA GPU
# OR: pip install torch                                                  # CPU-only (very slow)
```

**Step 3 — Data prep script** — create `prep_training_data.py`:
```python
from datasets import Dataset
import json, os

with open("training_data/nah_es_pairs.json") as f:
    pairs = json.load(f)

records = [{"src": p["nahuatl"], "tgt": p["spanish"]} for p in pairs]
n_val = int(len(records) * 0.1)          # 90% train, 10% val
ds_train = Dataset.from_list(records[n_val:])
ds_val   = Dataset.from_list(records[:n_val])
ds_train.save_to_disk("training_data/hf_train")
ds_val.save_to_disk("training_data/hf_val")
print(f"Train: {len(ds_train)}, Val: {len(ds_val)}")
```

**Step 4 — Fine-tune script** — create `finetune_nllb.py`:
```python
from transformers import (
    NllbTokenizer, AutoModelForSeq2SeqLM,
    Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
)
from datasets import load_from_disk

MODEL_NAME = "facebook/nllb-200-distilled-600M"
SRC_LANG, TGT_LANG = "nah_Latn", "spa_Latn"

tokenizer = NllbTokenizer.from_pretrained(MODEL_NAME, src_lang=SRC_LANG, tgt_lang=TGT_LANG)
model     = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

ds_train = load_from_disk("training_data/hf_train")
ds_val   = load_from_disk("training_data/hf_val")

def tokenize(batch):
    inputs = tokenizer(batch["src"], max_length=128, truncation=True, padding="max_length")
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(batch["tgt"], max_length=128, truncation=True, padding="max_length")
    inputs["labels"] = labels["input_ids"]
    return inputs

ds_train = ds_train.map(tokenize, batched=True, remove_columns=["src", "tgt"])
ds_val   = ds_val.map(tokenize, batched=True, remove_columns=["src", "tgt"])

args = Seq2SeqTrainingArguments(
    output_dir="models/nllb-nah-es",
    num_train_epochs=10,            # small dataset → more epochs
    per_device_train_batch_size=8,  # lower to 4 if CUDA OOM
    warmup_steps=100,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,    # early stopping via best checkpoint
    predict_with_generate=True,
    fp16=True,                      # GPU only — remove if CPU
    logging_steps=50,
)

trainer = Seq2SeqTrainer(
    model=model, args=args,
    train_dataset=ds_train, eval_dataset=ds_val,
    tokenizer=tokenizer,
    data_collator=DataCollatorForSeq2Seq(tokenizer, model),
)
trainer.train()
trainer.save_model("models/nllb-nah-es-final")
print("Saved to models/nllb-nah-es-final")
```

**Step 5 — Run**
```bash
python3 prep_training_data.py   # one-time data prep
python3 finetune_nllb.py        # ~30-60 min GPU / ~8-12 hrs CPU
```

**Step 6 — Test inference**
```python
from transformers import pipeline
pipe = pipeline("translation", model="models/nllb-nah-es-final",
                src_lang="nah_Latn", tgt_lang="spa_Latn")
print(pipe("Niaacalacqui quemman tiyahqueh atlauhco")[0]["translation_text"])
```

**Key notes for D4:**
- `nah_Latn` is NOT in vanilla NLLB-200's 200 languages — fine-tuning teaches it from scratch; this is expected and fine
- 4,594 pairs is "very low resource" territory — expect improvement over vanilla NLLB but not production quality; goal is proof of concept + BLEU baseline
- If CUDA OOM: lower `per_device_train_batch_size` from 8 → 4 → 2
- `load_best_model_at_end=True` guards against overfitting on small dataset
- If no GPU on laptop: use Google Colab free T4 (upload `nah_es_pairs.json` to Drive, run same script in notebook)

#### Other next steps (after laptop D4)

2. **Karttunen pipeline** — parse Karttunen dictionary as secondary classical Nahuatl fallback (planned for later this week)
3. **enrich_sullivan.py** — call Claude to translate Sullivan Nahuatl definitions → Spanish, filling `es` fields; makes Sullivan queryable via `morphology.py`
4. **A1 (Human)** — review Crispin_Carlos col H, add corrections to col I; 0 human-verified rules remains the biggest quality gap
5. **A2** — after A1: run `extract_rules.py` to merge col I → `translation_rules.json`
6. **B1** — re-run rows 4–488 with human-verified rules; measure BLEU lift
7. **Reset `translate_and_learn.py`** to Crispin_Carlos config before next Crispin run

### Notes

- Sullivan is a Huasteca Nahuatl monolingual dictionary (NAH→NAH) — same dialect as IDIEZ, high value for vocabulary coverage; xiquitta entries are cross-references ("see also"), not errors
- `normalized_sullivan.json` is schema-compatible with `dictionary_idiez.json` but `es` fields are empty until enriched — not yet queryable via `morphology.py.get_hints()`; wired separately via `sullivan_hints()` in `translate_and_learn.py`
- Karttunen is classical Nahuatl (NAH→EN), structurally different from IDIEZ/Sullivan; use as tertiary fallback only for words not found in the other two sources
- Two dev environments active: tablet (Termux, primary) and laptop (wsauto/wslinux, WSL2) — always `git pull` before starting work on either

---

## Checkpoint — 2026-07-13 (session 3 — remote laptop access confirmed)

### Work completed this session

- **Fixed SSH key path issue** — `finapp_oracle` key existed in Termux native home (`/data/data/com.termux/files/home/.ssh/`) but not in PRoot home (`/home/wsuser/.ssh/`); copied key + set `chmod 600`; VPS SSH now works from PRoot session
- **Confirmed Oracle VPS live** — `ssh -i ~/.ssh/finapp_oracle ubuntu@163.176.183.234` connects; Headscale v0.29.1 running; generated fresh pre-auth key (72h); no nodes currently registered on Headscale
- **Confirmed tcp-partners.com Tailscale still active** — tablet (`wsmdo-tab-s10-25`, `100.96.244.82`) and laptop (`ws-2023`, `100.68.100.23`) both showing green/online; Headscale unnecessary while this tailnet is active
- **Fixed WSL2 SSH not auto-starting** — added `[boot] command = service ssh start` to `/etc/wsl.conf` on laptop; WSL2 SSH now starts automatically on every Windows boot
- **Enabled Windows OpenSSH Server as backup** — installed via `Add-WindowsCapability`, set `Startup=Automatic`; reachable at `100.99.213.23` (`ws-2023-1`) as fallback if WSL2 SSH is down
- **Disabled Windows sleep** — `powercfg /change standby-timeout-ac 0` so laptop stays reachable on AC power
- **Confirmed end-to-end remote access** — `ssh wslinux@100.68.100.23` from native Termux connects successfully to `wslinux@ws-2023`; Ubuntu 24.04.4 LTS WSL2; 1TB disk, 3% memory, load 0.0

### Current state

- **Remote laptop access: fully working** — from tablet Termux: `ssh wslinux@100.68.100.23`
- Laptop is ready for NLLB-200 fine-tuning (D4)
- Laptop WSL2 SSH auto-starts; Windows OpenSSH at `100.99.213.23` as backup
- All Nahuatl pipeline code is at `fe907b4` on `origin/main` — needs `git pull` on laptop before starting D4

### Next steps — laptop (D4, do remotely via SSH)

**From tablet Termux, SSH to laptop first:**
```bash
ssh wslinux@100.68.100.23
```

**Then on laptop WSL2:**

```bash
# 1. Pull latest code
cd /path/to/Nahuatl_Translator2   # find with: find ~ -name "Nahuatl_Translator2" -type d
git pull origin main

# 2. Check GPU
python3 -c "import torch; print(torch.cuda.is_available())"

# 3. Install packages (if not already installed)
pip install transformers datasets accelerate sentencepiece sacrebleu
pip install torch --index-url https://download.pytorch.org/whl/cu118   # CUDA
# or: pip install torch   (CPU-only)

# 4. Prep data
python3 prep_training_data.py

# 5. Fine-tune (~30-60 min GPU)
python3 finetune_nllb.py
```

Both scripts (`prep_training_data.py` and `finetune_nllb.py`) are written out in full in the previous checkpoint — copy from plan into files on the laptop, then run.

**Fallback if no GPU:** upload `training_data/nah_es_pairs.json` to Google Drive, run in Google Colab (free T4).

### Next steps — tablet (parallel, this week)

1. **Karttunen pipeline** — parse Karttunen dictionary (classical NAH→EN fallback)
2. **A1 (Human)** — review Crispin_Carlos col H, add corrections to col I
3. **enrich_sullivan.py** — translate Sullivan NAH definitions → Spanish via Claude API

### Notes

- SSH key now in both Termux native (`/data/data/com.termux/files/home/.ssh/`) and PRoot (`/home/wsuser/.ssh/`) — no more path mismatch
- Tailscale via tcp-partners.com is the primary VPN; Headscale on Oracle VPS is standby if tcp-partners access is ever revoked
- Laptop username in WSL2: `wslinux`; Windows SSH backup: `ws@100.99.213.23` (use Windows login name)
- `ws-2023` (`100.68.100.23`) = WSL2 Tailscale node; `ws-2023-1` (`100.99.213.23`) = Windows Tailscale node

---

## Checkpoint — 2026-07-13 (session 4 — D4 environment ready, paused)

### Work completed this session

- **Confirmed NVIDIA GPU in laptop WSL2** — `/usr/lib/wsl/lib/` contains CUDA libs (driver version 580.91, CUDA 12.x capable); `nvidia-smi` binary present at `/usr/lib/wsl/lib/nvidia-smi`; GPU accessible through WSL2 pass-through
- **Created Python virtual environment on laptop** — `python3 -m venv ~/nllb-env` at `wslinux@ws-2023`; activated via `source ~/nllb-env/bin/activate`
- **Installed all training dependencies on laptop** (inside `~/nllb-env`):
  - `torch` + `torchvision` — PyTorch with CUDA 12.1 (`--index-url https://download.pytorch.org/whl/cu121`)
  - `transformers` — HuggingFace model library
  - `datasets` — HuggingFace dataset tools
  - `accelerate` — distributed/mixed-precision training
  - `sentencepiece` — tokenizer dependency for NLLB
  - `sacrebleu` — BLEU evaluation
  - Note: required `--break-system-packages` flag was NOT needed since venv was used; Ubuntu 24.04 blocks system-wide pip installs (PEP 668)
- **Verified PyTorch + GPU** — `python3 -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"` confirmed `True` and GPU name
- **Written and committed training scripts** (commit `dd7919e`):
  - `prep_training_data.py` — loads `training_data/nah_es_pairs.json`, 90/10 train/val split, saves HuggingFace arrow datasets to `training_data/hf_train/` and `training_data/hf_val/`
  - `finetune_nllb.py` — fine-tunes `facebook/nllb-200-distilled-600M`, 10 epochs, fp16 on GPU, saves best checkpoint to `models/nllb-nah-es-final/`, runs 3-sentence inference test on completion
- **Git pulled `dd7919e` on laptop** — both scripts present and ready to run

### Current state — D4 is ready to run

Everything is installed and in place on the laptop. The next action is to run 2 commands:

```bash
# On laptop WSL2 — activate env first every session
source ~/nllb-env/bin/activate
cd ~/path/to/Nahuatl_Translator2    # find with: find ~ -name "Nahuatl_Translator2" -type d

# Step 1 — prep data (run once, ~10 seconds)
python3 prep_training_data.py

# Step 2 — fine-tune (~30-60 min on GPU)
python3 finetune_nllb.py
```

Output lands in `models/nllb-nah-es-final/`. Script prints loss per 50 steps, saves checkpoint per epoch, and runs a 3-sentence inference test at the end.

### Laptop environment summary

| Item | Value |
|------|-------|
| Machine | `ws-2023`, Windows laptop, WSL2 |
| WSL2 distro | Ubuntu 24.04.4 LTS |
| Disk | 1006 GB (3.1% used) |
| GPU driver | NVIDIA 580.91 (CUDA 12.x) |
| Python venv | `~/nllb-env` (activate before every session) |
| PyTorch | CUDA 12.1 build (`cu121`) |
| SSH from tablet | `ssh wslinux@100.68.100.23` (Tailscale tcp-partners.com) |
| Backup SSH | `ssh ws@100.99.213.23` (Windows OpenSSH) |
| Repo location | find with `find ~ -name "Nahuatl_Translator2" -type d` |

### If CUDA OOM during training

Edit `finetune_nllb.py` and lower batch size:
```python
per_device_train_batch_size=4   # was 8 — try 4, then 2
per_device_eval_batch_size=4
```

### Next steps (resuming)

1. **D4 — Run training on laptop** (immediate — everything ready):
   ```bash
   source ~/nllb-env/bin/activate
   cd <repo>
   python3 prep_training_data.py && python3 finetune_nllb.py
   ```
2. **D5** — After training: evaluate fine-tuned model vs Claude API baseline on a held-out set; compare BLEU scores
3. **Karttunen pipeline** — parse Karttunen dictionary (classical NAH→EN fallback) — tablet work, independent of D4
4. **enrich_sullivan.py** — translate Sullivan NAH definitions → Spanish via Claude API, filling empty `es` fields
5. **A1 (Human)** — review Crispin_Carlos col H, add corrections to col I; 0 human-verified rules remains biggest quality gap

### Notes

- `finetune_nllb.py` uses `nah_Latn` as source language code — this is NOT in NLLB-200's native 200 languages; fine-tuning teaches it from scratch, which is expected and correct
- 4,594 pairs is low-resource territory; expect measurable BLEU improvement over vanilla NLLB but not production quality; this is a proof-of-concept baseline run
- `load_best_model_at_end=True` in training args provides automatic early-stopping protection against overfitting
- After D4 completes, commit `models/nllb-nah-es-final/` to a separate branch or store separately — model files are large (~1.2GB) and should not go into main git history

---

## Checkpoint — 2026-07-10

### Work completed this session
- **Caught up on project state** — reviewed full project plan; confirmed `few_shot_translate.py` is complete and was the last deliverable (session 4)
- **Diagnosed environment mismatch** — confirmed we are now running on WSL2 Linux (`/home/wslinux/...`), not Termux/Android; previous scripts and paths are Termux-specific and need updating
- **Identified missing dependency**: `anthropic` package not installed on WSL2 system (`pip3 install anthropic gspread google-auth google-auth-oauthlib` needed)
- **Identified missing credential**: `token.json` (OAuth) only exists on Android device — not synced to WSL2; service account auth is the cleaner alternative for this system
- **Confirmed dictionary is present**: `dictionaries/enriched_idiez.json` exists on WSL2 at correct path
- **API key confirmed set** by user (not in environment file yet)

### Current state
- `few_shot_translate.py` is written and logically complete but cannot run on this system yet
- Two blockers: (1) packages not installed, (2) `token.json` missing — auth section needs to be rewritten to use service account instead of OAuth
- `enriched_idiez.json` (dictionary for NAH→ES hints) is present and accessible
- Crispin sheet: 4,036 rows; col B complete; col C done rows 4–488; col E empty

### Next steps

#### Step 1 — Install packages (one-time, WSL2)
```bash
pip3 install anthropic gspread google-auth google-auth-oauthlib
```
Verify:
```bash
python3 -c "import anthropic, gspread, google.oauth2; print('OK')"
```

#### Step 2 — Get service_account.json onto this machine
The file was on Android at:
`/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json`

Option A — copy from Android over USB/file manager to:
`/home/wslinux/WS_Qwen_Projects_Windows/Financial_Analysis_App/python/service_account.json`

Option B — re-download from Google Cloud Console:
- Go to console.cloud.google.com → project `qwen-project-492821`
- IAM & Admin → Service Accounts → `ws-financial-analysis@qwen-project-492821.iam.gserviceaccount.com`
- Keys → Add Key → JSON → save to path above

#### Step 3 — Edit `few_shot_translate.py` (exact changes)

**3a. Replace lines 14–15** (OAuth imports) with service account import:
```python
# OLD (delete these two lines):
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# NEW (replace with):
from google.oauth2.service_account import Credentials
```

**3b. Replace line 20** (TOKEN_PATH) with SA_PATH:
```python
# OLD:
TOKEN_PATH     = "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json"

# NEW:
SA_PATH        = "/home/wslinux/WS_Qwen_Projects_Windows/Financial_Analysis_App/python/service_account.json"
```

**3c. Replace line 22** (DICT_PATH):
```python
# OLD:
DICT_PATH      = "/storage/self/primary/PY_Projects/Nahuatl_Translator2/dictionaries/enriched_idiez.json"

# NEW:
DICT_PATH      = "/home/wslinux/WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator/dictionaries/enriched_idiez.json"
```

**3d. Replace the entire `get_worksheet()` function** (lines 32–47):
```python
# OLD:
def get_worksheet():
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
    sh = gc.open_by_key(SPREADSHEET_ID)
    return sh.worksheet("Crispin")

# NEW (service account — no OAuth dance, no token refresh):
def get_worksheet():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(SA_PATH, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    return sh.worksheet("Crispin")
```

**3e. Update the docstring** at line 10:
```python
# OLD:
    /data/data/com.termux/files/usr/bin/python3 few_shot_translate.py

# NEW:
    python3 few_shot_translate.py
```

#### Step 4 — Persist API key
```bash
echo 'export ANTHROPIC_API_KEY=sk-ant-api03-...' >> ~/.bashrc
source ~/.bashrc
```

#### Step 5 — Run the 10-row test
```bash
cd /home/wslinux/WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator
python3 few_shot_translate.py
```
Expected output: 10 rows printed side-by-side (NAH / GOLD / CLAUDE), then "Done — 10/10 rows written to col E."
Open the Google Sheet and compare col C vs col E for rows 15–24.

#### Step 6 — If quality is acceptable, extend to full gold range
In `few_shot_translate.py`, change lines 26–27:
```python
# Change TEST_ROWS to cover all gold rows:
TEST_ROWS = list(range(15, 489))   # rows 15–488 (col C has gold Spanish)
```
Re-run. This fills col E for ~474 rows — compare against col C to measure baseline error rate.

#### Step 7 — Extend to pending rows (no gold)
```python
TEST_ROWS = list(range(489, 4037))   # rows 489–4036 (no gold — filling col E only)
```
This is the full auto-translation batch (~3,548 rows). Estimated cost: ~$0.05–0.10 with haiku-4-5.

#### Step 8 — Correction pass (creates training data)
Go through col E row by row; for each acceptable translation copy/edit it into col C.
Col C = final gold = training data for NLLB-200 fine-tune.

### Notes
- Service account email: `ws-financial-analysis@qwen-project-492821.iam.gserviceaccount.com`
- Spreadsheet must be shared with that email as Editor (already done from prior sessions)
- `ANTHROPIC_API_KEY` must be set in shell before running — add to `~/.bashrc` for persistence
- Model is `claude-haiku-4-5` for cost efficiency — switch to `claude-sonnet-4-6` at line 23 if quality is too low
- Dict lookup is exact-token match — agglutinated Nahuatl words will mostly miss; still helps for standalone roots
## Checkpoint — 2026-07-14 (architecture review session)

### Work completed this session

- **No code written this session** — conceptual/architecture review only
- **Reviewed `prep_training_data.py` and `finetune_nllb.py`** — explained how each script works: prep splits 4,594 pairs 90/10 into HuggingFace Arrow datasets; finetune loads NLLB-200-distilled-600M, tokenizes, trains 10 epochs with fp16 + best-checkpoint saving, runs 3-sentence inference test on completion
- **Compared NLLB-200 vs Claude API** — key finding: NLLB is a pure seq2seq pattern-matcher (input = raw sentence only); Claude is an instruction-follower that reads rules, dictionary hints, and few-shot examples in-context; quality gap is large in Claude's favour; NLLB value is as a free/offline bulk translator and proof-of-concept baseline
- **Explained why NLLB cannot use dictionary/rule injection** — architectural: NLLB was trained on source→target pairs only, has no instruction-following capability; injecting rules into input would cause it to translate the rules, not apply them; would require retraining with rules baked into input format (lexically constrained decoding — a different project)
- **Designed Ollama + LLaMA 3.1 8B as the autonomy upgrade path** — local instruction-following model that supports rules/hints/few-shot exactly like Claude; runs on laptop GPU (4–5 GB VRAM in 4-bit); only ~10 lines of code change in `translate_and_learn.py` to swap Anthropic client for Ollama HTTP call; quality: between NLLB and Claude
- **Designed NLLB + LLaMA cascade architecture** — two complementary roles:
  1. NLLB produces fast rough draft (~0.05 sec, free)
  2. LLaMA refines draft using rules + dictionary hints (instead of translating cold)
  Combined pipeline: morphology decompose → IDIEZ/Sullivan/Glossary hints → NLLB draft → LLaMA refinement → final Spanish
- **Identified NLLB as enrichment tool for Sullivan** — NLLB can fill the 9,782 empty `es` fields in `normalized_sullivan.json` cheaply and fast (word/phrase level translation); this is the `enrich_sullivan.py` task and NLLB is well-suited for it
- **Designed VPS deployment path** — Oracle VPS (Ubuntu 22.04, nginx already configured, 24GB ARM RAM) can host a 7B model in CPU inference mode (~20–60 sec/sentence); GPU VPS (RunPod/Vast.ai, ~$0.30–0.50/hr) for faster inference; HuggingFace private repo for sharing model weights and enabling collaborative sequential fine-tuning

### Current state

- All code unchanged from session 4 (2026-07-13) — D4 is still ready to run on laptop, nothing has been modified
- Architecture direction is now decided:
  - **Short term**: run D4 (NLLB fine-tune) on laptop as baseline
  - **Medium term**: add Ollama + LLaMA 3.1 8B as the autonomous high-quality path, using NLLB draft as first-pass input
  - **Long term**: VPS deployment for collaborative use; HuggingFace Hub for model weight sharing
- `enrich_sullivan.py` (filling Sullivan `es` fields) now has a clearer implementation path: use fine-tuned NLLB for word-level translation, fast and free

### Next steps

1. **D4 — Run NLLB fine-tune on laptop** (immediate — everything ready):
   ```bash
   ssh wslinux@100.68.100.23
   source ~/nllb-env/bin/activate
   cd <repo>   # find with: find ~ -name "Nahuatl_Translator2" -type d
   python3 prep_training_data.py && python3 finetune_nllb.py
   ```
2. **D5** — Evaluate fine-tuned NLLB vs Claude API on held-out sentences; record BLEU scores
3. **Install Ollama on laptop** — `curl -fsSL https://ollama.ai/install.sh | sh` in WSL2; pull `ollama pull llama3.1:8b`
4. **Swap `translate_and_learn.py` client** — replace Anthropic API call with Ollama HTTP endpoint; test on 10 Crispin rows
5. **Build cascade** — wire NLLB output as `rough_draft` field injected into LLaMA prompt; measure quality vs LLaMA alone
6. **`enrich_sullivan.py`** — use fine-tuned NLLB to translate Sullivan NAH definitions → Spanish, filling `es` fields in `normalized_sullivan.json`
7. **A1 (Human)** — review Crispin_Carlos col H, add corrections to col I; 0 human-verified rules remains the biggest quality gap

### Notes

- Ollama client swap in `translate_and_learn.py` is minimal: replace `anthropic.Anthropic()` with `requests.post("http://localhost:11434/api/chat", ...)` — same prompt structure works unchanged
- For VPS CPU inference: 7B model at 4-bit quantization needs ~5 GB RAM; Oracle free tier (24 GB ARM) is sufficient; inference will be slow but usable for low-traffic collaborative work
- HuggingFace Hub private repo is free up to 10 GB — sufficient for a 7B model in 4-bit (~4 GB) or NLLB-600M (~2.4 GB)
- Sequential fine-tuning workflow: person A fine-tunes → pushes to HF Hub → person B pulls, adds data, fine-tunes further → pushes back; no simultaneous training coordination needed
- NLLB enrichment of Sullivan (`enrich_sullivan.py`) unlocks Sullivan as a full dictionary source for `morphology.py.get_hints()` — currently Sullivan is wired separately via `sullivan_hints()` because `es` fields are empty

---

## Checkpoint — 2026-08-07

### Work completed this session

- **Session was orientation/planning only — no code written**
- **Ran `/catchup`** — rebuilt full project context from memory, project plan, and git log
- **Reviewed workstream tables** (A–E) — confirmed current status of each step
- **Attempted D4 laptop SSH** — `ssh wslinux@100.68.100.23` timed out; backup `ssh ws@100.99.213.23` also unreachable; laptop is off or Tailscale disconnected

### Current state

- D4 (NLLB fine-tune) is fully prepared and blocked only by laptop availability: venv `~/nllb-env` installed, `prep_training_data.py` + `finetune_nllb.py` committed, training corpus at 4,594 pairs
- All pipeline code unchanged since 2026-07-13 session 4 (commit `f943c90`)
- Untracked files in repo: `dictionaries/compare_sullivan_idiez.py`, `normalized_sullivan_enriched.json`, `dictionaries/sources/sullivan_2016.pdf`, `sullivan_pending_enrichment.json` — not yet committed

### Next steps

1. **D4 — Run NLLB fine-tune on laptop** (first priority — everything ready, just needs laptop online):
   ```bash
   ssh wslinux@100.68.100.23        # or backup: ssh ws@100.99.213.23
   source ~/nllb-env/bin/activate
   cd $(find ~ -name "Nahuatl_Translator2" -type d | head -1)
   git pull origin main
   tmux new -s d4                   # run inside tmux so SSH drop won't kill it
   python3 prep_training_data.py && python3 finetune_nllb.py
   ```
2. **D5** — After training: evaluate fine-tuned NLLB vs Claude API on held-out sentences; record BLEU
3. **enrich_sullivan.py** — use fine-tuned NLLB to fill 9,782 empty `es` fields in `normalized_sullivan.json`
4. **Install Ollama + LLaMA 3.1 8B on laptop** — swap `translate_and_learn.py` client; test on 10 Crispin rows
5. **A1 (Human)** — review Crispin_Carlos col H auto rules; type corrections into col I (0 human-verified rules is the biggest quality gap)
6. **Commit untracked files** — review and commit `compare_sullivan_idiez.py`, `normalized_sullivan_enriched.json`, `sullivan_pending_enrichment.json`

### Notes

- Laptop SSH (`100.68.100.23`) was unreachable — check Tailscale status and that Windows sleep is still disabled (`powercfg /change standby-timeout-ac 0`)
- `finetune_nllb.py` should be run inside `tmux` to survive SSH disconnects
- If CUDA OOM: lower `per_device_train_batch_size` from 8 → 4 in `finetune_nllb.py`
- Model output goes to `models/nllb-nah-es-final/` — do NOT commit to main (large files ~1.2 GB); store on a separate branch or HuggingFace Hub

---

### Full session context — 2026-07-14

#### How `prep_training_data.py` works

The script's only job is to convert `training_data/nah_es_pairs.json` into a format the trainer can read quickly.

**What it reads:** `training_data/nah_es_pairs.json` — each record is `{"nahuatl": "...", "spanish": "..."}`.

**What it does:**
1. Loads 4,594 pairs and drops any where either field is empty
2. Splits into two groups:
   - 90% → training set (~4,134 pairs) — the model learns from these
   - 10% → validation set (~460 pairs) — used to check if learning is working, never trained on
3. Saves both in HuggingFace Arrow binary format to `training_data/hf_train/` and `training_data/hf_val/`

**Why the split?** If you train on 100% of the data with no holdout, you can't tell whether the model is genuinely learning translation or just memorizing your specific examples. The 10% it never sees lets you catch overfitting.

---

#### How `finetune_nllb.py` works

Takes the pre-trained NLLB-200-distilled-600M model (Meta, trained on 200 languages) and adjusts it specifically for Nahuatl ↔ Spanish.

**Step 1 — Load the base model**
`facebook/nllb-200-distilled-600M` already understands Spanish well. It does not know Nahuatl — `nah_Latn` is not in its original 200 languages. Fine-tuning teaches it Nahuatl by showing it examples. "Distilled-600M" = smaller/faster version (600M parameters vs the full 3.3B).

**Step 2 — Tokenization**
A model can't read text — it reads numbers. The tokenizer converts each sentence into integer IDs (one per word-piece). `max_length=128` means sentences longer than 128 tokens get cut off — fine for most Nahuatl sentences.

**Step 3 — Training loop**

| Setting | What it means |
|---------|--------------|
| `num_train_epochs=10` | Goes through all ~4,134 training pairs 10 times |
| `batch_size=8` | Shows 8 pairs at a time, adjusts weights after each batch |
| `warmup_steps=100` | Starts with a very small learning rate, ramps up — prevents wild early adjustments |
| `fp16=True` | Uses 16-bit math on GPU — twice as fast, half the memory |
| `evaluation_strategy="epoch"` | After each epoch, tests on the 460 validation pairs |
| `load_best_model_at_end=True` | Keeps the best-validation checkpoint, not the last one — guards against overfitting |

**How one training step works:**
1. Model sees a Nahuatl sentence
2. Tries to produce the Spanish translation
3. Compares output to the correct answer — calculates error ("loss")
4. Adjusts internal weights slightly to reduce that error
5. Repeat ~51,000 times (4,134 pairs × 10 epochs ÷ 8 per batch)

**Step 4 — Save + test**
Best checkpoint saved to `models/nllb-nah-es-final/`. Then 3 test sentences run immediately to confirm the model produces output.

**Fine-tuning vs training from scratch:**

| | From scratch | Fine-tuning |
|--|--|--|
| Starting point | Random weights | NLLB-200 already trained on 200 languages |
| Data needed | Millions of examples | Hundreds to thousands is enough |
| Time | Weeks on many GPUs | 30–60 min on one GPU |
| Spanish knowledge | Must be learned | Already built-in |
| Nahuatl | Must be learned | Learned from your 4,594 pairs |

The model already knows how to translate — it knows grammar, word order, sentence structure from 200 other languages. Fine-tuning teaches it Nahuatl vocabulary and patterns on top of that foundation.

**Full pipeline:**
```
nah_es_pairs.json (4,594 pairs)
        │
        ▼
prep_training_data.py
        ├── hf_train/ (4,134 pairs, 90%)
        └── hf_val/   (  460 pairs, 10%)
                │
                ▼
        finetune_nllb.py
                ├── Downloads NLLB-200-distilled-600M
                ├── Converts text → token IDs
                ├── 10 epochs of training on hf_train
                ├── Validates after each epoch on hf_val
                └── Saves best checkpoint
                        │
                        ▼
                models/nllb-nah-es-final/
```

---

#### NLLB-200 vs Claude API — comparison

**The current Claude approach (`translate_and_learn.py`)** gives Claude a rich context package per sentence:
```
System prompt
 + up to 10 translation rules (from translation_rules.json)
 + 5–8 few-shot examples (highest-BLEU rows from sheet)
 + Glossary hints (human-verified terms)
 + IDIEZ dictionary hints (Spanish definitions)
 + Sullivan hints (Nahuatl definitions)
→ "Translate this sentence: ..."
```
Claude is also ~100–200B parameters of general language understanding. It can reason about context, handle unseen words by analogy, and notice discourse cues (dialogue vs. narration).

**The NLLB-200 fine-tuned approach** receives only the raw Nahuatl sentence. No rules, no dictionary hints, no examples. 600M parameters. Pure sequence-to-sequence pattern matching.

| Factor | Claude API | NLLB fine-tuned |
|--------|-----------|-----------------|
| Translation quality | Much higher | Noticeably lower |
| Cost per sentence | ~$0.00002–0.0001 | Free after training |
| Speed | ~1–3 sec (API call) | ~0.05 sec (local) |
| Dictionary awareness | Yes — IDIEZ + Sullivan + Glossary | No |
| Rule injection | Yes — 5,602 rules per call | No |
| Self-improving | Yes — derives new rules each run | No — static |
| Unknown word handling | Good — reasons by analogy | Poor |
| Requires internet | Yes | No |
| Scales to 10,000 sentences | $0.50–2.00 | Free |

**NLLB's legitimate use cases in this project:**
1. Proof of concept — confirm a seq2seq model can learn something from the data
2. Cheap bulk first pass — translate 10,000 sentences free, then correct only the bad ones
3. Baseline to beat — concrete BLEU number to optimize against as data grows

---

#### Why NLLB cannot use dictionary/rule injection

The answer is architectural. Claude was trained on a prompt → response format where the input can contain anything — rules, examples, context, definitions. It learned to read and apply natural language guidance. This is called **in-context learning**.

NLLB is a **sequence-to-sequence** model. Its entire training was: `input: Nahuatl sentence` → `output: Spanish sentence`. Millions of times across 200 languages. It was never trained to read rules, follow instructions, or use external definitions. If you put rules in the input, it would try to **translate the rules into Spanish**, not apply them.

Its knowledge is frozen into its weights at training time. There is no "reading" at inference — just pattern matching.

**Analogy:**
- Claude = human translator at a desk with a dictionary, style guide, and session notes open. Reads them before each sentence.
- NLLB = a reflex. Sees Nahuatl, immediately produces Spanish from internalized patterns. No desk, no notes, no pausing.

**Could you add dictionary/rules to NLLB?** Technically yes, but you'd have to change the training format too — train it with hints baked into the source:
```
"[tlatequiti=trabajar] [ni-=yo] nitlatequitiz notequiuh" → "Haré mi trabajo"
```
This is called **lexically constrained decoding** or **dictionary-augmented NMT** — a different research project, non-trivial to implement.

---

#### Ollama + LLaMA 3.1 8B — autonomous upgrade path

The sweet spot: a **local instruction-following model** that understands rules and prompts like Claude but runs entirely on local hardware.

**Ollama** is a tool that runs open-source models locally on the laptop GPU. You'd swap the Anthropic client in `translate_and_learn.py` for an Ollama HTTP call — same prompt structure, ~10 lines of code changed.

Good model candidates:

| Model | Size | Notes |
|-------|------|-------|
| `mistral:7b` | 4.1 GB | Strong, fast |
| `llama3.1:8b` | 4.7 GB | Best general quality at this size |
| `gemma2:9b` | 5.4 GB | Good multilingual |

All run comfortably on the laptop GPU (CUDA 12.x confirmed) in 4-bit quantization.

**Key advantage over NLLB:** these models are instruction-followers. They can read rules, process dictionary hints, use few-shot examples — the exact same prompt structure already in `translate_and_learn.py`. No prompt redesign needed.

**Optional upgrade:** fine-tune the local 7B model on your 4,594 pairs in instruction format:
```
[INST] Translate to Spanish.
Rules: ni- = first person, -z = future tense
Dictionary: tlatequiti = trabajar
Sentence: "Nitlatequitiz notequiuh." [/INST]
Haré mi trabajo.
```
This gives both instruction-following capability (rules/hints work) and Nahuatl domain knowledge baked in. Called **instruction fine-tuning**.

**Three-way comparison:**

| | NLLB fine-tuned | Local 7B (Ollama) | Local 7B + fine-tuned |
|--|--|--|--|
| Quality | Low | Medium-High | High |
| Dictionary/rules | No | Yes | Yes |
| Autonomy | Full | Full | Full |
| Cost | Free | Free | Free |
| Speed | Very fast | ~1–2 sec/sentence | ~1–2 sec/sentence |
| vs Claude | Much worse | Noticeably worse | Close |

---

#### NLLB + LLaMA cascade architecture

The two models complement each other. NLLB and LLaMA can be run jointly in a cascade:

**Option A: Cascade (NLLB drafts, LLaMA refines)**
```
Nahuatl sentence
    │
    ▼
NLLB-200 (fast, free, ~0.05 sec)
    │  rough draft: "Voy hacer mi trabajo"
    ▼
LLaMA 3.1 prompt:
  "Rules: [...]
   Dictionary hints: [...]
   Rough draft: 'Voy hacer mi trabajo'
   Refine: 'Nitlatequitiz notequiuh'"
    │
    ▼
Final: "Haré mi trabajo."
```
The rough draft anchors LLaMA — correcting and polishing is easier than translating cold. This is the professional MT + post-editing pattern, applied automatically.

**Option B: NLLB enriches Sullivan `es` fields**
NLLB is well-suited for word/phrase-level translation. It can fill the 9,782 empty `es` fields in `normalized_sullivan.json` fast and free. Once enriched, Sullivan becomes queryable via `morphology.py.get_hints()` and LLaMA gets better dictionary hints.

**Full combined pipeline:**
```
Nahuatl sentence
    │
    ├── morphology.py → decompose into roots
    ├── IDIEZ hints (Spanish definitions)
    ├── Sullivan hints (now enriched via NLLB)
    ├── Glossary hints (human-verified)
    ├── NLLB → rough draft translation
    └── LLaMA 3.1 (local)
            receives: rules + hints + rough draft + sentence
            produces: final Spanish
```
Fully autonomous, no API cost, better than either model alone.

---

#### VPS deployment for collaborative use

**Inference on a VPS:**
The Oracle VPS (Ubuntu 22.04, nginx already configured, 24 GB ARM RAM) can host a 7B model in CPU inference mode. A 7B model at 4-bit quantization needs ~5 GB RAM — fits comfortably. CPU inference speed: ~20–60 sec/sentence. Usable for low-traffic collaborative work.

For faster inference: a rented GPU VPS (RunPod, Vast.ai, Lambda Labs) at ~$0.30–0.50/hour gives ~1–2 sec/sentence. Spin up for a session, tear down when done.

Deployment tool options:
- **Ollama** — simple, same tool as local dev
- **vLLM** — production-grade, handles multiple concurrent users via batching

**Collaborative training — sequential fine-tuning via HuggingFace Hub:**
- Free private repo hosting up to 10 GB (sufficient for 7B at 4-bit ~4 GB, or NLLB-600M ~2.4 GB)
- Workflow: person A fine-tunes → pushes weights to HF Hub → person B pulls, adds data, fine-tunes further → pushes back
- No simultaneous training coordination needed — sequential passes, model improves incrementally

**Long-term deployment picture:**
```
Now:
  Laptop GPU → fine-tune NLLB + LLaMA → local use

Medium term:
  Oracle VPS → serve model via API → others can translate
  HuggingFace → share weights → others contribute training data

Long term:
  Dedicated GPU VPS → continuous fine-tuning as data grows
  → public API for Nahuatl translation as a service
```

The foundation already in place (4,594 pairs, 5,602 rules, morphology, multi-source dictionaries) is what a publicly useful Nahuatl translation service would need. VPS deployment is the natural next step once model quality reaches a threshold worth sharing.

---

## Checkpoint — 2026-08-08

### Work completed this session

- **Ran `/catchup`** — rebuilt full project context
- **Troubleshot Tailscale/SSH connectivity to laptop** — full diagnosis detailed below (see Notes)
- **No code written this session** — session was orientation + connectivity troubleshooting

### Current state

- D4 (NLLB fine-tune) is fully staged and still the immediate next action: venv `~/nllb-env` installed on laptop, `prep_training_data.py` + `finetune_nllb.py` committed, training corpus at 4,594 pairs
- All pipeline code unchanged since 2026-07-13 (commit `f943c90`)
- **Tablet Tailscale is offline** — must reconnect before SSH to laptop works (see Notes)
- 4 untracked files still pending commit: `dictionaries/compare_sullivan_idiez.py`, `normalized_sullivan_enriched.json`, `dictionaries/sources/sullivan_2016.pdf`, `sullivan_pending_enrichment.json`

### Next steps

1. **Reconnect tablet Tailscale** — open Tailscale app on tablet → Connect (was offline 24+ days)
2. **Verify SSH** — `! ssh wslinux@100.68.100.23` from Termux; backup: `! ssh ws@100.99.213.23`
3. **D4 — Run NLLB fine-tune on laptop** (everything ready — just needs SSH access):
   ```bash
   ssh wslinux@100.68.100.23
   source ~/nllb-env/bin/activate
   cd $(find ~ -name "Nahuatl_Translator2" -type d | head -1)
   git pull origin main
   tmux new -s d4
   python3 prep_training_data.py && python3 finetune_nllb.py
   ```
4. **D5** — After training: evaluate fine-tuned NLLB vs Claude API baseline; record BLEU scores
5. **Commit untracked files** — review and commit the 4 untracked files (skip `sullivan_2016.pdf` if too large for git)
6. **enrich_sullivan.py** — use fine-tuned NLLB to fill 9,782 empty `es` fields in `normalized_sullivan.json`
7. **A1 (Human)** — review Crispin_Carlos col H auto rules; type corrections into col I (0 human-verified rules is the biggest quality gap)

### Notes — Tailscale/SSH troubleshooting (2026-08-08)

**Symptom:** `ssh wslinux@100.68.100.23` and `ssh ws@100.99.213.23` both timed out from tablet Termux. Laptop was physically on with WSL2 open.

**Diagnosis steps:**
1. Checked `services.msc` on laptop → Tailscale service **Status: Running**, Startup: Automatic — service was fine
2. Ran `tailscale status` from WSL2 on laptop:
   ```
   100.99.213.23  ws-2023-1        ws@  windows  -
   100.68.100.23  ws-2023          ws@  linux    -
   100.96.244.82  wsmdo-tab-s10-25 ws@  android  offline, last seen 24d ago
   ```
3. Root cause identified: **tablet Tailscale was offline** — not the laptop. The laptop was fully connected to the tcp-partners.com tailnet. The SSH timeouts were because the tablet couldn't reach Tailscale IPs (it wasn't on the VPN).

**Fix:** Open Tailscale app on the Android tablet → tap Connect.

**Key lesson for future:** If SSH to laptop times out, run `tailscale status` from the laptop WSL2 window to check which end is actually offline:
```bash
/mnt/c/Program\ Files/Tailscale/tailscale.exe status
```
The status output shows all tailnet nodes — look for `offline` next to the tablet (`wsmdo-tab-s10-25`). If the tablet shows offline, fix is on the tablet side, not the laptop.

**Tailscale node reference:**
| Node | IP | Platform | SSH command |
|------|----|----------|-------------|
| `ws-2023` (WSL2) | `100.68.100.23` | Linux | `ssh wslinux@100.68.100.23` |
| `ws-2023-1` (Windows) | `100.99.213.23` | Windows | `ssh ws@100.99.213.23` |
| `wsmdo-tab-s10-25` | `100.96.244.82` | Android | (tablet — initiates SSH, doesn't receive it) |

---

## Checkpoint — 2026-09-07

### Work completed this session

- **Confirmed D4 completed successfully** — tmux session `d4` was gone; `models/nllb-nah-es-final/model.safetensors` present on laptop
- **Ran D5 eval (`--sheets-only`)** — wrote NLLB translations (col J) + BLEU scores (col K) to Crispin_Carlos (4,030 rows) and Eduardo (282 rows) sheets; avg BLEU 0.3450
- **Analyzed D5 results** (`d5_eval_results.json`, 4,312 pairs) — key lessons:
  - Model works well on full prose sentences (many BLEU=1.0)
  - Fails on: single-word nominalizations (`-liztli`), tense/aspect distinctions, complex agglutinative verb forms, place names (hallucination), section headings
  - BLEU=0.000 on diacritics-only mismatches (e.g. `Martínez` vs `Martinez`) — metric issue, not real error
- **Built `generate_deltas.py`** — creates "Deltas" tab in each source spreadsheet with 12 columns:
  - Auto: Source, Row, Nahuatl, Gold Spanish, NLLB Translation, BLEU Raw, BLEU Norm, Flag
  - Human fills: Error Type (pre-filled guess), Rule/Note (grammar rule extracted), Human Correction, Status
  - Flags: `skip` / `diacritics` / `proper_name` / `heading` / `real_error`
  - 2,767 real_error rows need human review; 743 diacritics, 111 proper_name, 358 heading, 52 skip
- **Discovered and filtered 52 Classical Nahuatl rows** — gold col contained `SKIP / Saltar`; these were in `nah_es_pairs.json` and polluting BLEU scores with false 0s
  - Removed from `nah_es_pairs.json` → **4,260 clean pairs** (was 4,312)
  - Updated `export_summary.json` with corrected counts
  - Adjusted avg BLEU (skip-excluded): **0.3492**
- **Committed all changes** — commit `8427f00` on `main`

### Current state

- D4 model lives at `~/WS_Qwen_Projects_Windows/Nahuatl_Translator/Nahuatl_Translator/models/nllb-nah-es-final/` on laptop
- D5 eval complete; results in `training_data/d5_eval_results.json` (local + on laptop)
- Deltas tab written to both sheets — human review queue ready (2,767 real_error rows)
- Clean training data: `nah_es_pairs.json` = 4,260 pairs; `nah_en_pairs.json` = 282 pairs; total 4,542
- `nah_es_pairs.json.bak` kept locally as rollback (not committed)

### Next steps

1. **Human review** — open Crispin_Carlos or Eduardo sheet → "Deltas" tab → filter col H=`real_error` → fill:
   - Col I: Error Type (confirm or correct the pre-filled guess)
   - Col J: Rule / Note (e.g. `"-liztli nominalizes verb → translate as abstract noun"`)
   - Col K: Human Correction (correct Spanish translation)
   - Col L: change `pending` → `done`
2. **Build `apply_corrections.py`** — reads Deltas tab col K (Human Correction, status=done), exports corrected pairs as new training data for D6
3. **Re-run D6 fine-tune on laptop** — use clean 4,260 pairs + human corrections from step 2
4. **Build `enrich_sullivan.py`** — use fine-tuned NLLB to fill 3,718 empty `es` fields in `normalized_sullivan_enriched.json`
5. **Commit untracked files** — `dictionaries/compare_sullivan_idiez.py`, `normalized_sullivan_enriched.json`, `sullivan_pending_enrichment.json`

### Notes

- `generate_deltas.py` is idempotent — re-run any time to refresh the Deltas tab after a new eval round
- Error Type valid values: `tense_aspect`, `verb_morphology`, `nominalization`, `lexical`, `hallucination`, `place_name`, `register`, `omission`, `other`
- To run on laptop after next fine-tune: scp `d5_eval_results.json` back to tablet first, or add a `--results-path` arg to `generate_deltas.py`
- SKIP rows are rows 173–239 in Crispin_Carlos (Classical Nahuatl section on maize terminology from Sahagún 1979) — not Modern Huasteca Nahuatl, correctly excluded

**Note on `tailscale up` from WSL2:** Running `tailscale up` inside WSL2 gives "Access denied: prefs write access denied" — this is because WSL2's own tailscale daemon needs sudo. This is a red herring; use `sudo tailscale up` in WSL2 only if you want WSL2 to have its own separate Tailscale connection. The Windows Tailscale (controlled via tray icon or `tailscale.exe` in `/mnt/c/Program Files/Tailscale/`) is what controls the VPN for SSH purposes.

---

## Checkpoint — 2026-09-21

### Work completed this session

- **Created `write_plan_to_doc.py`** — script that creates a new Google Doc for Nahuatl_Translator2 and populates it with a formatted project plan
  - Uses OAuth (`token.json`) to create the doc in the user's Drive (service account Drive was full — 403 quota exceeded)
  - Gives SA write access after creation; subsequent content writes use SA credentials
  - **4-phase pipeline:**
    - Phase 1: clear doc + insert full CONTENT (restructured with TOC section at top, no ─────── separator lines)
    - Phase 2: apply HEADING_1 to title, HEADING_2 to "Table of Contents" + all 9 section headings, HEADING_3 to Workstream/Step lines
    - Phase 3: read back doc — distinguish first occurrence of each section name (TOC entry, collect range) from second occurrence (actual heading, apply `pageBreakBefore: true` + collect `headingId`)
    - Phase 4: apply blue underlined hyperlinks (`link: {headingId}`) to each TOC entry line
  - Result: 9 sections each on their own page, clickable TOC on page 2
  - Doc ID: `15wEbCHRmjW09T5KgMLhHiGjyp4YcCRrNpBunnAiQURs`
  - URL: https://docs.google.com/document/d/15wEbCHRmjW09T5KgMLhHiGjyp4YcCRrNpBunnAiQURs/edit

- **Created `write_plan_to_doc.py` for Mayaihcuilolliztli** (`Macehualtlahtol/Mayaihcuilolliztli/write_plan_to_doc.py`)
  - Same 4-phase algorithm; 8 sections; created new Google Doc in user's Drive
  - Doc ID: `1EaSMcyl24HsZ-YySRUc0LWSx4gCmRRjHt5qArxTSuVk`

- **Updated `write_plan_to_doc.py` for Tlazanilohni** (`Macehualtlahtol/Tlazanilohni_app/write_plan_to_doc.py`)
  - Rewrote from single-pass flat script to same 4-phase algorithm; 8 sections; updated existing Doc ID `1Sfea88PHnQDlLE1LR5dkfs5aZ_FDHSgKZEnCz-Z8Wss`

### Current state

- All three Macehualtlahtol project Google Docs are live with consistent formatting:
  - Page 1: Title + date
  - Page 2: Table of Contents (section names as clickable blue hyperlinks)
  - Pages 3+: Each section on its own page with `pageBreakBefore`
- `write_plan_to_doc.py` scripts are re-runnable — clear and rewrite the full doc on each run
- All Nahuatl_Translator2 pipeline code unchanged (no translation or training work this session)
- D5 eval results and Deltas tab still represent the latest model state (avg BLEU 0.3492)

### Next steps

1. **Human review (A1)** — open Crispin_Carlos or Eduardo sheet → "Deltas" tab → filter col H = `real_error` → fill cols I/J/K/L; 2,767 rows pending, 0 human-verified rules is the biggest quality gap
2. **Build `apply_corrections.py`** — reads Deltas col K (Human Correction, status=done), exports corrected pairs as supplementary training data for D6
3. **D6 fine-tune** — re-run `finetune_nllb.py` on 4,260 original pairs + human corrections; measure BLEU improvement on nominalization and verb morphology errors
4. **Build `enrich_sullivan.py`** — use fine-tuned NLLB to fill 3,718 empty `es` fields in `normalized_sullivan_enriched.json`
5. **Commit untracked files** — `dictionaries/compare_sullivan_idiez.py`, `normalized_sullivan_enriched.json`, `sullivan_pending_enrichment.json`

### Notes

- `write_plan_to_doc.py` uses OAuth for doc creation (SA Drive quota exceeded) and SA for all batchUpdate writes — this split is intentional and must be preserved in future rewrites
- The 4-phase algorithm is now the standard pattern for all three project docs; keep them consistent
- Re-running `write_plan_to_doc.py` fully replaces doc content — it is not additive; update the CONTENT string in the script before re-running

---

## Checkpoint — 2026-09-22

### Work completed this session

- **Created `pdf_to_doc_table.py`** — script that downloads a Drive PDF, extracts text from a specified page range, and writes it to a Google Doc as a bi-columned table with one paragraph per row
  - Downloads PDF via Drive API (service account) using `MediaIoBaseDownload`
  - Extracts text from pages 108–123 of `america, Experiencias profesionales de lingüistas indomexicanos.pdf` (Drive file ID `1rE-3Xcgx099HcJvc4lvi_r2dnTlw5A8a`)
  - Paragraph extraction: splits on `\n \n` (paragraph boundaries), joins inner `\n` as spaces, strips running headers (`NNN Author Name`) and short noise fragments
  - Creates Google Doc via OAuth (user's Drive), shares with SA for subsequent writes
  - Inserts 2-column table (N+1 rows: 1 bold header + 1 row per paragraph) using `insertTable`
  - Collects cell `startIndex` values by reading back the doc structure; inserts text in reverse index order to avoid shifting
  - Fixed insert index bug: use `para_start` (paragraph's `startIndex`), **not** `para_start + 1` — the `+1` lands after the cell's newline and fails the Docs API bounds check
  - Bolded header row cells in a final pass
  - Result: 30 paragraphs extracted, 31-row × 2-col table written successfully
  - Doc ID: `1i66XN3qKwxM7KliQLqtwKm4EH6sMvVQTPR65MUD5HYI`

- **Added a third column** — single `insertTableColumn` call with `insertRight: True` on the rightmost column; table is now 31 rows × 3 cols

### Current state

- `pdf_to_doc_table.py` is complete and reusable (change `SOURCE_FILE_ID`, `PAGE_START`, `PAGE_END`, `DOC_ID` at the top for a different PDF or page range)
- Google Doc `1i66XN3qKwxM7KliQLqtwKm4EH6sMvVQTPR65MUD5HYI` has:
  - Column 1 ("Texto original"): Nahuatl text from pages 108–123, one paragraph per row
  - Columns 2–3: empty, ready for translation or notes
- Known artifacts in the table that may need manual cleanup:
  - Rows containing running chapter titles mixed with page numbers (e.g. "Nochān oniquīz… 109") — PDF repeated headers not fully stripped
  - Figure/map caption rows ("Mapa 1…", "Imagen 7…")
- All prior project code and data (NLLB fine-tune, Sheets pipeline) unchanged

### Next steps

1. **Manual cleanup** — remove or merge artifact rows in the Google Doc (running headers mixed with page numbers, figure captions)
2. **Fill columns 2–3** — add Spanish translation or notes to the empty right columns; or define what each column represents and update the header row
3. **Human review (A1)** — open Crispin_Carlos or Eduardo sheet → "Deltas" tab → filter `real_error` → fill cols I/J/K/L (0 human-verified rules remains the biggest translation quality gap)
4. **Build `apply_corrections.py`** — export human-corrected pairs from Deltas col K for D6 fine-tune
5. **D6 fine-tune** — re-train NLLB-200 on 4,260 pairs + corrections; measure BLEU improvement

### Notes

- `pdf_to_doc_table.py` uses SA for Drive download and all Docs API writes; OAuth only for doc creation (SA Drive quota exceeded)
- Insert index for table cells must be `content[0]['startIndex']` (the paragraph start), never `+1` — this is a non-obvious Docs API constraint worth remembering
- `insertTableColumn` only needs the table start index, one row index, and one column index — it applies to all rows automatically
- PDF text extraction via `pypdf` is good enough for clean prose but misses footnote separation and running headers on some pages; manual review of the output doc is recommended

---

## Checkpoint — 2026-09-24

### Work completed this session

- **Literature review: Nahuatl neologism generator** — researched strategies for coining Nahuatl vocabulary for modern technical terms (FT/NYT-register words not currently in Nahuatl)
  - Identified 4 main strategies: (1) native compounding, (2) Chinese semantic calque, (3) Greek/Latin neoclassical compound model, (4) committee-based institutional models
  - Key finding: Chinese model (dianao = "electric brain" = computer) is closest analog — semantically transparent compounding without phonological borrowing; directly applicable to Nahuatl's agglutinative morphology
  - Key finding: Wikipedia confirms Chinese serves same role as Latin/Greek for East Asian languages (wasei kango: 自動車 = "self-move-car" = automobile) — strongest existing precedent for Classical Nahuatl morphemes serving same function for Modern Huasteca Nahuatl
- **Created `add_neologism_section.py`** — 5-phase Google Docs API script that appends a new section to an existing doc and links it in the ToC
  - Phase 1: read doc, find TOC entry end index and document end index
  - Phase 2: insert section text at end + new TOC entry after last TOC item (higher index first in single batchUpdate)
  - Phase 3: apply HEADING_2 to both occurrences of section name
  - Phase 4: apply pageBreakBefore to actual section heading (second occurrence); apply HEADING_3 to sub-headings within the new section only (gated by `startIndex > section_start`)
  - Phase 5: apply blue underlined hyperlink to TOC entry using headingId
  - Ran successfully — "NEOLOGISM GENERATOR RESEARCH" added as page 11 with 8 HEADING_3 sub-headings and linked 10th ToC entry
- **Deep source review** — fetched and read primary sources using WebFetch + pypdf extraction of saved PDFs:
  - **NAU 2009 (Kimura & Counceller)** — full 20-page paper; key output: the 10 official guidelines for creating new Hawaiian words from *Māmaka Kaiao* appendix; detailed "evolution" coining example (liliuewe, liliuloli, liliuwelo from one root); Alutiiq calque example (Anchorage → Kicarwik = "place to anchor")
  - **ACL 2025 (Kuene)** — full 6-page paper; two-round approval process before publication; 400+ words published since launch; also building legal Hawaiian and monolingual dictionaries
  - **Mexicolore (Hadley 2021)** — train = "metal house that rolls"; typewriter = "metal writer"; library = "book house" — confirms two output modes: tight compound vs. descriptive periphrasis
  - **Wikipedia Hebrew revival** — specific coinages: tapuz (orange) = "golden apple" (pure calque); ʿagvaniyyah (tomato) calqued from German; ḥashmal (electricity) from Akkadian Ezekiel passage
  - Academia.edu (3 links) — 403; WebFetch cannot inherit browser auth sessions regardless of subscription

### Current state

- Neologism research added to Google Doc `15wEbCHRmjW09T5KgMLhHiGjyp4YcCRrNpBunnAiQURs` as section 10 with ToC link
- `add_neologism_section.py` is complete and reusable (change `NEW_SECTION`, `SECTION_TEXT`, `LAST_TOC_ENTRY` at the top for a different section)
- All prior NLLB / Sheets / translation pipeline code unchanged
- D5 eval still represents latest model state (avg BLEU 0.3492); 2,767 Deltas rows pending human review

### Next steps

1. **Neologism generator design** — define the architecture: (a) root inventory from IDIEZ dictionary, (b) rule engine applying the 10 Hawaiian-style composition guidelines adapted for Nahuatl, (c) optional committee/validation layer
2. **Target concept list** — extract 200–300 FT/NYT-register terms absent from IDIEZ; finance, geopolitics, technology, climate are the priority domains
3. **Human review (A1)** — open Crispin_Carlos or Eduardo sheet → Deltas tab → filter `real_error` → fill cols I/J/K/L; still 0 human-verified rules, biggest translation quality gap
4. **Build `apply_corrections.py`** — export human-corrected pairs from Deltas col K for D6 fine-tune
5. **D6 fine-tune** — re-train NLLB-200 on 4,260 pairs + human corrections; target improvements in nominalization and verb morphology
6. **Download Academia.edu PDFs manually** — three papers returned 403 to WebFetch; share files directly to read them: "Un nuevo sistema para la escritura náhuatl", "Language Documentation: The Nahuatl Grammar", "Náhuatl: Language Endangerment and Revitalization"

### Notes

- `add_neologism_section.py` pattern: always insert at higher index first within a single batchUpdate to avoid index shifting errors; HEADING_3 scoping uses `startIndex > section_start` to avoid accidentally styling identically-named paragraphs elsewhere in the doc
- The 10 Hawaiian word-formation guidelines (NAU 2009 appendix) map directly to Nahuatl: rules 4, 6, 7 (affixation, compounding, shorten-and-combine) are already productive in Nahuatl; rule 9 (borrow from related language) → use Classical Nahuatl or other Nahuan varieties (Pipil, Mexicanero); rule 10 (nativize foreign word) → last resort after native options exhausted
- Academia.edu cannot be accessed via WebFetch even with subscription — browser session auth is not passable; download PDFs manually and share as local files
- **Yale NNC chart** (`dictionaries/sources/nahuatl_nnc_structure_yale.pdf`) — formal one-page morphology diagram for Nahuatl noun compounds; source: Yale study group. Defines the "affinity stem" (combining form) transformation rules needed for both the FST morphological analyzer and the neologism generator. Verb morphology chart pending — if unavailable, will be built from grammar sources.
- **Ben Yehuda / Arabic borrowing research** — confirmed: Ben Yehuda's Language Committee explicitly borrowed from Arabic when Hebrew had no equivalent root, then applied Hebrew root-and-pattern morphology. Key paper: "Arabic loanwords in Hebrew" by Haseeb Shehadeh (Academia.edu — accessible with subscription). Concrete examples: rishmi (official) from Arabic rasmi; retsini (serious) from Arabic ratsin. Critical finding: Anton Shammas demonstrated *morphological* borrowing — coined lekhamer ("treat like a donkey/idiot") by applying an Arabic causative verb pattern to a Hebrew root. This is the most directly applicable model: import a grammatical pattern from a related language, not just a word. For Nahuatl: Classical Nahuatl serves the role Arabic played for Hebrew — same family, shared roots, specialist vocabulary already coined for medicine/astronomy/governance.
- **Sullivan 2016 example sentences** — `raw_sullivan.json` already contains example sentences for 8,046 of 9,782 entries (82%). The `example` field is populated; 1,736 entries have examples in `raw_body` that the parser missed. These ~8,000 Nahuatl example sentences are unused training data and a source for the neologism repository. The Sullivan PDF shared via Drive (file ID `1R4Xjxmi13GQ8Nf1hDQVAG3sx4pwEhc81`) is the same as `dictionaries/sources/sullivan_2016.pdf` already in repo — no need to save again.

---

## Checkpoint — 2026-09-25

### Work completed this session

- **Public domain / translation rights confirmed** — *On Liberty* (Mill, 1859) and *Walden* (Thoreau, 1854) are fully public domain everywhere. A Nahuatl translation of either would be original creative work owned by the translator; no royalties required. Project Gutenberg explained as the source for clean, bare public-domain text files.
- **Yale NNC morphology chart saved to repo** — downloaded `nahuatl_nnc_structure_yale.pdf` (183 KB) from Google Drive (file ID `1bjHuIUAdEiGFFaI4Xb_8P1AESDm3C9Th`) and saved to `dictionaries/sources/nahuatl_nnc_structure_yale.pdf`. Source: Yale study group. One-page formal slot diagram of Nahuatl noun-noun compound structure: prefix positions, person markers, absolute/possessive states, monadic/dyadic possession, three stem types (base/affinity/distributive), GU root stem transformation rules for tl-class nouns (subclasses a/b/c). Reference documents table in plan updated. Verb morphology chart pending from same source.
- **Replied to two Google Doc comments** (Drive API `replies().create`):
  - Comment on "systematically" — explained Ben Yehuda's root-and-pattern mechanism with concrete examples (ofanayim, tapuz, milon, iton)
  - Comment on "IDIEZ does informally" — proposed IDIEZ neologism repository: JSON structure, 5 mining sources, 50-100 example target for rule extraction
- **Ben Yehuda / Arabic borrowing research** — searched literature and fetched Times of Israel blog ("Brilliant borrowing & nifty neologisms"). Key findings:
  - Committee formally endorsed Arabic borrowing when no Hebrew root existed; applied Hebrew morphological patterns to Arabic roots (rishmi from rasmi, retsini from ratsin)
  - Critical: Anton Shammas demonstrated *morphological* borrowing — coined lekhamer by applying Arabic causative verb pattern to Hebrew root for donkey; imported a grammatical pattern, not a word
  - Academic paper: "Arabic loanwords in Hebrew" by Haseeb Shehadeh (Academia.edu, accessible with subscription)
  - Nahuatl parallel: Classical Nahuatl = "Arabic" for Modern Huasteca — same family, shared roots, specialist vocabulary already available
- **Sullivan 2016 Drive file reviewed** (file ID `1R4Xjxmi13GQ8Nf1hDQVAG3sx4pwEhc81`) — confirmed same as `dictionaries/sources/sullivan_2016.pdf` (644 pages, 16 MB). Key discovery: `raw_sullivan.json` already has example sentences for 8,046 of 9,782 entries (82%) in the `example` field; 1,736 entries have examples in `raw_body` not yet extracted. These ~8,000 Nahuatl sentences are unused training data.
- **Project plan notes updated** with all of the above findings.
- **Google Doc neologism section updated** — replaced single short Hebrew paragraph (16073–16366) with 5-paragraph expanded section covering: original summary, Arabic borrowing mechanism (rishmi/retsini), Shammas morphological borrowing (lekhamer), Classical Nahuatl as "Arabic" parallel, and inline sources.

### Current state

- Google Doc `15wEbCHRmjW09T5KgMLhHiGjyp4YcCRrNpBunnAiQURs` has expanded Hebrew/Arabic section in neologism research; both comments have replies
- Yale NNC noun morphology chart is in repo; verb chart still pending
- Sullivan example sentences (8,046) are in `raw_sullivan.json` but not yet used as training data or for the neologism repository
- All prior pipeline code and eval results unchanged (D5 BLEU 0.3492, 2,767 Deltas rows pending)

### Next steps

1. **IDIEZ neologism repository** — start JSON file of documented Nahuatl coinages: scan `dictionary_idiez.json` for compound entries (tepoztl- prefix, -liztli nominalizations of borrowed concepts), add Mexicolore examples, IDIEZ grammar examples; target 50–100 entries to bootstrap rule extraction
2. **Neologism generator design** — define architecture: (a) root inventory from IDIEZ, (b) rule engine based on 10 Hawaiian-style guidelines adapted for Nahuatl, (c) Classical Nahuatl borrowing layer (parallel to Ben Yehuda's Arabic layer)
3. **Target concept list** — 200–300 FT/NYT-register terms absent from IDIEZ: finance, geopolitics, technology, climate
4. **Get verb morphology chart** from Yale study group; if unavailable, reconstruct from Sullivan + IDIEZ grammar
5. **Extract missing Sullivan examples** — fix parser for 1,736 entries where `example` is null but `raw_body` contains quoted sentences
6. **Human review (A1)** — Deltas tab → filter `real_error` → fill cols I/J/K/L; 2,767 rows, 0 done — biggest translation quality gap
7. **Build `apply_corrections.py`** + **D6 fine-tune** (depends on A1)
8. **Download Academia.edu PDFs** — "Arabic loanwords in Hebrew" (Shehadeh), "Language Documentation: The Nahuatl Grammar", "Náhuatl: Language Endangerment and Revitalization"

### Notes

- Morphological borrowing (Shammas/lekhamer model) is more powerful than lexical borrowing for a neologism generator — the generator should be able to apply Classical Nahuatl morphological patterns to Modern Huasteca roots, not just borrow Classical words wholesale
- `raw_sullivan.json` structure: entries are lists keyed by headword_norm; `example` field is already parsed for 82% of entries; `raw_body` contains the full original text including examples for all entries
- Google Doc comment replies are posted via Drive API `replies().create(fileId, commentId, fields='id,content', body={'content': text})` — the `fields` parameter is required or the API returns 400

---

## Checkpoint — 2026-09-27

### Work completed this session

- **Audited both Drive folders** — source folder (`1AFp-WuRMnhmV05km0-4D-7cQQWRdIa2a`) has 14 PDFs; transcribed folder (`1LW0qwgf58wUX1UhpL7K2Y_6gW5x_NAoF`) has 3 sheets (Eduardo, Crispin, Crispin_Carlos)
- **Identified already-transcribed docs** — only De la Cruz 2017 (Eduardo) is done from the source folder; Crispin/Crispin_Carlos come from a separate source not in this folder
- **Assessed all 13 remaining PDFs** — downloaded and checked extractability; 11 of 13 are text-extractable (pypdf); 2 are >35MB and skipped for now (Martínez Rosas 2022, Maryniak&Nava 2017)
- **Sullivan 2016 Chicontepec confirmed as duplicate** — same file as `dictionaries/sources/sullivan_2016.pdf` already in repo as `raw_sullivan.json`; excluded from transcription
- **Discovered Zapoteco 2019 is trilingual** — has facing-page English translations (future: extract as gold col C)
- **Wrote `transcribe_all_docs.py`** — full pipeline script for laptop:
  - Downloads 10 PDFs from Drive (service account)
  - Extracts/segments Nahuatl text (prose / vocab / poetry modes)
  - Creates Google Sheets in standard 11-col format (col A=heading, col B=Nahuatl, col J=NLLB)
  - Loads NLLB fine-tuned model once, batch-translates all sentences → col J
  - Checkpoints progress to `transcribe_progress.json` (resume on crash)
  - CLI flags: `--dry-run`, `--skip-nllb`, `--doc SUBSTR`
- **Dry-run validated** — extraction working; row counts per doc:
  - De la Cruz 2015: 657 sentences | Bueno&Nava 2015: 120 | Burkhart 2017: 776
  - Nava 2013: 482 | Nava&Cuahutle 2015: 863 | De la Cruz 2016: 110
  - Atliaca 2020: still being tuned (prose intro bleeds into vocab section)
  - Xochitiotzin 2020: 26 | Zapoteco 2019: 41 | Zapoteco 2014: 38
  - **Total estimated: ~3,100–3,500 new Nahuatl sentences across all docs**

### Current state

- `transcribe_all_docs.py` written but NOT yet committed — one pending fix: Atliaca mode/skip_pages needs tuning (prose intro bleeds past p.20 into what should be vocabulary section)
- `tmp_pdfs/` folder has 11 cached PDFs (not committed, local only)
- No new sheets created yet — script is ready to run on laptop once committed + pushed
- All other pipeline code unchanged (D5 BLEU 0.3492, 2,767 Deltas rows pending)

### Next steps (immediate — finish before laptop run)

1. **Fix Atliaca extraction** — change mode to `prose` with skip_pages=8 to capture history intro as training data; vocab items will appear as short rows (acceptable)
2. **Commit and push** — `transcribe_all_docs.py` + updated project plan
3. **Laptop run** (SSH → tmux):
   ```bash
   ssh wslinux@100.68.100.23
   cd <Nahuatl_Translator2 path>
   git pull origin main
   tmux new -s transcribe
   source ~/nllb-env/bin/activate
   python3 transcribe_all_docs.py 2>&1 | tee transcribe.log
   ```
4. **After laptop finishes** — 10 new sheets appear in Drive folder `1LW0qwgf58wUX1UhpL7K2Y_6gW5x_NAoF`; fill col C (gold Spanish) for high-priority prose docs
5. **Human review (A1)** — still 2,767 Deltas rows pending (biggest quality gap)

### Notes

- `transcribe_all_docs.py` uses same `_sa_path()` pattern as `eval_nllb_d5.py` — finds `~/service_account.json` on laptop automatically
- Atliaca (Iglesias&Maryniak 2020) is a picture dictionary: first ~35 pages are history prose (Olmec, Teotihuacan), then vocabulary word lists — both are usable training data
- Zapoteco 2019 English parallel extraction is a future enhancement: detect Nahuatl vs English pages by language scoring, pair consecutive runs as col B (Nahuatl) + col C (English gold)
- Martínez Rosas 2022 (35MB) and Maryniak&Nava 2017 (46MB) skipped — likely large scanned documents; assess manually before adding to DOCS list
- `transcribe_progress.json` is the crash-recovery checkpoint; safe to delete and re-run from scratch if needed

---

## Checkpoint — 2026-09-27

### Work completed this session

- **ACK orthography standardization** — ran `apply_ack_spelling.py`; applied 35+ IDIEZ→ACK string replacements across 36 rows × 12 cols; 74 cells updated in the sheet and `morpheme_mapping_table.md` synced
- **Split NAH examples column into Attested vs. Neologisms** — created and ran `split_nah_examples_column.py`; inserted new column J after I using `insertDimension` API; hardcoded per-row classification for all 35 rows based on Karttunen (1992), Molina (1571), Sullivan/IDIEZ (2016), Lockhart (2001); column I renamed "NAH Attested Examples", J = "NAH Neologisms" (italic formatting); key linguistic examples: `achi cualli` (attested phrase), `cenca miac tominchipoltiliztli` (coined neologism)
- **ACK corrections in columns I/J** — created and ran `fix_ack_columns_ij.py`; 11 targeted batch_update fixes: `calcan`/`calton` (calli compounds), `pozotic`/`cualtic` (final k→c + z), `icpac` (classical form of ichpak), `tlalticpac` (J25/J26/J33), `tlacatecolotcayotl`/`mauhcayotl` (J32), `yollotcocolyotl` (wrong stem yolliz→yollot); confirmed `tlacatecolotcayotl` correct (tlacatecolotl = person+owl = devil)
- **References tab** — created and ran `add_references_tab.py`; 21 references across 6 categories (Nahuatl dictionaries, word-formation textbooks, morpheme databases, cross-linguistic, this project); color-coded by category; key fix: `fontSize` must nest inside `textFormat` dict, not at top-level `userEnteredFormat`
- **Initial Morpheme DB tab** — created `fetch_morpheme_db.py`; downloaded MorphyNet ENG (225,131 lines) + SPA (30,777 lines) via GitHub API and MorphoLEX-en xlsx; fixed MorphoLEX parser to read summary sheets "All prefixes"/"All suffixes" directly (first sheet is a cover page); wrote combined tab with 4 sections + "In Table?" cross-reference column
- **Rebuilt Morpheme DB as two tabs** — created and ran `rebuild_morpheme_db.py`; merged MorphyNet ENG (count ≥ 3) + MorphoLEX (family_size ≥ 2) on normalized (morpheme, type) key; results: 1,555 unique ENG morphemes (185 in both DBs, 1,300 MorphyNet-only, 70 MorphoLEX-only); 391 SPA morphemes; created "Morpheme DB - ENG" (9 columns) and "Morpheme DB - ESP" (10 columns) tabs; deleted old "Morpheme DB"; batched formatting in groups of 150 requests to avoid API limits
- **SPA→ENG mapping column** — created and ran `update_esp_eng_mapping.py`; hardcoded SPA_TO_ENG dict with ~50 entries mapping Spanish morphemes to English equivalents with semantic notes (e.g. `-ción` → `-tion/-ation`, `des-` → `dis-/un-/de-`); added column F "ENG Equivalents" (teal) + G/H for ENG MorphyNet/MorphoLEX stats; 83 of 391 morphemes mapped, 308 unmapped (demonyms, verbal endings, rare forms); 852 formatting requests in batches of 150
- **Google Doc** — created and ran `create_morpheme_mapping_doc.py`; OAuth token refresh; 57 paragraphs, 20,029 chars, 114 Docs API requests batched in groups of 100; placed in Tlahtolyancuictia folder (15HBoSkLT0dKjlxQquAv9zbmpQxjFaArH); covers: overview, sheet structure (13 cols A-M), all 35 morpheme categories, ACK rules + corrections, attested vs. neologisms, Lockhart delta analysis, MorphyNet/MorphoLEX/CELEX2 details, all 9 scripts, gaps/next steps, 21 references

### Current state

- Google Sheet has 5 tabs: Morpheme Mapping (35 rows, 13 cols A-M), Missing Morphemes, References (21 entries), Morpheme DB - ENG (1,555 rows), Morpheme DB - ESP (391 rows)
- Sheet column structure: A(#), B(Section), C(Category), D(EN Morpheme), E(EN Examples), F(ES Morpheme), G(ES Examples), H(NAH Morpheme), I(NAH Attested), J(NAH Neologisms), K(Productivity), L(Generator Rule), M(Lockhart Notes)
- All Nahuatl text in the sheet and morpheme_mapping_table.md is now in ACK orthography
- Google Doc `1c-0WWeSd66SLrtyrcv9WkG-DGn-AoBzwM9ILm9ytfN4` documents the full session's work
- 9 scripts total: apply_ack_spelling.py, split_nah_examples_column.py, fix_ack_columns_ij.py, add_references_tab.py, fetch_morpheme_db.py, rebuild_morpheme_db.py, update_esp_eng_mapping.py, create_morpheme_mapping_doc.py, add_neologism_section.py

### Next steps

1. **Extend SPA_TO_ENG mapping** — 308 of 391 Spanish morphemes unmapped; extend `update_esp_eng_mapping.py` SPA_TO_ENG dict to cover demonyms (-ano, -eño, -ense), verbal endings (-ar, -er, -ir, -ado, -ido), and more productive derivational suffixes
2. **Add missing morphemes to 35-row table** — flagged gaps: semi-/tlahco-, neo-/yancuic-, pseudo-/tlapic-, mal-/mis-/ahmo cualli + verb combination; add as new rows in the Morpheme Mapping tab
3. **IDIEZ neologism repository** — start JSON file of documented Nahuatl coinages from dictionary_idiez.json, IDIEZ grammar, Mexicolore; target 50–100 entries for rule extraction
4. **Neologism generator design** — architecture: (a) root inventory from IDIEZ, (b) rule engine based on Hawaiian-style guidelines adapted for Nahuatl, (c) Classical Nahuatl borrowing layer
5. **Target concept list** — 200–300 FT/NYT-register terms absent from IDIEZ; finance, geopolitics, technology, climate
6. **Human review (A1)** — Deltas tab → filter `real_error` → fill cols I/J/K/L; 2,767 rows, 0 done — biggest translation quality gap
7. **Build `apply_corrections.py`** + **D6 fine-tune** (depends on A1)

### Notes

- CELEX2 requires LDC license (LDC96L14) — not freely available; MorphoLEX used as open alternative throughout
- MorphoLEX xlsx structure: 34 sheets including cover "Presentation"; parse summary sheets "All prefixes" and "All suffixes" directly
- MorphyNet TSV format (no header): source_word, target_word, source_pos, target_pos, morpheme, type — use indices [4] and [5]
- `fontSize` in Sheets API must be inside `textFormat` dict; placing it at top-level `userEnteredFormat` causes HTTP 400 "Unknown name" error
- Sheets API formatting: batch max ~150 requests per batchUpdate call to avoid limits
- Docs API forward index tracking: start at idx=1, advance by len(text)+1 per paragraph; batch in groups of 100 requests

---

## Checkpoint — 2026-09-28

### Work completed this session

- **Atliaca mode fix** — changed `Iglesias Maryniak 2020 Atliaca` from `mode='vocab', skip_pages=20` to `mode='prose', skip_pages=8`; vocab mode was treating mid-sentence line fragments as vocabulary items; prose mode yields 156 clean sentences + 5 headings
- **`transcribe_all_docs.py` committed and pushed** — pipeline script for laptop: downloads 10 PDFs from Drive, extracts Nahuatl rows (prose/poetry/vocab modes), creates Google Sheets in standard 11-col format, runs NLLB translations; includes crash-recovery via `transcribe_progress.json`; CLI flags: `--skip-nllb`, `--dry-run`, `--doc SUBSTR`
- **Ran pipeline on laptop** — resolved a chain of issues before achieving success:
  1. `googleapiclient` missing in laptop venv → `pip install google-api-python-client`
  2. `storageQuotaExceeded` on SA Drive → multiple fix attempts; root cause: SA's 15GB Drive quota full
  3. Switched to user OAuth via `token.json` — replicated `transcribe_pdf_to_sheet.py` tablet pattern: load `token.json` field-by-field with `google.oauth2.credentials.Credentials`; use `gc.create()` (Sheets API, no Drive quota hit) instead of Drive API `files().create()`
  4. `token.json` not on laptop — copied from tablet (`/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json`) to laptop `~/token.json` via `scp`; added `~/token.json` as first candidate path in script
  5. gspread 6.x `ws.update()` argument order changed → fixed all header calls to `ws.update(values, range_name)`
- **All 10 sheets created successfully** — ~3,269 Nahuatl rows total across 10 sheets; `--skip-nllb` run (no translations yet)
- **`move_sheets_to_folder.py`** — one-off script to move the 10 already-created sheets from Drive root into `TARGET_FOLDER_ID` using user OAuth Drive API `files().update(addParents=...)`
- **`create_sheet()` updated** — now moves newly created sheet to `TARGET_FOLDER_ID` automatically after `gc.create()`, using `user_drive_svc` (user OAuth with Drive scope); `connect()` now returns `gc, user_drive_svc, sa_drive_svc` (SA kept for PDF downloads only)
- **Commits this session:** `0bc9ae7` (initial script), `c3e18a1` (OAuth Drive), `6121b07` (Sheets API create), `a83a787` (tablet token.json pattern), `a372b5b` (~/token.json candidate), `10e3588` (gspread arg order), `8b423af` (folder move)

### Current state

- 10 Google Sheets created in user's Drive with Nahuatl rows (col B) and section headings (col A); sheets need to be moved to `1LW0qwgf58wUX1UhpL7K2Y_6gW5x_NAoF` via `move_sheets_to_folder.py`
- Sheets do NOT yet have NLLB translations (col J) — `--skip-nllb` was used
- `~/token.json` exists on laptop (copied from tablet); script finds it as first candidate
- SA Drive quota is full — all Sheets creation must go through user OAuth path

### Next steps

1. **Move sheets to folder** — run `python3 move_sheets_to_folder.py` on laptop to place 10 sheets in target Drive folder
2. **NLLB translations** — delete `transcribe_progress.json` on laptop, re-run `python3 transcribe_all_docs.py` (without `--skip-nllb`) to fill col J; this needs the GPU — ensure `nllb-env` venv is active
3. **Fill col C (Gold Spanish)** — human translation reference for the 10 new sheets; high-priority for prose docs (Tototatahhuan, Malintzin, Chicontepec, Atliaca)
4. **Human review (A1)** — Deltas tabs in Crispin_Carlos and Eduardo sheets still have ~2,767 `real_error` rows pending (cols I/J/K); biggest quality gap for next fine-tune round
5. **D6 fine-tune** — once A1 corrections are in, build updated training set and fine-tune NLLB

### Notes

- `token.json` on laptop is at `~/token.json` — keep it there; it has both `spreadsheets` and `drive` scopes from the Financial_Analysis_App OAuth flow
- SA Drive quota exceeded permanently (15GB free tier) — never use SA for `files().create()` again; always use user OAuth `gc.create()` + `user_drive_svc.files().update(addParents=...)`
- The tablet pattern for new scripts: pre-create sheets in browser, share with SA, hardcode IDs — avoids all quota issues
- `transcribe_progress.json` records completed docs; delete it to force a full re-run; individual docs can be re-run with `--doc SUBSTR` flag
- Zapoteco 2019 English parallel extraction is a future enhancement (facing-page translations)
