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

---
## Check-Point — 2026-10-04

**Done this session:**
- Researched INEGI 2020 population stats for both sites: Huejutla (122,905 total, 51% Nahuatl speakers) and Chicontepec (50,129 total, 70% Nahuatl speakers, 320+ dispersed localities, Very High marginalization)
- Researched dual-site cost drivers: $9–17K/year overhead above single-site; recommended mobile unit ($12–18K) over fixed satellite — CESDER precedent
- Researched student digital income options (private sector, kids as earners): Nahuatl voice corpus sales (Tier 1, offline-capable, $50–150/student/month), AI labeling via school cooperative (Tier 2), Nahuatl content channel (Tier 3); school-as-data-cooperative is the structural unlock; Karya (India) is the operational model to contact
- Researched PE fund LP landscape: white space confirmed (no indigenous PE fund in LatAm); Raven Indigenous (Canada) as comp; recommended $25–35M fund, 1.5/15, Cayman LP; anchor LP path: Kellogg Foundation → Christensen Fund → Builders Vision → IDB Invest
- Researched venture builder model: recommended blended-finance tranche structure (IDB Lab precedent); priority sectors — vanilla/chili processing, artisan e-commerce, eco-tourism, rural fintech; EIR sourcing from Huasteca diaspora
- Researched talent recruitment: Enseña por México (paid fellows), AIESEC (volunteers), Codeando México (civic-tech), Catchafire (remote pro-bono), diaspora via MATT Foundation / Red de Talentos Mexicanos
- Accessed AZLera (Mozambique) and Talklet Drive folders via service account; extracted key lessons: local manager model (Coman), volunteer flow, bolsista warning (don't replicate — use digital income instead), Talklet's 0–5 speech gap as the "before" chapter to Tlamachiyotl
- Read Olko & Sullivan (2014) Nahuatl revitalization paper (Berkeley Linguistics Society) — confirmed evidence for monolingual Nahuatl instruction; IDIEZ model (Huasteca students specifically) as direct operational precedent
- Wrote 7 new sections to the Google Doc (~26,500 chars): site analysis, digital income pipeline, venture builder, talent recruitment, AZLera lessons, Talklet connection, Appendix C (PE fund LP landscape)
- Applied 223 formatting requests to full doc: H2 navy, H3 teal, Risk labels orange, Mitigation teal, key labels bold throughout
- Addressed two doc comments: (1) remote-first delivery block added across all curriculum tracks; (2) monolingual decision block added with Olko-Sullivan evidence and IDIEZ model
- Confirmed mthat MTurk is not viable for Mexico (gift cards only); Remotasks/TELUS AI are the viable equivalents
- Noted business/cooperative and PE fund must be separate legal entities from the academy

**Next:**
- Draft the 8 warm-intro emails (Mitch Resnick, Fernando Reimers, SEO Letters, DRCLAS, Fundación México en Harvard, 42 Foundation, IAF, UNESCO)
- Contact Karya (India) directly re: Mexico expansion or franchise partnership for Nahuatl voice data cooperative
- Contact IDIEZ (Zacatecas) re: Nahuatl monolingual pedagogy partnership
- Add remaining unannotated doc sections: Nahuatl cultural production evidence, Mandarin for LatAm youth, makerspace/fabrication pedagogy
- Decide and document: dual-site vs mobile unit (affects Phase 2 budget)
- Work through 30-day Appendix B items: AC incorporation, cohort gender/age, ground-person hire
- Continue agents course (Lesson 2 of `Ce_Tlamachiliztli.py`)

---
## Check-Point — 2026-10-04 (session 2)

**Done this session:**
- Executed `fix_comments.py` — 10 insertions applied to Google Doc in descending index order (safe single batchUpdate): IAF misplaced sentence label, co-partner sourcing (Ashoka/Sistema B/Endeavor/LinkedIn/UAEH/AZLera), Spanish literacy clarification, hybrid recruitment DECISION, co-ed + 40% girl quota DECISION, Starlink connectivity stack (MXN pricing, Telcel coverage, recommended MXN 1,100–3,500/month), after-school-only DECISION (no residential Phase 0–1), scope note, AZLera self-financing volunteer model, tech company direct links
- 11 new headings formatted (HEADING_3 teal/navy) + IAF paragraph changed from HEADING_3 to NORMAL_TEXT italic
- Researched Confucius Institutes in catchment area: CI-UAEH (Pachuca, 2h from Huejutla) and CI-UV (Xalapa) as closest options; Taiwan TECRO as preferred political/speed entry point; HelloChinese as free student platform; DECISION: CI-UAEH visiting teacher Year 1, AIESEC Mandarin fellow from Year 2
- Researched nutrition/cognitive development: iron deficiency anaemia (~30% in rural Hidalgo/Veracruz), weekly ferrous sulfate + biannual deworming + daily snack = ~MXN 1,500/student/year ($84–90 USD); HemoCue fingerprick screening at enrollment; DECISION: include nutrition package from Phase 1 Day 1
- Wrote two new sections to Google Doc (4,865 chars): "MANDARIN FOR LATAM YOUTH" and "NUTRITION AND COGNITIVE DEVELOPMENT" — both with H2 navy + H3 teal formatting applied

**Next:**
- Draft the 8 warm-intro emails (Mitch Resnick, Fernando Reimers, SEO Letters, DRCLAS, Fundación México en Harvard, 42 Foundation, IAF, UNESCO)
- Contact Karya (India) re: Mexico expansion for Nahuatl voice data cooperative
- Contact IDIEZ (Zacatecas) re: Nahuatl monolingual pedagogy partnership
- Contact CI-UAEH (institutodeconfucio@uaeh.edu.mx) re: visiting teacher arrangement Year 1
- Add remaining unannotated doc sections: Nahuatl cultural production evidence, makerspace/fabrication pedagogy
- Decide and document: dual-site vs mobile unit (Phase 2 budget)
- Work through 30-day Appendix B items: AC incorporation, cohort gender/age, ground-person hire
- Continue agents course (Lesson 2 of `Ce_Tlamachiliztli.py`)

---
## Checkpoint — 2026-10-04 (session 3)

### Work completed this session
- Fetched all 17 Google Doc comments via Drive API (15 open, 2 already resolved)
- Posted "AI reply: ..." to all 15 open comments via `drive.replies().create()`; resolved 13 as fully addressed, left 2 open (#3 site model, #15 links)
- Identified comment #3 as unaddressed: user clarified mobile unit recommendation is wrong — they plan to live on-site and rent a professional space
- Ran `fix_site_model.py`: deleted old "Recommended Alternative: Mobile Unit" heading + 2 body paragraphs (van costs + CESDER); inserted 3 new H3 sub-sections: "Phase 0–1 Site: Fixed Rented Premises in Huejutla" (navy), "Why fixed, not mobile" (teal), "Chicontepec access — Phase 2 model" (teal); CESDER precedent repositioned to Phase 2 outreach only
- Ran `add_links.py`: added 135 hyperlinks throughout the full doc; organisations covered: Starlink, Telcel, Karya, Remotasks, TELUS AI, Appen, iMerit, Outlier, Enseña por México, Codeando México, Catchafire, AIESEC, Idealist, UN Volunteers, GoOverseas, IDIEZ, CESDER, Clontarf Foundation, HelloChinese, TECRO, CI-UAEH, CI-UV, Ashoka, Sistema B, Endeavor, Google.org, Microsoft Philanthropies, Amazon Future Engineer, Cisco Networking Academy, Salesforce.org, Kellogg Foundation, Ford Foundation, Christensen Fund, Builders Vision, IDB Invest, Raven Indigenous Capital, Adobe Capital, Common Voice, Masakhane, UNESCO, UAEH, and others
- Resolved comment #3 reply (site model now corrected) and comment #15 reply (links fully addressed)

### Current state
- All 17 doc comments have AI replies; 15 resolved, 2 left open (both now actioned this session)
- Doc site model section reflects correct Phase 0–1 model: fixed rented premises in Huejutla, founder on-site, MXN 3–8K/month; Chicontepec as Phase 2 periodic outreach
- 135 hyperlinks live throughout the doc on all key organisations, platforms, and funders
- All research from the 2026-10-04 sessions written to doc: site analysis, digital income pipeline, venture builder, talent, AZLera lessons, Talklet connection, PE fund appendix, Mandarin section, nutrition section
- Doc is a defensible design document with formatted headings, bullets, colour hierarchy, evidence annotations, decisions, and linked references

### Next steps
1. Draft the 8 warm-intro emails (Mitch Resnick, Fernando Reimers, SEO Letters, DRCLAS, Fundación México en Harvard, 42 Foundation, IAF, UNESCO)
2. Contact Karya (India) — email re: Mexico expansion or franchise for Nahuatl voice data cooperative
3. Contact IDIEZ (Zacatecas) — email re: Nahuatl monolingual pedagogy partnership
4. Contact CI-UAEH (institutodeconfucio@uaeh.edu.mx) — visiting teacher arrangement Year 1
5. Add remaining unannotated doc sections: Nahuatl cultural production evidence, makerspace/fabrication pedagogy
6. Work through 30-day Appendix B items: AC incorporation, cohort gender/age decision, ground-person hire
7. Continue agents course (Lesson 2 of `Ce_Tlamachiliztli.py`)

### Notes
- Site model DECISION confirmed: Phase 0–1 = fixed rented premises in Huejutla (not mobile unit). Mobile unit concept deferred to Phase 2+ Chicontepec outreach only.
- Links in `add_links.py` are first-occurrence-per-run; running the script again on an already-linked doc is safe (it skips runs that already have a link style).
- Scripts in project folder: `fix_comments.py`, `fix_site_model.py`, `add_links.py`, `write_new_sections.py`, `write_mandarin_nutrition.py`, `format_doc.py`

---
## Check-Point — 2026-10-04 (session 4)

**Done this session:**
- Ran `doc_and_citations.py`: fixed "Why dual-site works" paragraph (deleted stale paragraph, inserted "Why Huejutla-first works" replacement); added 6 inline citations in gray italic 8pt throughout body text (UNESCO/Cummins/Olko-Sullivan for language sections, OECD/Lusardi for finance, NSW CESE for peer learning, Lozoff/Kang/Vendt for nutrition, AI4Bharat for digital income)
- Ran `consistency_fixes.py`: updated Appendix B "Decide on dual-site" item to CONFIRMED decision; replaced "Chicontepec / mobile unit days:" with "Phase 2 — Chicontepec outreach days (mobile):"; appended Appendix D (Space & Real Estate Research) with Huejutla/Chicontepec rental estimates
- Ran `write_appendices_ef.py`: appended 16,420 chars — six new sections: Appendix E (Revenue Streams with Tier 1/2/3/Zero-income breakdown), Appendix F (Site Comparison table Huejutla vs Chicontepec), Online Curricula & Bootcamp Resources (CS50x, freeCodeCamp, Odin Project, Laboratoria, Kaggle Learn, CONAFE Robótica, CONALEP), 4-Week Bootcamp — Tlamachiyotl Piscine curriculum, Finance Module 6 — Crypto Remittance Rails (Bitso, MoneyGram+Stellar, Strike), Languages — Spanish Positioning (Cummins Threshold, enrollment script). Applied 58 formatting requests.
- Ran `post_comment_replies.py`: posted "✅ DONE / ✅ ALREADY IN DOC" replies to all 14 open comments and resolved each one
- **Teacher training Step 0** (comment #2): added to this project plan (see Next steps below)

**Teacher training — Step 0 (pre-launch, before first cohort):**
- Recruit 1 Nahuatl-fluent teacher-in-residence from Huasteca region or Nahuatl diaspora
- Partner with IDIEZ (Zacatecas) or Universidad Veracruzana Intercultural for formal teacher training methodology in Nahuatl-medium instruction
- Train before first cohort opens; revisit and expand for Year 2

**Next:**
1. Draft 8 warm-intro emails (Mitch Resnick, Fernando Reimers, SEO Letters, DRCLAS, Fundación México en Harvard, 42 Foundation, IAF, UNESCO)
2. Contact Karya (India) re: Mexico expansion / franchise for Nahuatl voice data cooperative
3. Contact IDIEZ (Zacatecas) re: Nahuatl monolingual pedagogy partnership + teacher training Step 0
4. Contact CI-UAEH (institutodeconfucio@uaeh.edu.mx) re: visiting Mandarin teacher Year 1
5. Add remaining unannotated doc sections: Nahuatl cultural production evidence, makerspace/fabrication pedagogy
6. Work through 30-day Appendix B items: AC incorporation, cohort gender/age decision, ground-person hire
7. Continue agents course (Lesson 2 of `Ce_Tlamachiliztli.py`)
7. Continue agents course (Lesson 2 of `Ce_Tlamachiliztli.py`)

---
## Checkpoint — 2026-10-05 (session 5)

### Work completed this session
- Ran `write_arts_section.py`: appended 16,634-char ARTS & MUSIC — CURRICULUM AREA section at index 125,081. Eight H3 sub-sections: Why arts belong (cognitive transfer, language dev, cultural identity, revenue); Nahuatl heritage arts (huapango, bordado, amate, danza, décima); Cross-pollination with STEM/Finance/Digital income/Sports/Mandarin/Nutrition; Curriculum tracks (Foundation + Concentration); Local partners (Casa de la Cultura, INAH, FONCA, UAEH/UV); International partners (El Sistema, Latin Grammy, Berklee, Silkroad, UNESCO, British Council, BBVA, Common Voice); Revenue; Research gaps. 29 formatting requests applied.
- Ran `write_hgse_foundations.py`: appended 20,229-char HGSE COURSE FOUNDATIONS — RESEARCH, FRAMEWORKS & DESIGN CONNECTIONS section at index 141,715. Nine H3 sub-sections covering H700 (language dev + biliteracy), H126 (neuroscience of poverty + plasticity), HPL (Bronfenbrenner, UDL, Hattie effect sizes, Wiggins, Colvin), HT123 J-term + HAA 19Z (Kilman/Emdin/Bolduc arts evidence, codex literacy, Prof. Tom Cummins), MIT 2.S972 (VR/Unity aspiration), T581 (Scratch→Unity progression), S043/S022 (IRB/R stats), Faculty contacts. 38 formatting requests applied.
- Ran `integrate_hgse_content.py`: 7 insertions in descending index order into existing doc sections:
  - si=137555: Harvard Art Museums partner block (Arts international partners section)
  - si=133185: Codex literacy curriculum item (Arts curriculum section)
  - si=126419: Kilman/Emdin/Shapiro evidence paragraph (Arts "Why arts belong" section)
  - si=74585: 29 new HGSE academic references in 4 course-library sections (Academic References appendix)
  - si=56860: Phonological awareness transfer argument — H700 evidence (CLAIM 1 / Language section)
  - si=50063: UDL + Bronfenbrenner ecology + Hattie effect-size pedagogy block (cohort pedagogy section)
  - si=19250: Academic language + extended discourse + teacher training implication (Language/IDIEZ section)
  - 53 formatting requests applied (orange labels, teal headers, gray italic 8pt citations)
- Ran `update_toc.py`: deleted old incomplete TOC entries [495, 1105), inserted 1,478-char 39-entry linked TOC at si=495. Five category labels (CORE SECTIONS, CURRICULUM AREAS (added 2026), ACADEMY DESIGN & OPERATIONS, APPENDICES, RESEARCH & EVIDENCE) + 34 link entries with internal `#heading=h.{id}` anchors for all sections including new ARTS & MUSIC and HGSE COURSE FOUNDATIONS sections.
- Wrote and fixed `fix_toc_spacing.py` to correct TOC paragraph style inheritance issue:
  - Bug: inserting new text after a HEADING_2 caused all 39 TOC entry paragraphs to inherit HEADING_2 style (large spacing ~12–16pt per line)
  - Bug: `update_toc.py` link-finding loop (si<2500) accidentally applied teal 9pt + internal link to actual PREFACE heading at si=1973
  - Fix bug 1: changed all TOC paragraphs si=495–1972 from HEADING_2 → NORMAL_TEXT with tight spacing (spaceAbove=0/6pt, spaceBelow=0/1pt, lineSpacing=110); category labels bold navy 9.5pt; link entries teal 9pt
  - Fix bug 2: restored PREFACE heading at si=1973 to navy bold 13pt, cleared accidental link using `'link': None` (JSON null — empty dict `{}` rejected by API as "Links must include at least one type")
  - 80 requests applied successfully

### Current state
- Google Doc has complete 39-entry Table of Contents with internal hyperlinks, tight compact spacing
- Four new major sections added: ARTS & MUSIC, HGSE COURSE FOUNDATIONS, plus integrated HGSE research content woven into existing language/pedagogy/arts/references sections
- 29 new academic references (HGSE course library) added to Academic References appendix in gray italic 8pt
- All HGSE course connections documented: H700, H126, HPL, HT123, HAA 19Z, MIT 2.S972, T581, S043/S022
- All prior comment replies posted and resolved; doc is a complete, defensible design document

### Next steps
1. Draft 8 warm-intro emails (Mitch Resnick, Fernando Reimers, SEO Letters, DRCLAS, Fundación México en Harvard, 42 Foundation, IAF, UNESCO)
2. Contact Karya (India) re: Mexico expansion / franchise for Nahuatl voice data cooperative
3. Contact IDIEZ (Zacatecas) re: Nahuatl monolingual pedagogy partnership + teacher training Step 0
4. Contact CI-UAEH (institutodeconfucio@uaeh.edu.mx) re: visiting Mandarin teacher Year 1
5. Add remaining unannotated doc sections: Nahuatl cultural production evidence, makerspace/fabrication pedagogy
6. Work through 30-day Appendix B items: AC incorporation, cohort gender/age decision, ground-person hire
7. Continue agents course (Lesson 2 of `Ce_Tlamachiliztli.py`)

### Notes
- API link-clearing: use `'link': None` (not `{}`) in updateTextStyle to clear a link. Empty dict is rejected with "Links must include at least one type."
- TOC insertion order: new text inserted after a heading inherits that heading's paragraph style. Always follow TOC insertion with an explicit updateParagraphStyle pass to NORMAL_TEXT.
- Scripts this project: `post_comment_replies.py`, `write_arts_section.py`, `write_hgse_foundations.py`, `integrate_hgse_content.py`, `update_toc.py`, `fix_toc_spacing.py` (plus prior sessions: `fix_comments.py`, `fix_site_model.py`, `add_links.py`, `write_new_sections.py`, `write_mandarin_nutrition.py`, `format_doc.py`, `doc_and_citations.py`, `consistency_fixes.py`, `write_appendices_ef.py`)

---
## Checkpoint — 2026-10-05 (session 6)

### Work completed this session
- Ran `reorganize_doc.py` (carried over): executed 11 section moves (6 backward, 5 forward) to align doc body order with the user's manually updated TOC. All moves confirmed correct via final section-order printout. HeadingIds preserved via hid-based lookup + re-read between each move.
- Fixed two TOC link mismatches after the moves: APPENDIX C headingId updated (colon/dash title mismatch caused prefix comparison failure); HGSE entry confirmed unchanged. Both entries now resolve correctly.
- Moved "Remote-First Delivery" section (Finance Track) into ONLINE CURRICULA section per open comment; resolved both open doc comments with replies.
- Ran spacing diagnosis (`diagnose_spacing.py`): found 0 NORMAL_TEXT paragraphs with explicit spaceAbove > 0 or lineSpacing > 200. Root cause of 300-page expansion was NOT explicit style overrides — likely named-style default inheritance.
- Ran `/tmp/fix_spacing_full.py`: applied explicit paragraph style overrides to all 1582 body paragraphs (si > 2000): NORMAL_TEXT → spaceAbove=0, spaceBelow=0, lineSpacing=115; HEADING_2 → spaceAbove=10, spaceBelow=4, lineSpacing=100; HEADING_3 → spaceAbove=6, spaceBelow=2, lineSpacing=100; HEADING_1 → 8/4/100; HEADING_4 → 4/2/100.
- Added new APPENDIX F subsection via `/tmp/add_appendix_f_schools.py` (8,040 chars at section_end=124428):
  - H3: "School landscape within 15 km radius — Huejutla and Chicontepec": placeholder map screenshot notes (italic gray), per-level school breakdown (public/private) for both cities, summary paragraphs
  - H3: "Cultural and media organisations": XEJAM (Huejutla, INPI AM 1180), Radio Comunitaria Chicontepec (to confirm), Casa de Cultura both cities, INPI CDI offices, UIEH, IDIEZ, Huapango Arribeño network
  - Field verification note (gray italic)
  - 50 formatting requests: orange labels, teal org names, gray screenshot placeholders, navy intro text

### Current state
- Doc section order matches the user's manually reordered TOC (11 sections correctly repositioned)
- TOC links updated to reflect post-move headingIds
- Spacing normalized document-wide (explicit overrides on all 1582 paragraphs — should resolve 300-page expansion)
- APPENDIX F now has two new H3 subsections: school landscape data (public/private, K–preparatoria) + cultural/media organisations for both sites
- Two open comments resolved

### Next steps
1. Verify spacing fix resolved the 300-page expansion (user should check page count in doc)
2. Add actual map screenshots to APPENDIX F school placeholders (user must do manually: Google Maps → export screenshot → insert in doc)
3. Confirm Radio Comunitaria Chicontepec station name/frequency (field verification)
4. Draft 8 warm-intro emails (Mitch Resnick, Fernando Reimers, SEO Letters, DRCLAS, Fundación México en Harvard, 42 Foundation, IAF, UNESCO)
5. Contact IDIEZ (Zacatecas) re: Nahuatl monolingual pedagogy partnership + teacher training Step 0
6. Contact CI-UAEH re: visiting Mandarin teacher Year 1
7. Continue agents course (Lesson 2 of `Ce_Tlamachiliztli.py`)

### Notes
- **Root cause of 300+ page explosion:** `reorganize_doc.py` inserted content at H2 heading positions that had `pageBreakBefore=True`. All inserted paragraphs inherited that flag. `build_requests()` didn't extract or reset `pageBreakBefore`, so 312 paragraphs (285 NORMAL_TEXT + 27 H3) each forced a new blank page.
- **Fix:** `fix_page_breaks.py` cleared `pageBreakBefore=False` on 312 wrong paragraphs; kept on 15 legitimate H2 section headings. Result: 88 pages (confirmed from PDF root /Pages /Count).
- **PDF page count gotcha:** `max(/Count)` from PDF regex is WRONG — picks up font/glyph counts. Correct method: count `/Type /Page(?![sS])` leaf nodes, then verify with root `/Pages` object `/Count`. Both returned 88.
- APPENDIX F map screenshots: insert manually in Google Docs. Recommended source: Google Maps with "Schools" layer or SEP 911 estadística escolar open dataset filtered by municipality.
- **Future rule:** any `build_requests()` or `insertText` at heading positions must follow with `updateParagraphStyle` that explicitly sets `pageBreakBefore=False` on all non-heading inserted paragraphs.
- Scripts this session (temp, `/tmp/`): `fix_spacing_full.py`, `add_appendix_f_schools.py`, `fix_page_breaks.py`, `verify_page_count.py`

---
## Checkpoint — 2026-10-05 (session 7)

### Work completed this session
- Applied all remaining pending open-comment tasks carried from session 6:
  - Inserted "nearby towns" paragraph (Tamazunchale, Tampico, SLP, CD MX distances) into APPENDIX F geographic dispersion section
  - Applied hyperlinks to all Potential Partners section entries
  - Inserted "School landscape" H3 + paragraph (COBACH Hidalgo, CECYTE Hidalgo, COBAVER, SEP DGEI) with live links into APPENDIX F
  - Inserted and filled 8×2 Core Concentrations table (Nahuatl/Language, STEM, Finance/Business, Digital Skills, Arts/Music, Sports, Mandarin, Nutrition)
  - Applied CONALEP and CONEVAL hyperlinks to relevant paragraphs
- Resolved all 12 open comments from session 6 (first wave) via `resolve_comments2.py`
- Ran `insert_parental_involvement.py`: inserted full "PARENTAL INVOLVEMENT — RESEARCH & BEST PRACTICES FOR BUY-IN" section at si=34812 (~10,270 chars, 10 H3 subsections): evidence base, school communication channels, homework involvement, governance/decision-making, mother tongue affirmation, digital bridge tools, community liaison role, trust-building, Huasteca-specific field notes, implementation roadmap
- Ran `link_parental_section.py`: applied 20 live hyperlinks within the new section (Harvard Family Research Project, Epstein et al., Funds of Knowledge, WHO Lancet, INPI, INALI, Duolingo, WhatsApp for Education, etc.)
- Diagnosed and re-inserted APPENDIX F site maps (both previously-inserted images had disappeared — 0 inlineObjects in doc):
  - Regenerated OSM tile composites (3×3 grid, z=12) for Huejutla (21.1405, -98.4195) and Chicontepec (20.9778, -98.1800) using PIL
  - Uploaded both PNGs to Google Drive via user OAuth token (`token.json`, drive scope)
  - Ran `fix_and_insert_maps.py`: deleted misplaced placeholder content that had been accidentally inserted twice inside the population table's last cell, then inserted both maps (396×396 pt) plus "Geographic context — site maps" heading and per-city labels after the population table at the correct doc-level position
  - Confirmed 2 inline objects present (kix.9rm6qq86bju8 and kix.caknyy1xwo9v)
- Reviewed 11 re-opened comments (second wave) and applied all changes:
  - Site rating matrix: inserted 10×5 table (10 candidate sites × 5 criteria) after "Key finding" paragraph in APPENDIX F
  - Population table: expanded from 9×3 → 9×5 by adding two columns (state average and national average) via `insertTableColumn` twice; filled new cells with Hidalgo state and Mexico national CONEVAL poverty/marginalization figures
  - École 42 cohort: inserted paragraph at si≈8180 describing 42's cohort model (peer learning, no teachers, 3–5 year program), with links to INEGI youth data, Scale AI, and Appen
  - CONALEP remote: inserted paragraph after CONALEP contact line describing remote/hybrid delivery option
  - Resolved all 11 comments via `replies().create()` with `action: resolve`

### Current state
- Google Doc is up-to-date with all open comments resolved (two waves: 12 + 11 = 23 total resolved this session)
- New "PARENTAL INVOLVEMENT" section fully written and linked (sits after Introduction / before Academic References)
- APPENDIX F has both OSM site maps (Huejutla + Chicontepec) correctly placed after population table, 396×396 pt inline
- Population table is 9×5 with state and national CONEVAL comparison columns
- Site rating matrix table (10×5) inserted in APPENDIX F
- All prior comment tasks from sessions 5–6 backlog now complete

### Next steps
1. Verify no new open comments remain in the doc
2. Draft 8 warm-intro emails (Mitch Resnick, Fernando Reimers, SEO Letters, DRCLAS, Fundación México en Harvard, 42 Foundation, IAF, UNESCO)
3. Contact Karya (India) re: Nahuatl voice data cooperative / Mexico franchise
4. Contact IDIEZ (Zacatecas) re: Nahuatl monolingual pedagogy partnership + teacher training Step 0
5. Contact CI-UAEH (institutodeconfucio@uaeh.edu.mx) re: visiting Mandarin teacher Year 1
6. Work through 30-day Appendix B items: AC incorporation, cohort gender/age decision, ground-person hire
7. Continue agents course (Lesson 2 of `Ce_Tlamachiliztli.py`)

### Notes
- **Drive upload scope:** `token.json` has `https://www.googleapis.com/auth/drive` (not `.file`). Scripts using `google.oauth2.credentials.Credentials` must specify this exact scope or `RefreshError: invalid_scope` is thrown.
- **Table cell insertion index:** for an empty table cell, use `'index': para_si` (the cell paragraph's startIndex), NOT `para_si + 1`. The `+ 1` variant hits "insertion index must be inside the bounds" error.
- **Comment resolve API:** body must include `'content': original_content` (not just `'resolved': True`) and `fields='id,resolved'` kwarg is required, otherwise API returns 400.
- **insertTableColumn safety:** must re-read the doc between the first and second `insertTableColumn` calls — the column insertion shifts all subsequent indices.
- **Maps disappearing:** likely caused by prior batchUpdate operations that deleted ranges containing the inlineObjectElement paragraphs. Mitigation: always verify `len(doc['inlineObjects'])` after any large range-deletion operation.
- Scripts this session (temp, `/tmp/`): `insert_towns_and_schools.py`, `apply_all_links.py`, `fill_concentrations2.py`, `resolve_comments2.py`, `insert_parental_involvement.py`, `link_parental_section.py`, `reinsert_maps.py`, `fix_and_insert_maps.py`, `verify_maps.py`, `verify_maps2.py`, `find_immersion.py`, `find_comment_texts.py`, `read_all_comments.py`

---
## Checkpoint — 2026-10-06 (session 8)

### Work completed this session
- **APPENDIX G** (Digital Income Pathways: Games & Virtual Economies) inserted at si≈160,086 — 8,468 chars, 11 headings; covers Roblox Studio, UEFN/Fortnite, asset marketplaces (Unity/Unreal), mobile indie, localization, content creation, pixel art/graphic design; implementation notes framed for Huasteca students
- **APPENDIX H** (Venture Builders, Funders & Strategic Partners) inserted at si≈169,368 — 12,842 chars, 10 headings; covers TechnoServe model, Mondragon cooperative, Laboratoria ISA, Preston anchor purchasing, 12-week curriculum framework for uninvestable micro-businesses in Huasteca; Section 7 establishes the academy-as-venture-builder thesis
- **APPENDIX I** (Indigenous Enterprise: Mexico & Central America) inserted at si≈183,295 — 9,166 chars; agricultural cooperatives (UCIRI, CEPCO/MICHIZA Yeni Navan, Tosepan Titataniske), knowledge export (IDIEZ), cultural enterprises (Sna Jtz'ibajom), networks (CIELO, CESDER, Mercado Global); negative lesson: XEGLO state-dependency failure; TABLE_I (7×3 mechanisms synthesis)
- **APPENDIX J** (Indigenous Enterprise: North & South America) inserted at si≈193,563 — 15,018 chars; US: Cherokee Nation Businesses, Seminole/Hard Rock, Tanka Bar, NDN Collective, Citizen Potawatomi; Canada: Clearwater Mi'kmaq, Membertou ISO 9001, Raven Capital, Animikii; South America: Kapawi phased transfer, ANEI Coffee dual-cert, Sarayaku, Sateré-Mawé guaraná, Kayapó nuts, Bolivian quinoa (commoditization warning), Suruí carbon (warning); TABLE_J (5×4 priority actions)
- **APPENDIX K** (Mechanisms of Scale from Structural Poverty: Chinese Cases) inserted at si≈209,390 — 13,553 chars; hui/ROSCA = tanda (core zero-collateral capital mechanism), Li Ka-shing / Lim Goh Tong / Robert Kuok, Wenzhou model (biaohui + cluster manufacturing + Paris diaspora), ethnic minorities (Yi/Nuosu clan warning, Naxi Lijiang, Dong Grand Song, Miao Taobao Villages, Ren Zhengfei/Huawei); 4 transferable lessons; TABLE_K (5×4)
- **APPENDIX L** (Three Stages to Escape Velocity: Ce / Ome / Yei) inserted at si≈224,100 — 15,593 chars; Ce Tlamachiliztli (0–3yr, income floor: AI annotation + 15 university contracts + corpus licensing + founding tanda), Ome Tlachihualiztli (3–7yr: content studio + translation cooperative + **Nahuatl certification exam as key IP asset** + digital agency + heritage immersion, $1–3M/yr), Yei Tlacahuiliztli (7–15yr: 100+ global contracts + AI corpus royalties + certification as toll road + cultural IP + game studio + community fund, $5–15M/yr); non-negotiables stated explicitly; TABLE_L (4×5 stage transitions)
- **APPENDIX M** (International University Track: Engineering and Medicine) inserted at si≈240,720 — 15,230 chars; China CSC (fully funded, HIT/Zhejiang engineering, Ningxia/Guangxi MBBS), Israel (Hebrew University as Tier 1 warm-intro via founder's alumni contacts — Hadassah Medical, Faculty of Agriculture, CS; Technion cost analysis), Germany (DAAD KOSPIE, €992/month, 1-year + industrial internship), Hungary (Stipendium Hungaricum, full tuition Semmelweis/Pécs, EU-recognized MD), France (Eiffel Excellence, €1,200/month, master's level); return-flow covenant (3–5% of income above living wage for 10 years + 1 week/year knowledge transfer + network obligation); 2026–2027 timeline; TABLE_M (7×6 pathway comparison)
- **TOC updated** (`update_toc.py`): inserted 7 hyperlinked TOC entries (APPENDIX G–M) after the APPENDIX F entry, styled to match existing TOC format (teal underline, 10pt, headingId links)
- **Memory updated**: saved Hebrew University warm-intro pathway as persistent memory (user is alumnus with active contacts; treat as Tier 1, not cold application)

### Current state
- Google Doc has 13 appendices (A–M); all are in the TOC with working hyperlinks
- Three-stage strategic arc (Ce/Ome/Yei) is now the organizing spine of the entire planning document
- Language app clarified as internal flywheel (translating books INTO Nahuatl for community learning acceleration), not a revenue product — stated as non-negotiable in APPENDIX L
- Seminole model clarified: talent scales AWAY from the community (too small to absorb it); fund recirculates returns back — shapes Yei stage "escape velocity" framing
- Doc is at ~255,000+ index positions (approx. 300+ pages equivalent)

### Next steps
1. Identify the first 2–3 student candidates with realistic international university profile (STEM aptitude, English base, family support)
2. Contact Hebrew University directly via founder's alumni network — propose cohort agreement for Huasteca students (start with Faculty of Agriculture or CS track)
3. Register students for Mandarin at UAEH Confucius Institute (CI-UAEH) — prerequisite for China CSC track by 2028
4. Contact IDIEZ (Zacatecas) re: Nahuatl monolingual pedagogy partnership + teacher training
5. Draft the 8 warm-intro emails (Mitch Resnick, Fernando Reimers, SEO, DRCLAS, Fundación México en Harvard, 42 Foundation, IAF, UNESCO)
6. AC incorporation and ground-person hire (30-day Appendix B items)
7. APPENDIX N candidates: governance & legal structure (AC vs. SAPI vs. cooperative), or land/real estate acquisition pathway

### Notes
- **Tanda = Hui recognition**: Mexican rotating credit (tanda) is structurally identical to Chinese hui/ROSCA — zero-collateral capital mechanism. This is the seed-funding vehicle for Ce stage.
- **No craft-scale ideas**: any income stream discussed must be scalable beyond the local community. Crafts, tourism, and local services were explicitly ruled out as insufficient.
- **Nahuatl certification exam** (APPENDIX L, Ome stage): this is the highest-leverage IP asset in the plan — creates a certification standard the academy owns, generates recurring revenue, and functions as a quality-verification seal like Max Havelaar. Needs legal/IP strategy.
- **Scripts this session** (temp, `/tmp/`): `insert_appendix_texts.py`, `insert_appendix_tables.py`, `insert_appendix_i.py`, `insert_appendix_j.py`, `insert_appendix_k.py`, `insert_appendix_l.py`, `insert_appendix_m.py`, `update_toc.py`

---
## Checkpoint — 2026-10-08 (session 9)

### Work completed this session
- **Chicontepec Formation research**: read Wikipedia article + 8 targeted searches + 2 page fetches covering: geological formation (139B barrels in place, 19B recoverable, 31.5 TCF gas), Pemex production history (peaked 68K b/d in 2012, declined to 15.7K b/d in 2024, MX$4B investment in 2026), indigenous community impacts (Mequetla 2024 spills: 7 leaks, 2,450L water-oil mix + 400L crude on ejido farmland), ILO Convention 169 enforcement (Tecoltemi 2022 SCJN ruling cancelling mining concessions for Nahua community in Puebla), Canadian Impact Benefit Agreement model ($350M/yr to First Nations), Nations Royalty Corp. (world's first majority-Indigenous mining royalty company, Nisga'a Nation + Frank Giustra), AI annotation in oil & gas ($2.5B market growing 7.1% CAGR)
- **APPENDIX N inserted** (`insert_appendix_n.py`): 17,241 chars, 15 headings (1 H2 + 14 H3), si≈257,481; covers: formation facts, legal gap analysis, four legal levers (surface easements / FPIC-ILO169 / environmental liability / service contracts), Tecoltemi 2022 precedent, income streams by Ce/Ome/Yei stage ($200–500K by Ome, $1–3M by Yei), seismic annotation bridge, Nations Royalty model adaptation, integration with three-stage arc, risks and non-negotiables, priority actions 2026–2028; TABLE_N (7×5 lever comparison)
- **TOC updated**: APPENDIX N entry added after APPENDIX M, hyperlinked to heading, styled to match existing TOC format

### Current state
- Google Doc has 14 appendices (A–N), all in the TOC with working hyperlinks
- APPENDIX N establishes the Chicontepec Formation as the fourth major Yei-stage income stream alongside AI corpus royalties, certification revenues, and content studio IP
- The Tecoltemi 2022 precedent (SCJN) is documented as the controlling legal authority for FPIC enforcement in Nahua territory
- The seismic annotation bridge connects the Ce-stage annotation income stream to a $2.5B oil-and-gas AI market — same workflow, no new infrastructure
- The Nations Royalty (Nisga'a/Giustra, Canada 2024) model is identified as the template for a Mexican Indigenous royalty pooling vehicle

### Next steps
1. Identify the first 2–3 student candidates with realistic international university profile (STEM aptitude, English base, family support)
2. Contact Hebrew University via founder's alumni network — propose cohort agreement for Huasteca students (Faculty of Agriculture or CS track as entry point)
3. Register students for Mandarin at UAEH Confucius Institute — prerequisite for China CSC track by 2028
4. Commission Chicontepec surface agreement mapping exercise — UAEH law student, Registro Agrario Nacional data + community interviews
5. Incorporate the AC or cooperative to hold ejido negotiating authority (Late 2026)
6. Contact IDIEZ (Zacatecas) re: Nahuatl monolingual pedagogy + teacher training Step 0
7. Draft 8 warm-intro emails (Mitch Resnick, Fernando Reimers, SEO, DRCLAS, Fundación México en Harvard, 42 Foundation, IAF, UNESCO)
8. AC incorporation and ground-person hire (30-day Appendix B items)

### Notes
- **Chicontepec legal strategy**: posture is "indispensable local partner," not opponent of Pemex. The four levers (surface rights, FPIC, environmental liability, service contracts) are all exercised through legal and technical engagement, not protest.
- **Mequetla spills (2024)**: documented 7 leaks May–Oct 2024, 2,450L water-oil + 400L crude on ejido farmland in Castillo de Teayo, Veracruz. This is the opening evidence for the environmental monitoring lab argument.
- **Tecoltemi 2022 (SCJN)**: Nahua community in Puebla — adjacent to Chicontepec — won cancellation of two mining concessions from Almaden Minerals (Canada) for failure to conduct FPIC consultation. No compensation required. Strongest available precedent.
- **Nations Royalty**: world's first majority-Indigenous mining royalty company (Nisga'a Nation + Frank Giustra, 2024). Pools 400+ individual IBAs. Model for Mexico adaptation.
- **Seismic annotation**: $2.5B market (2024), 7.1% CAGR. Same annotation skillset as Ce-stage academic text work. Scale AI and Appen already serve oil and gas clients.
- **Scripts this session** (temp, `/tmp/`): `insert_appendix_n.py`, inline TOC update (run via heredoc)
