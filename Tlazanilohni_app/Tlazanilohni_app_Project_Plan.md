# Tlazanilohni App — Project Plan

**Created:** 2026-09-19
**Last updated:** 2026-09-19 (session 2)
**Status:** Active

---

## Overview

A text-to-speech (TTS) app that reads modern Nahuatl aloud using a cloned voice extracted from a reference YouTube video. "Tlazanilohni" means "the one who reads aloud" in Nahuatl. The app targets the modern spoken Nahuatl dialect (distinct from the classical Nahuatl used in Nahuatl_Translator2).

---

## Checkpoint — 2026-09-19

### Work completed this session

- Defined project scope, name ("Tlazanilohni"), and folder location: `Macehualtlahtol/Tlazanilohni_app/`
- Bootstrapped `.claude/commands/` (copied parent workspace commands)
- Created `.claude/settings.local.json` with baseline permissions
- Created this plan file (`Tlazanilohni_app_Project_Plan.md`)
- Designed a full 5-phase architecture plan (see below)

### Current state

Project is at planning stage only — no code written yet. The architecture is defined and agreed upon.

### Next steps

1. **Resolve TTS engine decision** — user to confirm whether to use ElevenLabs API (fast, cloud) or Coqui XTTS-v2 (local, offline). This gates everything else.
2. **Extract reference voice** — use `yt-dlp` + `ffmpeg` to download and clip a 15–30 sec clean speech segment from `https://youtu.be/PbEf5jDd_pk`; save as `reference_voice.wav`
3. **Set up TTS engine** — if ElevenLabs: create account, clone voice via API; if XTTS-v2: install in PRoot Debian, test on CPU
4. **Build `normalizer.py`** — Nahuatl grapheme-to-phoneme normalizer (handle `x→sh`, saltillo, `tl`, `tz`, etc.)
5. **Build `voice_engine.py`** — adapter wrapping chosen TTS backend
6. **Build `main.py`** — CLI entry point: text input → normalized text → TTS → audio file + playback
7. **Test with 10–20 modern Nahuatl sentences** — validate pronunciation and intonation quality
8. **Optional:** Add `tkinter` GUI wrapper

### Notes

- **Dialect note:** The Nahuatl in this app is modern spoken Nahuatl, NOT the classical/literary Nahuatl used in `Nahuatl_Translator2`. They use different orthographic conventions and vocabulary.
- **Reference video:** `https://youtu.be/PbEf5jDd_pk?si=BDdMWAoAgu4yQiKQ` — target intonation/voice style
- **Hardware constraint:** Device is ARM aarch64 (Android/Termux). Local TTS models run slow (~30–60s/sentence on CPU). ElevenLabs API avoids this entirely.
- **Nahuatl phoneme mapping strategy:** Spanish-trained TTS models handle most Nahuatl sounds adequately. Key exceptions: `x`=/ʃ/ ("sh"), `tl`=/tɬ/ (no equivalent), saltillo /ʔ/ (glottal stop). The normalizer handles these before sending to TTS.
- **Interpreter:** Always use Termux Python `/data/data/com.termux/files/usr/bin/python3`. Selenium/XTTS-v2 local path uses PRoot Debian `/usr/bin/python3`.

---

## Architecture Reference

```
Tlazanilohni_app/
├── main.py              ← CLI entry: text input → audio output
├── normalizer.py        ← Nahuatl grapheme → TTS-friendly text
├── voice_engine.py      ← ElevenLabs or XTTS adapter
├── reference_voice.wav  ← extracted from YouTube reference video
├── output/              ← generated audio files
└── CLAUDE.md
```

**Flow:** User text → `normalizer.py` → `voice_engine.py` → audio playback + saved file

---

## Checkpoint — 2026-09-19 (session 2)

### Work completed this session

- Confirmed TTS engine: **Coqui XTTS-v2** (free, local, no ElevenLabs) running on **laptop GPU (RTX 3060)** via Tailscale
- Revised architecture: laptop runs a FastAPI TTS server; Android calls it over Tailscale HTTP (`http://100.68.100.23:8000`)
- Installed `yt-dlp` in Termux Python (`pip3 install yt-dlp`) — v2026.08.19
- Installed `ffmpeg` in Termux native (v8.1.2-5) via `pkg install ffmpeg` — had to run from native Termux session, not PRoot
- Downloaded full audio from reference YouTube video (`https://youtu.be/PbEf5jDd_pk`) → `full_audio.wav` (1:47, 20 MB)
- Clipped 25-second reference segment → `reference_voice.wav` (1.1 MB, 22050 Hz mono) — format required by XTTS-v2
- ffmpeg binary location confirmed: `/data/data/com.termux/files/usr/bin/ffmpeg`

### Current state

- `reference_voice.wav` exists in project folder, ready to upload to laptop for voice cloning
- `full_audio.wav` retained as backup in case re-clipping from a different timestamp is needed
- No Python code written yet; audio extraction pipeline complete

### Next steps

