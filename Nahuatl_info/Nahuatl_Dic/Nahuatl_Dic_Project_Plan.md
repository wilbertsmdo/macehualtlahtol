# Nahuatl_Dic — Project Plan

**Created:** 2026-08-24
**Last updated:** 2026-08-24
**Status:** Active

---

## Overview

Research and tooling around the Nahuatl dictionary. Includes scripts for sorting and processing Nahuatl dictionary documents, and exploratory work on Nahuatl linguistics — particularly strategies for deriving modern vocabulary (neologisms) in an agglutinative language that lacks contemporary terminology.

---

## Checkpoint — 2026-08-24

### Work completed this session
- **Research session:** Explored strategies for deriving new words in Nahuatl for a modern vocabulary / translation project.
- Surveyed the **corpus language planning** literature (Fishman 1991, Hornberger 1996, Karttunen 1983, Lockhart 1992).
- Mapped out five main neologism strategies: native compounding, calques/loan translations, semantic extension, direct phonological borrowing, and hybrid approaches.
- Analyzed the **Chinese model** (Mandarin semantic compounding — e.g., 电脑 "electric brain" = computer) as the strongest parallel and most applicable approach given Nahuatl's agglutinative morphology.
- Assessed the **Latin/Greek etymology route**: useful for highly technical terms as a last resort, but risks creating a two-tier vocabulary that marginalizes the native layer over time.
- Assessed **Hebrew revival** (Ben-Yehuda) as evidence that large-scale native-root neologism is feasible.
- No code written or modified this session.

### Current state
- `sort_nahuatl_doc.py` — exists, purpose: sorts Nahuatl dictionary document.
- `check_revisions.py` — exists, purpose: checks document revisions.
- `original_rev1.*` — source dictionary content in multiple formats (html, md, rtf, txt, xml).
- No plan file existed prior to this session; created now.

### Next steps
1. Decide on a concrete neologism strategy to implement (Chinese-model compounding is the recommendation).
2. Inventory existing Nahuatl roots available in the dictionary files — extract a usable root list from `original_rev1.*`.
3. Design a compounding schema: identify which Nahuatl morphological patterns (noun incorporation, derivational suffixes, etc.) will be used to build modern terms.
4. Build a candidate neologism list for a target domain (e.g., technology, medicine, daily modern life).
5. Consider integrating neologism rules into the `Nahuatl_Translator2` pipeline.

### Notes
- The **Chinese semantic compounding model** is the strongest fit: Nahuatl already uses compounding heavily (e.g., *teocalli* = teo- + calli). Extending this pattern for modern terms keeps the language internally coherent.
- Avoid Latin/Greek borrowing as a primary strategy — it creates stratification that tends to marginalize the native layer.
- INALI (Mexico's national linguistic institute) has active neologism working groups; worth checking for existing approved terms before coining new ones.
- Nahuatl phonology constraints: no /f/, no /r/ in classical Nahuatl — relevant if any phonological borrowing is needed.

---

## Checkpoint — 2026-08-24 (continued)

### Work completed this session
- **Ben-Yehuda literature survey:** Identified key books — Fellman (1973) *The Revival of a Classical Tongue* (primary academic study), St. John (1952) *Tongue of the Prophets* (popular biography), Zuckermann (2003) *Language Contact and Lexical Enrichment in Israeli Hebrew* (critical revisionist view), Chomsky W. (1957) *Hebrew: The Eternal Language*.
- **Clarified Ben-Yehuda's actual method:** Drew from Biblical, Mishnaic, and Medieval Hebrew plus Arabic cognates — NOT from Chinese. The Chinese/Hebrew parallel is an independent convergence of similar strategies, not a historical influence.
- **Corrected an overclaim:** Had suggested INALI maintains a public Nahuatl neologism list with a findable URL. User correctly challenged this. Confirmed: no consolidated, authoritative public neologism list for modern Nahuatl exists. Work is fragmented across academic papers and informal community efforts. No Hebrew Academy equivalent exists for Nahuatl.
- No code written or modified.

### Current state
Same as prior checkpoint. Research phase only.

### Next steps
1. Decide on a concrete neologism strategy (Chinese-model compounding recommended).
2. Inventory Nahuatl roots from `original_rev1.*` dictionary files.
3. Design a compounding schema using Nahuatl morphological patterns.
4. Build a candidate neologism list for a target domain.
5. Consider integrating neologism rules into `Nahuatl_Translator2`.

### Notes
- **No authoritative Nahuatl neologism list exists publicly.** The Nahuatl Wikipedia (`nah.wikipedia.org`) is the closest practical corpus of coined modern terms with community reasoning, but it is not official.
- Zuckermann's revisionist argument: Modern Israeli Hebrew is a hybrid with heavy Yiddish/European substrate — the "pure revival from roots" narrative is partially myth. Worth keeping in mind as a caution against overstating the purity of any revival effort.
- Ben-Yehuda's dictionary (17 volumes) is itself a model for the kind of systematic root inventory that would benefit this project.
