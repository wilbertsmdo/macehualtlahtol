import json
from google.oauth2.service_account import Credentials as SACredentials
from googleapiclient.discovery import build

SA_KEY  = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
DOC_ID  = '1Sfea88PHnQDlLE1LR5dkfs5aZ_FDHSgKZEnCz-Z8Wss'

SA_SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive',
]

sa_creds = SACredentials.from_service_account_file(SA_KEY, scopes=SA_SCOPES)
docs_service = build('docs', 'v1', credentials=sa_creds)
print(f'Updating: https://docs.google.com/document/d/{DOC_ID}/edit')

# ── section registry ───────────────────────────────────────────────────────────

TOC_HEADER = 'Table of Contents'

SECTIONS = [
    'WHAT IS THIS PROJECT?',
    'WHY BUILD THIS?',
    'SYSTEM ARCHITECTURE',
    'FILE STRUCTURE',
    'TOOLS & PACKAGES — WITH RATIONALE',
    'BUILD SEQUENCE',
    'AUDIOBOOK PIPELINE — PHASE 2',
    'NORMALIZER PHONOLOGY — KNOWN GAPS',
    'COMPATIBILITY PATCHES (coqui-tts vs transformers)',
    'HOW TO RUN THE APP',
    'KEY CONSTRAINTS AND DECISIONS',
    'OPEN QUESTIONS',
    'SESSION LOG',
]

HEADING_3_PREFIXES = (
    'Step 1',
    'Step 2',
    'Step 3',
    'Step 4',
    'Step 5',
    'Step 6',
    'Step 7',
    'Data source',
    'Script spec',
    'Output structure',
    'Error handling',
    'Problem 1',
    'Problem 2',
    'Recommended',
    'Requirements',
    'Check if the server',
    'Start the laptop',
    'Synthesize speech',
    'Find saved audio',
    'Troubleshooting',
    'Quick reference',
    'Session 2026-09-19',
    'Session 2026-09-20',
    'Session 2026-09-23',
    'Session 2026-09-27',
    'Session 2026-09-28',
)

# ── document content ───────────────────────────────────────────────────────────