1. **Verify `reference_voice.wav`** — user plays the clip and confirms it contains clear Nahuatl speech (no music, no noise). Re-clip from `full_audio.wav` if needed using a different `-ss` timestamp.
2. **SSH into laptop** — `ssh wslinux@100.68.100.23` (activate `~/nllb-env`)
3. **Install XTTS-v2 on laptop** — `pip install TTS torch torchaudio fastapi uvicorn` in `nllb-env`
4. **Copy `reference_voice.wav` to laptop** — `scp reference_voice.wav wslinux@100.68.100.23:~/Tlazanilohni_server/`
5. **Build `tts_server.py`** — FastAPI server on laptop: POST `/synthesize` → returns audio bytes using XTTS-v2 + reference voice
6. **Start server in tmux on laptop** — persistent, survives SSH disconnect
7. **Build `normalizer.py`** on Android — Nahuatl grapheme normalizer (`x→sh`, saltillo, `tl`, `tz`)
8. **Build `main.py`** on Android — CLI: text input → normalize → HTTP POST to laptop → play audio + save to `output/`
9. **End-to-end test** — type Nahuatl sentence on Android, hear audio back

### Notes

- **ffmpeg from PRoot:** Use full path `/data/data/com.termux/files/usr/bin/ffmpeg` — `which ffmpeg` does not resolve inside PRoot even though Termux bin is in PATH
- **pkg install must be run from native Termux** — running `pkg` from inside PRoot hits PRoot's dpkg and fails with "superuser privilege" error
- **XTTS-v2 reference audio spec:** 22050 Hz, mono, WAV — already formatted correctly in `reference_voice.wav`
- **Laptop SSH:** `ssh wslinux@100.68.100.23` via Tailscale; activate venv with `source ~/nllb-env/bin/activate` before any pip/python commands
- **Server port:** 8000 (FastAPI default); ensure it's not blocked by Windows firewall for WSL2

---

## Checkpoint — 2026-09-20

### Work completed this session

- Wrote full project plan to Google Doc (`1Sfea88PHnQDlLE1LR5dkfs5aZ_FDHSgKZEnCz-Z8Wss`) via service account API
- Plan includes: project overview, system architecture diagram, file structure, rationale for every tool/package (yt-dlp, ffmpeg, XTTS-v2, PyTorch, FastAPI, Uvicorn, Tailscale, requests, normalizer.py), 7-step build sequence with statuses, constraints, and open questions
- Created `write_plan_to_doc.py` — script that clears the Doc, inserts full content, and applies HEADING_1/HEADING_2/HEADING_3 styles via Google Docs API batchUpdate

### Current state

- Project is fully planned and documented in Google Docs
- Reference audio extraction complete: `full_audio.wav` (1:47 backup) and `reference_voice.wav` (25s, 22050 Hz mono) both present in project folder
- No Python TTS code written yet
- Laptop server not yet set up

### Next steps

1. **Verify `reference_voice.wav`** — play the clip; confirm clean Nahuatl speech. Re-clip from `full_audio.wav` with a different `-ss` offset if needed.
2. **SSH into laptop** — `ssh wslinux@100.68.100.23`, then `source ~/nllb-env/bin/activate`
3. **Install server dependencies on laptop** — `pip install TTS torch torchaudio fastapi uvicorn --index-url https://download.pytorch.org/whl/cu121`
4. **Copy `reference_voice.wav` to laptop** — `scp reference_voice.wav wslinux@100.68.100.23:~/Tlazanilohni_server/`
5. **Build `tts_server.py`** — FastAPI endpoint POST `/synthesize` → XTTS-v2 → returns WAV bytes
6. **Launch server in tmux** — `uvicorn tts_server:app --host 0.0.0.0 --port 8000`
7. **Build `normalizer.py`** on Android — grapheme rules for Nahuatl → TTS-friendly text
8. **Build `main.py`** on Android — CLI: normalize → POST → play + save audio
9. **End-to-end test** — Nahuatl text in, audio out, within ~5 seconds

### Notes

- `write_plan_to_doc.py` uses the Financial_Analysis_App service account key — this is intentional (shared key across workspace projects)
- Google Doc styled with Heading 1 (title), Heading 2 (major sections), Heading 3 (build steps) — ready to share with stakeholders
- Next session should start by verifying the reference audio, then move straight to laptop SSH setup

---

## Checkpoint — 2026-09-23 (session 2)

### Work completed this session

- Verified `reference_voice.wav` — confirmed clean Nahuatl speech, good for voice cloning
- SSHed into laptop (`wslinux@100.68.100.23`), activated `nllb-env`
- Fixed `pip install TTS` failure: `--index-url` replaced PyPI entirely; split into two installs — `torch`/`torchaudio` from PyTorch wheel server, `coqui-tts`/`fastapi`/`uvicorn` from PyPI
- Installed all server dependencies on laptop: `coqui-tts`, `torch`, `torchaudio`, `fastapi`, `uvicorn`
- Copied `reference_voice.wav` to `~/Tlazanilohni_server/` on laptop via `scp` from Android Termux
- Wrote `tts_server.py` — FastAPI server with `POST /synthesize` (text → WAV bytes via XTTS-v2 zero-shot voice cloning) and `GET /health`

