# Tlamachiyotl — Project Plan

**Created:** 2026-06-06
**Last updated:** 2026-06-06
**Status:** Active

---

## Overview

Agents course study project. Working through an AI agents course (originally using ChatGPT + Google Colab) using Claude Sonnet 4.6 and the native Anthropic SDK instead, running locally in the Termux/PRoot environment.

---

## Checkpoint — 2026-06-06

### Work completed this session
- Created `Ce_Tlamachilizltli.py` — first lesson file, based on course sample code
- Identified that original code used Google Colab (`userdata`), `litellm`, and hardcoded API key — none of which are needed or safe in this setup
- Decided to use native `anthropic` SDK instead of `litellm`; confirmed Google Colab not needed given existing Termux/PRoot environment
- Produced corrected version of `Ce_Tlamachilizltli.py` with minimal changes: removed Colab imports, replaced `litellm` with `anthropic` SDK, fixed model ID to `claude-sonnet-4-6`, fixed response parsing, added system message extraction (Anthropic API separates system from messages)
- API key security issue identified: original file had real key hardcoded — user advised to revoke and regenerate, and to set key via `export ANTHROPIC_API_KEY=...` in shell instead

### Current state
- `Ce_Tlamachilizltli.py` exists with original course code (not yet updated)
- Corrected version provided in console but not yet written to file
- `anthropic` SDK install status unknown — may need `pip3 install anthropic`

### Next steps
1. Revoke exposed API key at console.anthropic.com and generate a new one
2. Set `ANTHROPIC_API_KEY` in shell: `echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc && source ~/.bashrc`
3. Install SDK if not present: `/data/data/com.termux/files/usr/bin/pip3 install anthropic`
4. Apply corrected code to `Ce_Tlamachilizltli.py` and run it
5. Continue with next lesson in the course

### Notes
- Course originally uses ChatGPT (`openai` SDK) + Google Colab — all samples will need similar adaptation to Anthropic SDK
- Key structural difference per lesson: Anthropic separates `system` prompt from `messages` list; OpenAI puts system as a message with `role: system`
- Termux Python path: `/data/data/com.termux/files/usr/bin/python3`

---

## Checkpoint — 2026-06-06 (session 2)

### Work completed this session
- Renamed file from `Ce_Tlamachilizltli.py` to `Ce_Tlamachiliztli.py` (corrected spelling)
- Fixed all bugs in `Ce_Tlamachiliztli.py`: added missing `client = Anthropic()`, fixed split string literal on line 27, fixed indentation errors throughout
- Installed `anthropic` SDK in PRoot Debian: `pip3 install --break-system-packages anthropic`
- Confirmed `anthropic` already installed in Termux Python
- Set `ANTHROPIC_API_KEY` in Termux `~/.bashrc` via `echo export ... >> ~/.bashrc && source ~/.bashrc`
- Successfully ran `Ce_Tlamachiliztli.py` from Termux — Claude responded with a correct, functional-style `swap_dict` implementation
- Explained `system`/`user_messages` split, the full `generate_response` function line by line, SDK vs model distinction, and Pydroid vs Termux/Debian environment differences

### Current state
- `Ce_Tlamachiliztli.py` is fully working end-to-end in Termux
- Script calls Claude Sonnet 4.6 via native `anthropic` SDK, passes system prompt separately, and prints the response
- `anthropic` installed in both Termux and PRoot Debian
- API key set in Termux `~/.bashrc`

### Next steps
1. Confirm API key is also set in PRoot Debian `~/.bashrc` if running from there
2. Move to Lesson 2 of the agents course — adapt next sample file the same way
3. Keep adapting pattern: replace `openai` SDK with `anthropic`, fix model IDs, split system from messages

### Notes
- Running from Termux (`python3 Ce_Tlamachiliztli.py`) is the preferred execution path
- Pydroid 3 can also run the script but requires hardcoding the API key in the file — acceptable for local dev, never share/commit
- Claude responses are non-deterministic — same prompt gives slightly different but valid answers each run

---

## Checkpoint — 2026-10-02

### Work completed this session
- Read and confirmed the brainstorm Google Doc URL: `https://docs.google.com/document/d/1VB9eKJhOUtligj2oiBiFcqVkWrWS-ghBjW66qzsokZ4/edit`
- Read the full 329-line brainstorm doc via Google Docs API (service account auth, `googleapiclient`)
- Ran parallel web research across 9 claim areas: (1) mother-tongue medium of instruction, (2) Nahuatl/Mexico EIB, (3) UNESCO MTB-MLE evidence, (4) Clontarf Foundation sports+education, (5) École 42 peer learning, (6) AI tutoring for language, (7) indigenous language revitalization cognitive benefits, (8) financial literacy youth outcomes, (9) nutrition/iron and cognitive development
- Appended new section **"EVIDENCE BASE & RESEARCH NOTES"** to the Google Doc — 6 annotated claims (Nahuatl as medium, sports retention, peer learning, AI tutoring, finance track, nutrition), each with supporting evidence, key numbers, caveats, and design implications
- Appended new **"ACADEMIC REFERENCES (added 2026-10-01)"** section — ~30 sources organised by claim area with URLs
- Applied 115 formatting requests to the entire doc via `batchUpdate`:
  - HEADING_1 (navy) for Evidence Base + Academic References section headers
  - HEADING_3 (teal) for each CLAIM and category headers
  - Bold orange labels for Counter-evidence/Caveat; bold teal for Supporting evidence; bold navy for Decision/Implication labels
  - 7pt gray for decorative separator lines
  - Bullet lists added to: Vision section 5 reference models, Risk labels (orange bold), Open questions, Appendix B 30/60/90-day items, ~29 partnership/pipeline list groups

### Current state
- Brainstorm doc is now a defensible design document, not just a brainstorm — major decisions are annotated with research, caveats flagged, and gaps documented
- Key finding documented: Nahuatl-as-medium claim is well-supported by UNESCO/RTI/Cummins evidence; Mexico EIB implementation gap is the exact problem the academy addresses
- "Open Research Gaps" section documents 4 questions the academy can answer itself — framed as a potential UVI/HGSE research partnership and second funding track
- Doc formatting is now navigable: colored headers, bullets throughout, visual hierarchy across all sections

### Next steps
1. Add evidence for remaining sections not yet annotated: Nahuatl cultural production (Wikipedia/Common Voice evidence), Mandarin for LatAm youth, makerspace/fabrication pedagogy
2. Draft the 8 warm-intro emails listed in "Leveraging your background" — Mitch Resnick, Fernando Reimers, SEO Letters, DRCLAS, Fundación México en Harvard, 42 Foundation, IAF, UNESCO
3. Work through the 30-day Appendix B items: AC incorporation, cohort gender/age decisions, dual-site vs single-site decision
4. Continue agents course (Lesson 2 of `Ce_Tlamachiliztli.py` track) — adapt next OpenAI sample to Anthropic SDK

### Notes
- Google Doc accessible via service account (same key as Financial_Analysis_App) — `googleapiclient` is installed in Termux Python
- Doc now has two parallel track appendices: (A) Essay → Curriculum crosswalk, (B) 30/60/90-day action items, plus the new Evidence Base and Academic References
- The academy brainstorm and the agents course are two separate workstreams inside this project folder; the agents course files are in the root (`Ce_Tlamachiliztli.py`), the academy files are in `Curriculum_Deve/`
