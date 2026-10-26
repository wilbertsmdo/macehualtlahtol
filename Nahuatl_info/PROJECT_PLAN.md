# Nahuatl_info — Project Plan

**Created:** 2026-10-20
**Last updated:** 2026-10-20
**Status:** Active

---

## Overview

Research and reference materials for Classical Nahuatl study. Includes the Huehuei Nahuatl Google Doc (shared study notes for University of Utah / Yale Nahuatl courses), scrapers, and dictionary data. Work in this project typically involves reading, organizing, and reformatting content from the Huehuei Nahuatl document and related resources.

**Primary doc:** Huehuei Nahuatl Google Doc (`1SLl9ZsJ6KplraIlOk3gv2ZEnX1-YsAKzTrokAI7sChs`) — shared with service account `ws-financial-analysis@qwen-project-492821.iam.gserviceaccount.com`.

---

## Checkpoint — 2026-10-20

### Work completed this session

- **Read Huehuei Nahuatl Google Doc** (pages 229–230) via the Docs API using the service account. Identified two major tables in the `#tlahtoltecpaniliztli` section:
  - *Side-by-side table* (elem [4389]): Verb Stem / Agentive Noun / Active Action Noun / Patientive Noun — already a proper Google Docs table.
  - *Summary Table* (elems 4444–4449): Turning *cāhcāhua* into a noun — existed only as markdown text, not a real table.
  - *Deverbal Adjectives table* (elem [4456]): already a proper Google Docs table.
  - *Deverbal Adverbs* (elems 4474–4487): existed only as loose paragraphs, no proper table.
- **Presented all four tables** as clean markdown in the chat (column headers + rows).
- **Inserted all four tables as editable Google Docs tables** into the document at the end of the `#tlahtoltecpaniliztli` section, just before `#tlahtolxitlauhcayotl` (vocabulary list), using `batchUpdate` (insertTable + insertText in reverse-index order). Each table was given a plain-text title heading above it:
  1. "Side-by-side (pg 229): Verb Stem / Noun Types" — 6 rows × 4 cols
  2. "Summary (pg 229): Turning cahcahua into a Noun" — 5 rows × 4 cols
  3. "Deverbal Adjectives (pg 230): Verbs to Adjectival Modifiers" — 7 rows × 4 cols
  4. "Deverbal Adverbs (pg 230)" — 5 rows × 4 cols
- Verified insertion by re-reading the document via API and confirming all cell content was present.

### Current state

The Huehuei Nahuatl Google Doc now has four clean, editable tables at the end of the `#tlahtoltecpaniliztli` section (document indices ~149773–153301). The original content (markdown Summary Table text and loose Deverbal Adverbs paragraphs) still exists earlier in the document and was not removed.

### Next steps

1. (Optional) Delete the now-redundant markdown Summary Table text (doc elems around si=144110–144775) and the loose Deverbal Adverbs paragraphs (si≈148103–149720) to clean up duplicates.
2. Continue reading and organizing additional pages of the Huehuei Nahuatl doc as needed for study sessions.
3. Add any scraped/dictionary data to `Lockhart_Scraper/` or `Nahuatl_Dic/` as those pipelines develop.

### Notes

- The doc has 4698+ structural elements and is too large for HTML export via Drive API (`exportSizeLimitExceeded`). Use the Docs API (`documents().get()`) for reading; use plain-text export (`text/plain`) for bulk text searches.
- Physical page numbers in the Google Doc are not derivable from the API (no explicit page break markers beyond 14 manual ones). "Page 229" was located by identifying content described by the user (4-column table header at the end of `#tlahtoltecpaniliztli`).
- Cell text insertion uses `insertText` at `content[0].startIndex` of each empty cell, applied in reverse-index order within a single `batchUpdate` call to preserve index validity.