### Current state

- Laptop has all dependencies installed and `reference_voice.wav` in place
- `tts_server.py` written and copied to laptop — not yet launched
- Android side: no `normalizer.py` or `main.py` yet
- XTTS-v2 model not yet downloaded (happens on first server start)

### Next steps

1. **Copy `tts_server.py` to laptop** — `scp tts_server.py wslinux@100.68.100.23:~/Tlazanilohni_server/`
2. **Launch server in tmux** — `tmux new -s tts`, `source ~/nllb-env/bin/activate`, `uvicorn tts_server:app --host 0.0.0.0 --port 8000`; wait for model download (~2 GB) and `Uvicorn running` message
3. **Test health endpoint** — `curl http://100.68.100.23:8000/health` from Android
4. **Build `normalizer.py`** on Android — grapheme rules: `x→sh`, `tl→tl` (or IPA workaround), saltillo drop/glottal, `tz`, `hu→w`
5. **Build `main.py`** on Android — CLI: text input → normalize → POST `/synthesize` → play audio + save to `output/`
6. **End-to-end test** — type a Nahuatl sentence on Android, hear audio back within ~5 seconds

### Notes

- `coqui-tts` is the maintained community fork of the archived Coqui TTS; imports as `from TTS.api import TTS` — same API
- Zero-shot voice cloning used (no fine-tuning): reference audio provides voice fingerprint only, no transcript needed
- Language set to `"es"` (Spanish) as closest XTTS-v2 option for Nahuatl; normalizer handles phoneme gaps before text reaches server
- First server start downloads XTTS-v2 model (~2 GB) — subsequent starts load from cache

---

## Checkpoint — 2026-09-23 (session 3)

### Work completed this session

- Confirmed `reference_voice.wav` clean — step 1 done
- SSHed into laptop, activated `nllb-env` — step 2 done
- Fixed `pip install TTS` failure: `--index-url` replaced PyPI entirely; correct fix is to split installs: torch/torchaudio from PyTorch wheel server separately, then `coqui-tts fastapi uvicorn` from PyPI
- Diagnosed `coqui-tts` broken against all transformers versions — it imports functions that don't exist in any single version (`isin_mps_friendly` removed in newer, `is_torch_greater_or_equal`/`is_torchcodec_available` not in older)
- Patched `TTS/tts/layers/tortoise/autoregressive.py` — added try/except fallback for `isin_mps_friendly` (uses `torch.isin` instead)
- Patched `TTS/__init__.py` — removed `is_torch_greater_or_equal` from import block and prepended stub `def is_torch_greater_or_equal(v): return True`
- Copied `tts_server.py` to laptop `~/Tlazanilohni_server/`
- Confirmed `(nllb-env)` venv is active on laptop

### Current state

- All dependencies installed on laptop (`coqui-tts`, `torch`, `torchaudio`, `fastapi`, `uvicorn`, `transformers` latest)
- Two coqui-tts source files patched for transformers compatibility
- Server still not launching — `is_torchcodec_available` is the next missing import from `TTS/__init__.py` line 5
- Need to see full import block (lines 1–20 of `TTS/__init__.py`) to patch all missing functions at once

### Next steps

1. **Show full import block** — `head -20 /home/wslinux/nllb-env/lib/python3.12/site-packages/TTS/__init__.py`
2. **Patch all missing imports at once** — remove all non-existent functions from the import and add stubs
3. **Launch server** — `uvicorn tts_server:app --host 0.0.0.0 --port 8000`; wait for XTTS-v2 model download (~2 GB)
4. **Test health endpoint** — `curl http://100.68.100.23:8000/health` from Android
5. **Build `normalizer.py`** on Android
6. **Build `main.py`** on Android
7. **End-to-end test**

### Notes

- `coqui-tts 0.27.5` has a genuine packaging bug: imports transformers internal utilities that don't exist in any single version. Patching the source files is the correct workaround — do not attempt to find a "compatible" transformers version, none exists.
- Always activate venv before running anything on laptop: `source ~/nllb-env/bin/activate`
- File permissions on coqui-tts source files are restrictive — always run `chmod u+rw <file>` before patching

---

## Checkpoint — 2026-09-27

### Work completed this session