CONTENT = """\
Tlazanilohni — Modern Nahuatl Text-to-Speech App
Project Plan · Last updated 2026-09-27

Table of Contents

WHAT IS THIS PROJECT?
WHY BUILD THIS?
SYSTEM ARCHITECTURE
FILE STRUCTURE
TOOLS & PACKAGES — WITH RATIONALE
BUILD SEQUENCE
AUDIOBOOK PIPELINE — PHASE 2
NORMALIZER PHONOLOGY — KNOWN GAPS
COMPATIBILITY PATCHES (coqui-tts vs transformers)
HOW TO RUN THE APP
KEY CONSTRAINTS AND DECISIONS
OPEN QUESTIONS
SESSION LOG

WHAT IS THIS PROJECT?

"Tlazanilohni" (tla-za-ni-LOH-ni) means "the one who reads aloud" in Nahuatl. This app takes modern Nahuatl text as input and produces spoken audio output using a cloned voice extracted from a real Nahuatl speaker on YouTube.

The target dialect is modern spoken Nahuatl — not the classical or literary register used in Nahuatl_Translator2. This distinction matters because modern Nahuatl has different phonology, orthographic conventions, and vocabulary.

WHY BUILD THIS?

Nahuatl has virtually no text-to-speech (TTS) resources. There is no Google TTS voice for it, no commercial product, and no open-source model trained on it. Any system that can pronounce Nahuatl text in a natural-sounding voice would be genuinely novel.

The approach: clone an existing Nahuatl speaker's voice from a YouTube video, and use a multilingual zero-shot TTS model to speak any text in that voice. The model handles phoneme production; the voice clone provides the speaker's timbre and intonation.

SYSTEM ARCHITECTURE

The app is split across two devices:

  Android Tablet (ARM / Termux)  ←─── Tailscale VPN (HTTP) ───→  Windows Laptop (x86_64)
  main.py                                                          WSL2 Ubuntu 24.04
    └─ normalizer.py                                               NVIDIA RTX 3060 (CUDA)
    └─ HTTP POST /synthesize                                       tts_server.py (FastAPI)
    └─ save to Music/Tlazanilohni/                                   └─ XTTS-v2 model
    └─ play via termux-open                                          └─ reference_voice.wav

  Tailscale IP of laptop WSL2: 100.68.100.23
  Server port: 8000

WHY TWO DEVICES?

The core TTS model (Coqui XTTS-v2) requires a GPU to run at acceptable speed. On a CPU (like the ARM tablet), it takes 30–60 seconds per sentence. On an NVIDIA RTX 3060 with CUDA, the same sentence takes 2–5 seconds. The laptop GPU is already available and accessible over Tailscale, so the model runs there and the tablet acts as the front-end.

FILE STRUCTURE

Android side (Tlazanilohni_app/):
  main.py              — entry point: accepts Nahuatl text, calls server, plays audio
  normalizer.py        — preprocesses Nahuatl text for TTS pronunciation
  patch_coqui.py       — patches coqui-tts source files for transformers compatibility
  full_audio.wav       — full 1:47 audio from the YouTube reference video (backup)
  reference_voice.wav  — 25-second clean clip used as the voice fingerprint

Laptop side (~/Tlazanilohni_server/):
  tts_server.py        — FastAPI server: receives text, runs XTTS-v2, returns audio
  reference_voice.wav  — copy of the voice reference (same file, different machine)
  tts.log              — Uvicorn server log (stdout/stderr from nohup run)

Output (Android shared storage):
  /storage/emulated/0/Music/Tlazanilohni/   — generated .wav files (visible in Files app)

TOOLS & PACKAGES — WITH RATIONALE

1. yt-dlp
   What: Command-line YouTube downloader.
   Why needed: Extract audio from the reference YouTube video containing the Nahuatl speaker whose voice we clone.
   Installed: Termux Python via pip3 (pure Python, no compiled extensions)
   Version: 2026.08.19

2. ffmpeg
   What: Multimedia processing tool. Converts audio/video formats, clips segments, resamples.
   Why needed: Converts raw download to WAV, resamples to 22050 Hz mono (XTTS-v2 spec), clips 25-second segment.
   Installed: Termux native via pkg install
   Version: 8.1.2-5
   Binary path: /data/data/com.termux/files/usr/bin/ffmpeg (must use full path from PRoot)

3. Coqui XTTS-v2 (coqui-tts package, imports as TTS)
   What: Open-source multilingual TTS model with zero-shot voice cloning.
   Why needed: Core synthesis engine. Free, open-source, 17 languages, true zero-shot voice cloning, GPU-accelerated.
   Installed: Laptop WSL2, ~/nllb-env, via pip install TTS (coqui-tts community fork)
   Version: coqui-tts 0.27.5
   Model size: ~2 GB (downloaded once automatically on first run, cached in ~/.local/share/tts/)
   Note: coqui-tts 0.27.5 has import incompatibilities with all versions of transformers — requires patches (see COMPATIBILITY PATCHES section).

4. PyTorch + torchaudio
   What: Deep learning framework; torchaudio handles audio tensor operations.
   Why needed: XTTS-v2 is built on PyTorch. RTX 3060 GPU reduces inference from ~60s to ~3s via CUDA.
   Installed: Laptop WSL2, via pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

5. transformers (HuggingFace)
   What: NLP library. XTTS-v2 uses GPT2InferenceModel from transformers internally for autoregressive token generation.
   Version on laptop: 4.37.2 (downgraded from 4.44.2 to reduce incompatibility surface)
   Note: coqui-tts declares requirement for >=4.57 but no such version resolves all issues — patches are required regardless.

6. FastAPI
   What: Modern Python web framework for building APIs.
   Why needed: Turns the laptop's TTS function into an HTTP endpoint the tablet can call over Tailscale.
   Installed: Laptop WSL2, via pip install fastapi

7. Uvicorn
   What: ASGI server that runs FastAPI applications.
   Why needed: FastAPI cannot serve HTTP on its own — Uvicorn listens on port 8000 and dispatches requests.
   Installed: Laptop WSL2, via pip install uvicorn
   Start command: nohup uvicorn tts_server:app --host 0.0.0.0 --port 8000 > ~/Tlazanilohni_server/tts.log 2>&1 &

8. Tailscale
   What: Mesh VPN that creates a secure private network between devices.
   Why needed: Android tablet and Windows laptop are on different networks. Tailscale assigns stable private IPs.
   Laptop Tailscale IP: 100.68.100.23 (WSL2 Ubuntu)
   Already installed: Both devices, under tcp-partners.com tailnet

9. requests (Python, Android side)
   What: HTTP client library for Python.
   Why needed: main.py sends HTTP POST requests to the laptop's FastAPI server.
   Already installed: Termux Python

10. normalizer.py (custom module)
    What: normalize(text: str) -> str — preprocesses Nahuatl text before sending to XTTS-v2.
    Rules applied: lowercase → hu+vowel → w+vowel → x → sh → tz → ts → saltillo dropped → tl kept as-is
    Status: Built and tested. Working correctly.

11. termux-open (Android playback)
    What: Termux utility that triggers Android's native media player intent for a file.
    Why needed: termux-media-player requires play subcommand and has issues with WAV from private Termux storage. termux-open passes the file to whatever music app the user has installed.

BUILD SEQUENCE

Step 1 — Reference Voice Extraction [DONE]
  Tools: yt-dlp, ffmpeg
  Output: reference_voice.wav (25s, 22050 Hz, mono)
  Status: Complete. full_audio.wav (1:47 backup) and reference_voice.wav (25s clip) in project folder.

Step 2 — Laptop Server Setup [DONE]
  Actions completed:
    a. SSH into laptop via Tailscale: ssh wslinux@100.68.100.23 (alias: ssh ws)
    b. Activate venv: source ~/nllb-env/bin/activate
    c. Install packages: torch/torchaudio from PyTorch wheel server, then coqui-tts/fastapi/uvicorn from PyPI
    d. Created ~/Tlazanilohni_server/
    e. Copied reference_voice.wav to laptop via scp

Step 3 — Build tts_server.py [DONE]
  FastAPI app with POST /synthesize and GET /health
  Loads XTTS-v2 at startup (gpu=True); on each request calls tts.tts_to_file(); returns WAV bytes
  Server running via nohup on port 8000 (not tmux — survives SSH disconnect but not reboot)

Step 4 — Build normalizer.py [DONE]
  normalize(text) applies Nahuatl grapheme rules before sending to Spanish-trained XTTS-v2.
  Tested and working.

Step 5 — Build main.py [DONE]
  Usage: py3 main.py "Nimitztlazohtla"
  Flow: text → normalize → POST /synthesize → save to /storage/emulated/0/Music/Tlazanilohni/ → play via termux-open

Step 6 — End-to-End Test [MOSTLY DONE]
  Synthesis confirmed working: server receives text, XTTS-v2 generates audio, WAV returned and saved.
  Audio playback: not yet confirmed with sound — termux-open fix applied, needs verification.

Step 7 — Optional: GUI Wrapper [FUTURE]
  Wrap CLI in a simple tkinter window: text input box + "Read Aloud" button + playback controls.

COMPATIBILITY PATCHES (coqui-tts vs transformers)

coqui-tts 0.27.5 has a packaging bug: it imports internal utility functions from transformers that were removed or never existed in any single version. These must be patched directly in the installed site-packages. All patches are in patch_coqui.py, run via: lpy $TPROJ/patch_coqui.py

Patch 1 — TTS/__init__.py (missing stubs)
  Problem: Imports is_torchcodec_available and is_torch_greater_or_equal from transformers — neither exists in transformers 4.37.2 or 4.44.2.
  Fix: Remove those names from the import block; prepend stub functions (both return True) at top of file. Also bypass raise ImportError(TORCHCODEC_IMPORT_ERROR) with pass.

Patch 2 — TTS/tts/layers/tortoise/autoregressive.py (removed symbol)
  Problem: from transformers.pytorch_utils import isin_mps_friendly as isin — isin_mps_friendly was removed from transformers.
  Fix: Replace with isin = torch.isin (equivalent functionality).

Patch 3 — TTS/tts/datasets/dataset.py (missing symbol)
  Problem: from transformers.utils.import_utils import is_torch_greater_or_equal — does not exist.
  Fix: Replace import line with inline stub: def is_torch_greater_or_equal(v): return True

Patch 4 — transformers/generation/utils.py (NoneType errors at synthesis time)
  Problem A: self.generation_config._from_model_config raises AttributeError when generation_config is None.
  Fix A: Wrap with None guard: (self.generation_config is not None and self.generation_config._from_model_config)
  Problem B: _validate_model_class raises TypeError because GPT2InferenceModel does not satisfy the check.
  Fix B: Insert early return at line after def _validate_model_class(self):

Patch 5 — TTS/tts/layers/xtts/gpt_inference.py (generation_config and missing methods)
  Problem A: generation_config property can return None (parent class setter can set it to None), causing AttributeError.
  Fix A: Add generation_config property and setter to GPT2InferenceModel; getter reinitializes _gen_cfg if None.
  Problem B: NotImplementedError: A model class needs to define a prepare_inputs_for_generation method.
  Fix B: Add prepare_inputs_for_generation method to GPT2InferenceModel using standard GPT-2 KV-cache pattern.
  Problem C: _validate_model_class raises on the class itself.
  Fix C: Add def _validate_model_class(self): return to GPT2InferenceModel.

patch_coqui.py is idempotent — safe to re-run after any package update. Each patch checks if it is already applied before modifying the file.

AUDIOBOOK PIPELINE — PHASE 2

Goal: convert parsed Nahuatl books (already in Google Sheets) into audiobook MP3s, playable like a podcast on Android.

Data source

Books are already parsed sentence-by-sentence into Google Sheets in Drive folder 1LW0qwgf58wUX1UhpL7K2Y_6gW5x_NAoF.
Column B (Nahuatlahtolli) contains the Nahuatl text. All other columns (Spanish translation, BLEU, Claude analysis) are ignored for TTS.

Current books ready:
  Eduardo — Cenyahtoc Cintli Tonacayo: ~1,500 sentences. Sheet ID: 1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw
  Crispin_Carlos — Nahuatl Tequitl: ~3,800 sentences, 228 chapter breaks. Sheet ID: 1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg (tab: Crispin)
  14 PDFs in Drive folder 1AFp-WuRMnhmV05km0-4D-7cQQWRdIa2a — being progressively transcribed into the same format.

Script spec — audiobook_builder.py

  Usage: py3 audiobook_builder.py --sheet <ID> --tab <name> --book <title>

  1. Read column B from Google Sheet (skip header rows 0-2, skip empty cells)
  2. Classify each row: section title (len < 40, no . , ? ! -) vs sentence
  3. For each sentence: normalize → POST /synthesize → save tmp_NNNN.wav
  4. On section title: ffmpeg-concat accumulated WAVs → chapter_NNN_<title>.mp3; clear buffer
  5. Write progress.json after every sentence (stores last_row and chapter index)
  6. On restart: read progress.json and resume from last processed row
  7. Generate playlist.m3u listing all chapter MP3s in order

Output structure

  /storage/emulated/0/Music/Tlazanilohni/
    Cenyahtoc_Cintli_Tonacayo/
      chapter_001_Tlazcamatiliztli.mp3
      chapter_002_Tlapannextiliztli.mp3
      ...
      playlist.m3u
    Nahuatl_Tequitl_Crispin/
      chapter_001_Tlazcamatiliztli.mp3
      ...
      playlist.m3u

  M3U playlist is playable in VLC, Musicolet, or any Android music app — chapter skip, position memory, speed control.

Synthesis time estimates (RTX 3060, ~3 sec/sentence):
  Eduardo: ~75 minutes GPU time → ~75 minutes of audio
  Crispin_Carlos: ~190 minutes GPU time → ~190 minutes of audio
  Run overnight with resume support — progress.json ensures no re-synthesis if interrupted.

Error handling

  Server timeout → retry 3x with 5s delay, then skip sentence and log to errors.txt
  ffmpeg failure → log and continue to next chapter

NORMALIZER PHONOLOGY — KNOWN GAPS

The normalizer currently maps Nahuatl graphemes to Spanish-friendly text before sending to XTTS-v2 (language="es"). Two sounds are rendered incorrectly under Spanish rules.

Problem 1 — "h" is silent in Spanish TTS

Nahuatl "h" = voiceless glottal fricative /h/ (like English "h" in "hat"). Literature: Andrews (1975) Introduction to Classical Nahuatl, Carochi (1645) Arte de la lengua mexicana, Sullivan (1992) A Scribe's Wisdom, INALI orthographic conventions — all confirm "h" is a distinct Nahuatl phoneme, never silent.

Spanish "h" is always completely silent. XTTS-v2 with language="es" produces no sound for "h". This is the more urgent of the two problems.

Options:
  A. Substitute h → j in normalizer. Spanish "j" = /x/ (velar fricative, like "ch" in German "Bach") — too harsh but audible. Acceptable short-term approximation.
  B. Switch TTS language to "en" (English). English "h" = /h/ exactly. Tradeoff: English vowel rules differ from Nahuatl's 5-vowel system, but XTTS-v2 voice cloning may compensate by pulling vowel quality toward the reference speaker.
  C. Long term: use eSpeak-ng (supports Nahuatl "nah" language code) as text→phoneme stage, feed IPA output to XTTS-v2.

Recommended short term: test option A (h→j) and option B (language="en") side by side on 5 sentences.

Problem 2 — "tl" lateral affricate

Nahuatl "tl" = voiceless lateral affricate /tɬ/ — a hallmark Nahuatl sound with no direct Spanish equivalent. However, Mexican Spanish speakers naturally produce /tɬ/ in Nahuatl loanwords (atole, axolotl, tlapalería). XTTS-v2 trained on Mexican Spanish likely handles "tl" adequately.

Options:
  A. Leave "tl" as-is — test first before changing anything.
  B. Map word-final "tl" → "thl" — some practitioners report this better approximates the lateral fricative in text-based TTS.
  C. Long term: eSpeak-ng "nah" phonemizer.

Recommended short term: leave "tl" unchanged and evaluate from audio output.

HOW TO RUN THE APP

Requirements

  Android tablet with Termux installed
  Windows laptop with WSL2 Ubuntu, ~/nllb-env venv, coqui-tts installed and patched
  Both devices connected to Tailscale (laptop IP: 100.68.100.23)
  Laptop must be on and not sleeping

Step 1 — Check if the server is already running

Open a native Termux session and run:

  curl http://100.68.100.23:8000/health

If you get {"status":"ok"} → server is running, skip to Step 3.
If you get a connection error → proceed to Step 2.

Step 2 — Start the laptop TTS server

In native Termux (not inside PRoot):

  lsh "cd ~/Tlazanilohni_server && source ~/nllb-env/bin/activate && nohup uvicorn tts_server:app --host 0.0.0.0 --port 8000 > ~/Tlazanilohni_server/tts.log 2>&1 &"

Wait 10 seconds then verify with the health check again. First start after a laptop reboot also loads XTTS-v2 (~10 seconds).

Step 3 — Synthesize speech

In native Termux:

  py3 $TPROJ/main.py "Nimitztlazohtla"

Or run interactively (prompts you to type text):

  py3 $TPROJ/main.py

Expected output:
  Input:      Nimitztlazohtla
  Normalized: nimitztlasohtla
  Saved: /storage/emulated/0/Music/Tlazanilohni/Nimitztlazohtla.wav

Android opens audio automatically via default media player.

Step 4 — Find saved audio files

  Path: /storage/emulated/0/Music/Tlazanilohni/
  Access: Files app → Internal Storage → Music → Tlazanilohni → tap any .wav file

Troubleshooting

  Connection error on health check → server not running, do Step 2
  ModuleNotFoundError → use py3 (Termux Python), not python3 (PRoot Python)
  Audio saved but nothing plays → open manually: Files app → Music → Tlazanilohni
  Server errors after pip update → run: lpy $TPROJ/patch_coqui.py then restart server
  lsh or lpy command not found → you are inside PRoot, switch to native Termux session

Quick reference — all commands

  curl http://100.68.100.23:8000/health
  lsh "cd ~/Tlazanilohni_server && source ~/nllb-env/bin/activate && nohup uvicorn tts_server:app --host 0.0.0.0 --port 8000 > ~/Tlazanilohni_server/tts.log 2>&1 &"
  py3 $TPROJ/main.py "Your Nahuatl text here"
  lpy $TPROJ/patch_coqui.py
  lsh "tail -30 ~/Tlazanilohni_server/tts.log"

KEY CONSTRAINTS AND DECISIONS

No paid APIs
  ElevenLabs was considered and rejected. All tools used are free and open-source.

XTTS-v2 language setting
  We use language='es' (Spanish) since Nahuatl has no XTTS-v2 code. Spanish is the closest supported language phonetically. normalizer.py bridges the phoneme gap before text reaches the server.

Output saved to shared storage
  Audio is saved to /storage/emulated/0/Music/Tlazanilohni/ (not Termux private storage) so files are visible in the Samsung Files app and any media player can access them.

Server started with nohup (not tmux)
  The server survives SSH disconnect (nohup backgrounds the process) but does not survive a laptop reboot. To restart: lsh "cd ~/Tlazanilohni_server && source ~/nllb-env/bin/activate && nohup uvicorn tts_server:app --host 0.0.0.0 --port 8000 > ~/Tlazanilohni_server/tts.log 2>&1 &"

Workflow: two Termux sessions
  Session 1: SSH to laptop (lsh or ssh ws) — for server operations, patches, log checks.
  Session 2: Native Termux — for running py3 main.py, pkg installs, scp commands. lpy and lsh aliases defined in ~/.bashrc.

ffmpeg full path required from PRoot
  Inside PRoot Distro, /data/data/com.termux/files/usr/bin/ may not resolve via which. Always use full path.

pkg install must run from native Termux
  Running pkg from inside PRoot invokes Debian's dpkg which requires superuser. Always open a native Termux session for package installs.

WSL2 server must bind to 0.0.0.0
  --host 0.0.0.0 required so the port is reachable from Tailscale. Binding to 127.0.0.1 would only allow localhost connections inside WSL2.

OPEN QUESTIONS

1. Audio playback: termux-open fix applied; audible playback not yet confirmed. May need to manually open file from Files app → Music → Tlazanilohni if termux-open does not trigger sound.

2. Nahuatl 'tl' pronunciation: XTTS-v2 with Spanish rules will likely not produce the correct lateral affricate /tɬ/. May need to test substitutions like 'thl' and compare with keeping 'tl'.

3. Server persistence: nohup keeps server alive through SSH disconnect but not laptop reboot. A Windows Startup Task or WSL2 boot script would make this automatic.

4. Reference voice quality: The 25s clip is clean speech. If voice clone quality is unsatisfactory, try a different timestamp in full_audio.wav.

5. Saltillo handling: Currently the saltillo (ʼ) is dropped. Some Nahuatl varieties use it phonologically. May need to experiment with a glottal stop approximation.

SESSION LOG

Session 2026-09-19 (session 1)
  Defined project scope and name (Tlazanilohni). Bootstrapped .claude/commands/. Created project plan. Designed 5-phase architecture.

Session 2026-09-19 (session 2)
  Confirmed TTS engine: Coqui XTTS-v2 on laptop GPU. Installed yt-dlp (Termux pip) and ffmpeg (Termux pkg). Downloaded full YouTube reference audio. Clipped 25s reference_voice.wav at 22050 Hz mono.

Session 2026-09-20
  Wrote full project plan to this Google Doc via service account API. Built write_plan_to_doc.py with HEADING_1/2/3 styles and TOC hyperlinks.

Session 2026-09-23 (session 1)
  Verified reference_voice.wav. SSHed to laptop. Fixed pip install TTS (split torch/torchaudio from PyTorch wheel server vs. coqui-tts from PyPI). Installed all server deps. Copied reference_voice.wav to laptop. Built tts_server.py.

Session 2026-09-23 (session 2 & 3)
  Applied Patches 1–3 (init, autoregressive, dataset). Diagnosed and applied Patch 4 (generation/utils.py — None guard and _validate_model_class). Began applying Patch 5 (gpt_inference.py generation_config property). Built normalizer.py and main.py. Confirmed server health endpoint working.

Session 2026-09-27
  Applied Patch 5 fully: added prepare_inputs_for_generation to GPT2InferenceModel (was the final blocker). Confirmed server starts and loads XTTS-v2 successfully. End-to-end synthesis confirmed: Nimitztlazohtla → WAV generated, returned, saved. Fixed main.py: save path changed to /storage/emulated/0/Music/Tlazanilohni/ (Files app visible); playback switched from termux-media-player to termux-open. Documented all 5 patches in patch_coqui.py (idempotent, safe to re-run). Discovered and documented audiobook pipeline plan using existing Google Sheets data (books already parsed sentence by sentence). Addressed normalizer phonology gaps for h and tl.

Session 2026-09-28
  Major normalizer improvements — all confirmed working by audio test:
  h→j substitution (lookbehind preserves sh and ch). Silent-u rule: vowel+uh → vowel+h (queniuhqui→kenijki, nouhquiya→nohkiya). Em-dash and en-dash stripped (were causing XTTS-v2 hallucinations). Hyphen stripped (was spoken as "menos"). Trailing period stripped (was causing audio artifact). Multiple spaces and embedded newlines collapsed. Inverted Spanish openers added (¿/¡) for correct interrogative and exclamatory intonation.
  main.py rewritten with sentence splitting and WAV concatenation: XTTS-v2 hallucinates beyond ~250 chars; synthesize() now splits on sentence-ending punctuation, synthesizes each separately, and concatenates via Python wave module. Multi-sentence paragraphs and full dialogue passages now work cleanly. Audio quality confirmed excellent.

Session 2026-09-28 (session 2)
  Built audiobook_builder.py — full pipeline from Google Sheet to MP3 audiobook chapters. CLI args: --sheet, --tab, --book. Reads column B (Nahuatlahtolli), skips header rows. Classifies rows as section titles (chapter breaks) vs sentences. Synthesizes each sentence via server with retry logic. Flushes chapter WAVs to MP3 via ffmpeg at each chapter break. Writes progress.json after every sentence for resume support — restart the same command after any interruption. Generates playlist.m3u for podcast-like playback in any music app. Syntax-checked and ready to run. Eduardo (~1,500 sentences) is the first dry run target.

Session 2026-09-28 (session 3)
  Eduardo audiobook completed: 1,517 sentences, 15 chapters, playlist.m3u written — first full Nahuatl audiobook produced end-to-end. Added cc→cj rule to normalizer: Nahuatl geminate /k/ (nocca) was rendered as plain /k/ (noka) by Spanish TTS; correct pronunciation is aspirated /kx/ (nocja); rule inserted before the iuh rule. Verified: nocca→nocja, Huacca→wacja, ticcaqui→ticjaki. Crispin_Carlos audiobook started overnight (~3,800 sentences, ~190 min GPU). Google Drive storage discussed as alternative to tablet local storage — pending user sharing a Drive folder with the service account.
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

    if text == 'Tlazanilohni — Modern Nahuatl Text-to-Speech App':
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

seen_texts      = set()
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