- Diagnosed remaining coqui-tts/transformers incompatibility: `NotImplementedError: prepare_inputs_for_generation` — GPT2InferenceModel was missing this required method
- Updated `patch_coqui.py` to add `prepare_inputs_for_generation` to GPT2InferenceModel in `gpt_inference.py`; method delegates to standard GPT-2 KV-cache pattern
- Confirmed all prior patches still applied: `__init__.py`, `autoregressive.py`, `dataset.py`, `generation/utils.py` all already patched
- Patch successfully added `prepare_inputs_for_generation` — confirmed by patch output: "added prepare_inputs_for_generation to GPT2InferenceModel"
- Confirmed laptop server directory `~/Tlazanilohni_server/` exists with `reference_voice.wav` and `tts_server.py`
- Copied updated `tts_server.py` to laptop via `scp`
- Started Uvicorn server on laptop — confirmed running: `Uvicorn running on http://0.0.0.0:8000`
- **End-to-end synthesis worked**: `py3 main.py "Nimitztlazohtla"` → server synthesized WAV → file saved
- Fixed `main.py` playback: `termux-media-player` requires `play <file>` subcommand, not bare filename
- Fixed `main.py` save path: changed from relative `output/` (saves to Termux private sandbox) to `/storage/emulated/0/Music/Tlazanilohni/` (visible in Files app)
- Fixed `main.py` playback to use `termux-open` (Android native media player intent) instead of `termux-media-player`
- transformers downgraded to 4.37.2 on laptop (from 4.44.2) as intermediate step; patches cover the compatibility gap
- Rewrote `write_plan_to_doc.py` with full updated content: new COMPATIBILITY PATCHES section documenting all 5 patches, SESSION LOG section, BUILD SEQUENCE statuses updated (Steps 1–5 DONE), revised FILE STRUCTURE and KEY CONSTRAINTS
- Ran `write_plan_to_doc.py` directly via Bash tool (no longer requires user to type `py3` — Claude can run it directly)
- Established: Google Doc updates can be triggered by Claude directly; user does not need to run py3 commands for doc updates

### Current state

- Laptop server is running (Uvicorn on port 8000, XTTS-v2 loaded with reference voice)
- `patch_coqui.py` fully covers all known coqui-tts/transformers incompatibilities
- `main.py` synthesizes audio and saves to `/storage/emulated/0/Music/Tlazanilohni/` (visible in Files app)
- Playback via `termux-open` not yet confirmed — last test did not produce audible output
- `normalizer.py` working correctly

### Next steps

1. **Confirm audio playback** — run `py3 $TPROJ/main.py "Nimitztlazohtla"` and verify sound plays via Android media player
2. **If termux-open fails** — manually open the file from Files app → Music → Tlazanilohni → tap the WAV file
3. **Test more sentences** — try longer Nahuatl phrases; verify normalizer handles `x`, `hu+V`, `tz`, saltillo correctly
4. **Check server persistence** — confirm server survives SSH disconnect (running via nohup, not tmux); add tmux session if needed for resilience
5. **Write a startup script** — one-line command to (re)start the laptop server without SSH session
6. **Optional:** Build simple input loop in `main.py` — keep running, accept multiple sentences without restarting

### Notes

- Server started with `nohup uvicorn ... &` — not in tmux; will survive SSH disconnect but not laptop reboot
- To restart server after reboot: `lsh "cd ~/Tlazanilohni_server && source ~/nllb-env/bin/activate && nohup uvicorn tts_server:app --host 0.0.0.0 --port 8000 > ~/Tlazanilohni_server/tts.log 2>&1 &"`
- transformers 4.37.2 installed on laptop; coqui-tts warns it wants ≥4.57 — ignore, patches cover the gap
- Output files go to `/storage/emulated/0/Music/Tlazanilohni/` — accessible in Samsung Files app under Music

---

## Checkpoint — 2026-09-27 (session 2)

### Work completed this session

- Discovered that books are already parsed sentence-by-sentence into Google Sheets (Drive folder `1LW0qwgf58wUX1UhpL7K2Y_6gW5x_NAoF`) — PDF extraction pipeline is NOT needed
- Read and analyzed both parsed sheets via Drive/Sheets API:
  - `Cenyahtoc Cintli Tonacayo - Eduardo`: 1,520 rows, ~1,517 Nahuatl sentences (col B: `Nahuatlahtolli`)
  - `Nahuatl Tequitl - Crispin_Carlos`: 4,037 rows, ~3,803 sentences, 228 section titles — use this one
- Confirmed data structure: col B = Nahuatl text; other cols = Spanish translation, BLEU scores, Claude analysis (not needed for TTS)
- Confirmed chapter break strategy: section titles are short entries (< 40 chars) with no terminal punctuation — 228 of them in Crispin_Carlos (natural chapter breaks matching the book's own structure)
- Refined section title heuristic: exclude entries with commas, question marks, dashes — those are dialogue lines, not headings
- Confirmed 14 PDFs in books folder being progressively transcribed into the same sheet format
- Addressed normalizer phonology gaps: "h" and "tl" both render incorrectly under Spanish TTS rules — documented refinement options (see Normalizer Phonology section below)

### Current state

- Pipeline design complete: Google Sheets → sentence list → normalize → /synthesize → WAVs → ffmpeg concat → MP3 chapters + M3U playlist
- Two books ready to process: Eduardo (~1,500 sentences) and Crispin_Carlos (~3,800 sentences)
- Normalizer has known phonology gaps for "h" and "tl" — refinement planned before build
- No code written yet for the audiobook builder

### Next steps

1. **Refine normalizer** — fix "h" (silent in Spanish TTS, should be /h/) and validate "tl" handling before building the audiobook pipeline
2. **Test normalizer changes** — synthesize 3–5 sentences with before/after comparison
3. **Build `audiobook_builder.py`** — see detailed spec below
4. **Run on Eduardo first** (smaller, ~1,500 sentences, ~75 min synthesis) — validate output before processing Crispin_Carlos
5. **Run on Crispin_Carlos** (~3,800 sentences, ~3 hrs synthesis) — overnight run with resume support
6. **Verify M3U playlist** plays correctly in VLC or Musicolet on Android

### Audiobook Builder — Detailed Spec

**Script:** `audiobook_builder.py`

**Usage:**
```
py3 audiobook_builder.py --sheet <SHEET_ID> --tab <TAB_NAME> --book <TITLE>
```

**Data reading:**
- Read column B (`Nahuatlahtolli`) from Google Sheet, skip rows 0–2 (header block)
- Skip empty cells
- Classify each row: **section title** (len < 40, no `.`, `,`, `?`, `!`, `-`) vs **sentence**

**Synthesis loop:**
- For each sentence: normalize → POST `/synthesize` → save as `tmp_NNNN.wav`
- On section title: ffmpeg-concat accumulated WAVs → `chapter_NNN_<title>.mp3`; clear buffer
- Write `progress.json` after every sentence: `{sheet, tab, last_row, chapter}`
- On restart: read `progress.json` → resume from `last_row`, skip already-processed sentences

**Output structure:**
```
/storage/emulated/0/Music/Tlazanilohni/
  <BookTitle>/
    chapter_001_Tlazcamatiliztli.mp3
    chapter_002_Tlapannextiliztli.mp3
    ...
    playlist.m3u
```

**M3U playlist:** lists all chapter MP3s in order — playable in VLC, Musicolet, any music app.

**Error handling:**
- Server timeout → retry 3× with 5s delay, then skip sentence and log to `errors.txt`
- ffmpeg failure → log, continue to next chapter

### Normalizer Phonology — Known Gaps and Refinement Plan

**Problem 1: "h" is silent in Spanish TTS**
Nahuatl "h" = voiceless glottal fricative /h/ (like English "h" in "hat"). In Spanish, "h" is always silent. XTTS-v2 with `language="es"` produces no sound for "h". User reports this sounds wrong — the "h" should be audible, like a soft aspiration.

Literature: Andrews (1975), Carochi (1645), Sullivan (1992), INALI orthographic conventions — all agree Nahuatl "h" is a distinct /h/ phoneme, not silent.

Options (in order of preference):
- A. Substitute `h` → `j` in normalizer: Spanish "j" = /x/ (velar fricative, like German "Bach") — too harsh but at least audible; acceptable as approximation
- B. Switch TTS language from `"es"` to `"en"` (English): English "h" = /h/ exactly; tradeoff is English vowel rules differ from Nahuatl's 5-vowel system (though XTTS-v2 voice cloning may compensate)
- C. Long term: use eSpeak-ng (has Nahuatl "nah" phoneme support) as text→phoneme stage, feed IPA to XTTS-v2

**Problem 2: "tl" lateral affricate**
Nahuatl "tl" = voiceless lateral affricate /tɬ/ — a Nahuatl hallmark. No direct Spanish equivalent, but Mexican Spanish speakers naturally produce /tɬ/ in Nahuatl loanwords (atole, axolotl, tlapalería). XTTS-v2 trained on Mexican Spanish may handle "tl" adequately.

Options:
- A. Leave "tl" as-is and test — Mexican Spanish TTS likely handles it reasonably
- B. Map word-final "tl" → "thl" — some practitioners report this gets closer to the lateral fricative in TTS
- C. Long term: eSpeak-ng Nahuatl phonemizer

**Recommended immediate action:** Test option A for both (no change to "tl", substitute h→j), synthesize comparison audio, decide based on listening.

### Notes

- Sheet IDs: Eduardo = `1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw`; Crispin_Carlos = `1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg` (tab: "Crispin")
- Books Drive folder: `1AFp-WuRMnhmV05km0-4D-7cQQWRdIa2a` (14 PDFs, more being transcribed)
- Parsed sentences Drive folder: `1LW0qwgf58wUX1UhpL7K2Y_6gW5x_NAoF`
- Synthesis time estimate: ~3 sec/sentence on RTX 3060 → Eduardo ~75 min, Crispin_Carlos ~190 min — run overnight
- eSpeak-ng has Nahuatl ("nah") phoneme support — best long-term text→phoneme solution; installable via apt on laptop WSL2

---

## How to Run the App (Operating Instructions)

### Requirements

- Android tablet with Termux installed
- Windows laptop with WSL2 Ubuntu, `~/nllb-env` venv, and coqui-tts installed and patched
- Both devices connected to Tailscale (laptop Tailscale IP: `100.68.100.23`)
- Laptop must be on and not sleeping

---

### Step 1 — Check if the server is already running

Open a native Termux session and run:

```
curl http://100.68.100.23:8000/health
```

If you get `{"status":"ok"}` → server is running, skip to Step 3.

If you get a connection error → proceed to Step 2.

---

### Step 2 — Start the laptop TTS server

In native Termux (not inside PRoot):

```
lsh "cd ~/Tlazanilohni_server && source ~/nllb-env/bin/activate && nohup uvicorn tts_server:app --host 0.0.0.0 --port 8000 > ~/Tlazanilohni_server/tts.log 2>&1 &"
```

Wait 10 seconds, then verify:

```
curl http://100.68.100.23:8000/health
```

Should return `{"status":"ok"}`. The first start after a laptop reboot also loads the XTTS-v2 model (~10 seconds).

---

### Step 3 — Synthesize speech

In native Termux, run with text as an argument:

```
py3 $TPROJ/main.py "Nimitztlazohtla"
```

Or run interactively (it will prompt you to type):

```
py3 $TPROJ/main.py
```

Expected output:
```
Input:      Nimitztlazohtla
Normalized: nimitztlasohtla
Saved: /storage/emulated/0/Music/Tlazanilohni/Nimitztlazohtla.wav
```

Android will open the audio automatically via the default media player.

---

### Step 4 — Find saved audio files

All generated audio is saved to:

```
/storage/emulated/0/Music/Tlazanilohni/
```

Access via: **Files app → Internal Storage → Music → Tlazanilohni**

Tap any `.wav` file to play it.

---

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `curl` returns connection error | Server not running — do Step 2 |
| `ModuleNotFoundError` when running `main.py` | Use native Termux, not PRoot: run `py3`, not `python3` |
| Audio saved but nothing plays | Open Files app → Music → Tlazanilohni → tap the file manually |
| Server error after laptop package update | Re-run patches: `lpy $TPROJ/patch_coqui.py` then restart server |
| `lsh` or `lpy` not found | You are inside PRoot — exit to native Termux session |

---

### Quick reference — all commands

```bash
# Check server
curl http://100.68.100.23:8000/health

# Start server (if needed)
lsh "cd ~/Tlazanilohni_server && source ~/nllb-env/bin/activate && nohup uvicorn tts_server:app --host 0.0.0.0 --port 8000 > ~/Tlazanilohni_server/tts.log 2>&1 &"

# Synthesize
py3 $TPROJ/main.py "Your Nahuatl text here"

# Re-apply patches (after any pip update on laptop)
lpy $TPROJ/patch_coqui.py

# View server log
lsh "tail -30 ~/Tlazanilohni_server/tts.log"
```

---

## Checkpoint — 2026-09-27 (session 3 — pausing)

### Work completed this session

- Discussed phonology gaps in the normalizer: "h" (silent in Spanish TTS, should be /h/) and "tl" (lateral affricate /tɬ/)
- Researched literature: Andrews (1975), Carochi (1645), Sullivan (1992), INALI — all confirm "h" is a distinct phoneme in Nahuatl, never silent
- Documented three options for "h": h→j substitution (quick), switch to language="en" (better), eSpeak-ng Nahuatl phonemizer (best long-term)
- Documented "tl" options: leave as-is first (Mexican Spanish TTS likely handles it via loanword training data), then test "thl" if needed
- Added AUDIOBOOK PIPELINE — PHASE 2 and NORMALIZER PHONOLOGY — KNOWN GAPS sections to Google Doc and project plan
- All documentation up to date. Pausing session here.

### Current state

- End-to-end single-sentence TTS pipeline works: Android → normalize → laptop XTTS-v2 → WAV saved to Music/Tlazanilohni/
- Known phonology gap: "h" is silent in output (Spanish TTS), "tl" untested
- Audiobook builder not yet built — full spec documented and ready to implement
- Two books ready to process: Eduardo (~1,500 sentences), Crispin_Carlos (~3,800 sentences)
- Google Doc and plan file fully up to date

### Next steps

1. **Fix "h" in normalizer** — add `h → j` substitution (not before `u`, which is already handled); synthesize a sentence with several h's before and after; listen and compare
2. **Test "tl"** — synthesize a sentence with "tl" sounds (e.g. "tlatoa", "tlahtolli"); evaluate by ear; try "thl" substitution if needed
3. **Decide language code** — if h→j still sounds too harsh, test `language="en"` on same sentences; pick whichever sounds more natural
4. **Build `audiobook_builder.py`** — reads Google Sheet, synthesizes all sentences, outputs MP3 chapters + M3U playlist with resume support
5. **Run on Eduardo first** (smaller book, ~75 min synthesis) — validate full pipeline
6. **Run on Crispin_Carlos** overnight (~190 min synthesis)

### Notes

- **Pausing here** — next session starts at step 1: normalizer h→j fix and A/B listening test
- eSpeak-ng (`nah` language) is the best long-term phonemizer; skip for now, revisit after audiobook builder is working
- Do not build audiobook_builder.py before resolving the phonology fixes — quality matters for a 3-hour audiobook

---

## Checkpoint — 2026-09-28

### Work completed this session

**normalizer.py — multiple fixes:**
- Added `h → j` substitution with negative lookbehind `(?<!s)(?<!c)` — preserves "sh" (from x→sh rule) and "ch" (Nahuatl /tʃ/); all other standalone h → j (Spanish /x/, audible aspiration approximating Nahuatl /h/)
- Added `([aeiou])uh → \1h` — silent u rule: "queniuhqui"→"kenijki", "nouhquiya"→"nohkiya", "iuhquinon"→"ijkinon"; must run before hu→w rule
- Added em-dash `—` and en-dash `–` → space — was causing XTTS-v2 hallucinations (model associates em-dash with specific training patterns)
- Added hyphen `-` → space — was being spoken as "menos" in Spanish TTS
- Added strip of `"""«»():;` — other punctuation causing TTS artifacts
- Reordered REPLACEMENTS: punctuation stripping first, then `([aeiou])uh`, then `hu→w`, then `x→sh`, then `h→j`
- Fixed recurring curly-apostrophe SyntaxError by rewriting file with explicit ASCII string delimiters throughout
- Added `¿` / `¡` inverted openers for sentences ending in `?` / `!` — triggers correct interrogative/exclamatory intonation in Spanish-trained XTTS-v2
- Added trailing period strip — XTTS-v2 produces small audible artifact on end-of-input period
- Added `re.sub(r"\s+", " ", text)` collapse — normalizes multiple spaces and embedded newlines from book text

**main.py — sentence splitting and WAV concatenation:**
- Added `split_sentences()` — splits input on sentence-ending punctuation (`[.?!]`) before synthesizing; fixes XTTS-v2 hallucination on inputs > ~250 characters
- Added `MAX_CHARS = 220` threshold — sentences still over limit are split secondarily at commas
- Added `concat_wavs()` — joins multiple WAV byte strings using Python's `wave` module (no ffmpeg needed); preserves audio params from first chunk
- Modified `synthesize()` to loop over sentence chunks, print each one as it's processed, and concatenate results
- All changes confirmed working: multi-sentence passage synthesized cleanly with no hallucination, correct intonation on questions and exclamations

### Current state

- Full normalizer pipeline: collapse whitespace → strip punctuation → iuh/ouh → hu→w → x→sh → h→j → tz→ts → qu→k → cu→kw → saltillo drop → ll→l → strip trailing period → add ¿/¡
- Multi-sentence input handled transparently in main.py — user can pass full paragraphs, output is one concatenated WAV
- Audio quality confirmed good by user ("sounds great, really great job")
- "tl" untested in isolation but not flagged as a problem — leave as-is

### Next steps

1. **Build `audiobook_builder.py`** — reads Google Sheet (Crispin_Carlos: `1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg`, tab "Crispin"), synthesizes all sentences, groups by section title → MP3 chapters + M3U playlist with resume support
2. **Run on Eduardo first** (smaller, ~1,500 sentences) — validate full pipeline before overnight run
3. **Run on Crispin_Carlos** (~3,800 sentences, ~190 min GPU) — overnight
4. **Female voice** — find clean female Nahuatl speaker clip on YouTube, extract 25s reference, add as `reference_voice_female.wav`, add `voice` param to server and CLI
5. **eSpeak-ng** — revisit as long-term phonemizer after audiobook builder is working

### Notes

- XTTS-v2 character limit is ~250 chars normalized — always split on sentence boundaries before sending; `main.py` handles this automatically now
- The `wave` module concatenation requires all chunks to have identical audio params (sample rate, channels, bit depth) — guaranteed since all come from the same server/model
- "tl" left as-is — Mexican Spanish XTTS-v2 handles the lateral affricate adequately from training on Nahuatl loanwords
- Next big task is audiobook_builder.py — all specs already documented in plan; ready to build

---

## Checkpoint — 2026-09-28 (session 2)

### Work completed this session

- Built `audiobook_builder.py` — full audiobook pipeline from Google Sheet to MP3 chapters
  - `--sheet`, `--tab`, `--book` CLI arguments
  - Reads column B (`Nahuatlahtolli`) from Google Sheet, skips 3-row header block
  - `is_section_title()` — classifies rows: len ≤ 50, no `.?!,;:-` → chapter break; otherwise → sentence
  - `synthesize_sentence()` — normalizes, splits at sentence boundaries if > 220 chars, further splits at commas, concatenates partial WAVs via `wave` module
  - `post_tts()` — HTTP POST to laptop server, retries 3× with 5s delay on failure, logs skipped sentences to `errors.txt`
  - `flush_chapter()` — ffmpeg concat of accumulated tmp WAVs → `chapter_NNN_<title>.mp3`; falls back gracefully if libmp3lame unavailable
  - `write_playlist()` — generates `playlist.m3u` listing all chapter MP3s in order (playable in VLC, Musicolet, any music app)
  - **Resume support** — `progress.json` written after every sentence; on restart, loads `last_row`/`chapter_num`/`chapter_title` and scans `_tmp/` for existing WAVs to reload chapter buffer
  - Progress printed as percentage: `[12.3%] row 45/370: sentence text...`
  - Output: `Music/Tlazanilohni/<BookTitle>/chapter_001_xxx.mp3 ... playlist.m3u`
- Syntax-checked clean — `ast.parse()` passed

### Current state

- Full pipeline ready end-to-end:
  - Single sentences: `py3 main.py "text"` — normalize → server → WAV saved + played
  - Multi-sentence paragraphs: auto-split, synthesize, concatenate, save
  - Full books: `py3 audiobook_builder.py --sheet ID --tab name --book title` — Sheet → chapters → playlist
- Both Eduardo and Crispin_Carlos sheets are ready to process
- Not yet run — Eduardo dry run is the immediate next step

### Next steps

1. **Run Eduardo** — first full book, ~1,500 sentences, ~75 min synthesis:
   ```
   cd $TPROJ && py3 audiobook_builder.py \
     --sheet 1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw \
     --tab Eduardo \
     --book "Cenyahtoc Cintli Tonacayo"
   ```
2. **Validate** — listen to first 2–3 chapters; check chapter names, audio quality, no hallucinations
3. **Run Crispin_Carlos overnight** — ~3,800 sentences, ~190 min GPU:
   ```
   cd $TPROJ && py3 audiobook_builder.py \
     --sheet 1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg \
     --tab Crispin \
     --book "Nahuatl Tequitl Crispin"
   ```
4. **Female voice** — extract 25s clean clip from a female Nahuatl speaker on YouTube → `reference_voice_female.wav`; add `voice` param to server and CLI
5. **eSpeak-ng** — long-term phonemizer improvement (nah language support); revisit after audiobook runs validated

### Notes

- Run from `$TPROJ` so `normalizer.py` is importable: `cd $TPROJ && py3 audiobook_builder.py ...`
- If interrupted: just re-run the same command — `progress.json` and `_tmp/*.wav` enable seamless resume
- ffmpeg must have libmp3lame for MP3 output; if not, script logs error and leaves WAVs in `_tmp/` for manual handling
- Eduardo tab name is "Eduardo" — verify with `lpy` or by reading the sheet if first run fails on tab name

---

## Checkpoint — 2026-09-28 (session 3)

### Work completed this session

- **Eduardo audiobook completed** — 1,517 sentences, 15 chapters, `playlist.m3u` written to `Music/Tlazanilohni/Cenyahtoc_Cintli_Tonacayo/`; first full Nahuatl audiobook produced end-to-end
- **normalizer.py — `cc → cj` rule added** — Nahuatl geminate /k/ ("nocca") was being rendered as plain /k/ ("noka") by Spanish TTS; correct pronunciation is aspirated /kx/ ("nocja"); fix: insert `("cc", "cj")` before the `([aeiou])uh` rule; verified: `nocca→nocja`, `Huacca→wacja`, `ticcaqui→ticjaki` all correct
- **Crispin_Carlos audiobook started** — `py3 audiobook_builder.py --sheet 1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg --tab Crispin --book "Nahuatl Tequitl Crispin"` — running overnight (~190 min GPU time, ~3,800 sentences)
- **Google Drive storage discussed** — agreed to upload MP3 chapters to Drive to avoid tablet storage use; pending: user to create Drive folder and share with service account; will modify `audiobook_builder.py` after Crispin run

### Current state

- Normalizer rules (in order): whitespace collapse → em/en-dash strip → hyphen strip → punctuation strip → `cc→cj` → `([aeiou])uh→\1h` → `hu+V→w` → `x→sh` → `h→j` → `tz→ts` → `qu([ei])→k` → `cu+V→kw` → saltillo drop → `ll→l` → trailing period strip → `¿`/`¡` openers
- `main.py`: handles multi-sentence input, auto-splits at sentence boundaries, concatenates WAVs via `wave` module
- `audiobook_builder.py`: reads Google Sheet → synthesizes → MP3 chapters + M3U playlist; resume support via `progress.json`
- Eduardo: 15 chapters complete, playable via playlist in VLC/Files app
- Crispin: running overnight

### Next steps

1. **Check Crispin run** — verify it completed without errors; listen to first chapter
2. **Google Drive upload** — user creates `Tlazanilohni Audiobooks` folder in Drive, shares with `ws-financial-analysis@qwen-project-492821.iam.gserviceaccount.com`; send folder ID; add Drive upload to `audiobook_builder.py` (upload each chapter MP3 after ffmpeg, optionally delete local copy)
3. **Female voice** — find female Nahuatl speaker clip on YouTube (10–30s, clean speech), extract with yt-dlp + ffmpeg, copy to laptop as `reference_voice_female.wav`; add `voice` param to server and CLI
4. **More books** — as remaining 14 PDFs get transcribed into the same sheet format, run `audiobook_builder.py` with each new sheet ID
5. **eSpeak-ng** — long-term phonemizer for Nahuatl (`nah` language code); revisit after Drive upload is working

### Notes

- Crispin run command (for reference/resume): `cd $TPROJ && py3 audiobook_builder.py --sheet 1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg --tab Crispin --book "Nahuatl Tequitl Crispin"`
- `cc→cj` rule applies universally — no edge cases found; `ticcaqui` (a common Nahuatl word) handled correctly
- Drive folder ID needed before modifying audiobook_builder.py for upload
