"""
parse_lockhart.py
Parses Lockhart 2001 "Nahuatl as Written" (264-page PDF) and uploads to a Google Doc.

Design:
  • extract_text() gives clean lines → used for all text and heading detection.
  • extract_words() gives x/y positions → used only for multi-column detection.
    Y-buckets of 15 px merge the 2-4 px vertical scatter between OCR'd left- and
    right-column words, so inter-column x-gaps are correctly detected.
  • Vocab section (pp.219-255): full left/right x-split at 350 px → 2-col table.
"""

import sys, re, io, html as html_module
sys.path.insert(0, '/data/data/com.termux/files/usr/lib/python3.13/site-packages')

import pdfplumber
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# ── Config ────────────────────────────────────────────────────────────────────
PDF    = ("/storage/self/primary/PY_Projects/Piltzin_Tlamantli/"
          "Lockhart_Scraper/Lockhart_2001_NAWocr.pdf")
DOC_ID = "1Uyp0be0k6QBuyrrhCGYz36HC5hVv_paXbhC4SAyfxJE"
TOKEN  = ("/storage/self/primary/PY_Projects/Financial_Analysis_App/"
          "python/token.json")
SCOPES = ["https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/spreadsheets"]

VOCAB_START = 218   # 0-based page index (page 219)
VOCAB_END   = 255   # exclusive
VOCAB_COL_X = 350   # x-split for vocabulary columns
COL_GAP     = 65    # minimum x-gap (pts) between table columns
ROW_CLUSTER = 5.0   # max vertical scatter (pts) within a single OCR scan-line

# ── Auth ──────────────────────────────────────────────────────────────────────
def get_drive_svc():
    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN, "w") as f:
            f.write(creds.to_json())
    return build("drive", "v3", credentials=creds)

# ── Pattern matchers ──────────────────────────────────────────────────────────
esc = html_module.escape

RE_RUNNING = re.compile(
    r'^\d*\s*[-–]\s*Lesson\s+\d+\s*[-–]'
    r'|^[-–]\s*Lesson\s+\d+\s*[-–]'
    r'|^Nahuatl as Written$'
    r'|^VOCABULARY$'
    r'|^[•·\-─=\s]+$',
    re.I
)
RE_PAGE_NUM   = re.compile(r'^\d{1,3}$')
RE_LESSON_H   = re.compile(r'^(\d{1,2})\.\s+[A-Z][^.]{5,70}[^.]$')  # title, no trailing period
RE_MAJOR_H    = re.compile(
    # Title-cased words only (no re.I) so prose lines starting with lowercase
    # "vocabulary…", "index…" etc. never match.
    # Optional suffix must start with punctuation (colon, dash, period) or a
    # digit — not a plain lowercase word like "and" / "to".
    r'^(Preface|Epilogue|Vocabulary|Index|Contents|Bibliography'
    r'|Appendix\s+\d+)'
    r'(?:\s*[\-–:\.]\s*.*|\s+\d+.*)?$'
)
# Inline section heading: "A. Subject prefixes. <prose...>"  or standalone "A. Subject prefixes."
# Group 1 = heading, Group 2 = rest of prose (may be empty)
RE_INLINE_H   = re.compile(
    r'^([A-Z][A-Za-z0-9]?\.\s+[A-Z][^.]{3,50}\.)'  # "A. Short title."
    r'(?:\s+([A-Z].*))?$'                             # optional prose after
)
RE_FOOTNOTE   = re.compile(r'^\d+[TtIil]?\.\s+[A-Z]')

# ── HTML builder ──────────────────────────────────────────────────────────────
class Builder:
    def __init__(self):
        self.parts     = []
        self._para_buf = []
        self._tbl_rows = []

    def _flush_para(self):
        if self._para_buf:
            text = re.sub(r'\s+', ' ', ' '.join(self._para_buf)).strip()
            if text:
                self.parts.append(f'<p>{esc(text)}</p>')
            self._para_buf = []

    def _flush_table(self):
        if self._tbl_rows:
            rows_html = []
            for cells in self._tbl_rows:
                tds = ''.join(
                    f'<td style="padding:3px 8px;vertical-align:top">{esc(c)}</td>'
                    for c in cells
                )
                rows_html.append(f'<tr>{tds}</tr>')
            self.parts.append(
                '<table border="1" cellspacing="0" cellpadding="0"'
                ' style="border-collapse:collapse;margin:6px 0">'
                + ''.join(rows_html) + '</table>'
            )
            self._tbl_rows = []

    def flush(self):
        self._flush_para()
        self._flush_table()

    def heading(self, text, level):
        self.flush()
        self.parts.append(f'<h{level}>{esc(text)}</h{level}>')

    def para_line(self, line):
        self._flush_table()
        self._para_buf.append(line)

    def para_break(self):
        self._flush_para()

    def table_row(self, cells):
        self._flush_para()
        self._tbl_rows.append(cells)

    def raw(self, html_str):
        self.flush()
        self.parts.append(html_str)

    def build(self):
        self.flush()
        return '\n'.join(self.parts)

# ── Word-position index (scan-line clustering) ────────────────────────────────
def build_word_index(page):
    """
    Cluster words into scan-lines using greedy single-linkage on y (max gap =
    ROW_CLUSTER pts). This merges the 2-4 pt vertical OCR scatter between
    left- and right-column words on the same visual row, while keeping distinct
    rows (typically 10-12 pt apart) in separate clusters.

    Returns:
      words_stream — sorted by (top, x0) for sequential cursor lookup
      cluster_map  — {cluster_id: {'centroid': float, 'max_gap': float,
                                    'words': [words sorted by x0]}}
      word_cluster — {word index in stream → cluster_id}
    """
    raw = page.extract_words(x_tolerance=4, y_tolerance=3)
    words_stream = sorted(raw, key=lambda w: (w['top'], w['x0']))

    if not words_stream:
        return [], {}, {}

    # Greedy single-linkage clustering by sorted y
    clusters_raw = []  # list of lists of words
    current = [words_stream[0]]
    for w in words_stream[1:]:
        if w['top'] - current[-1]['top'] <= ROW_CLUSTER:
            current.append(w)
        else:
            clusters_raw.append(current)
            current = [w]
    clusters_raw.append(current)

    cluster_map  = {}
    word_cluster = {}
    for cid, cws in enumerate(clusters_raw):
        ws_x = sorted(cws, key=lambda w: w['x0'])
        centroid = sum(w['top'] for w in cws) / len(cws)
        gaps = [ws_x[i+1]['x0'] - ws_x[i]['x1'] for i in range(len(ws_x) - 1)]
        cluster_map[cid] = {
            'centroid': centroid,
            'max_gap':  max(gaps) if gaps else 0,
            'words':    ws_x,
        }
        for w in cws:
            word_cluster[id(w)] = cid

    return words_stream, cluster_map, word_cluster


def find_cluster_for_line(first_tok, words_stream, word_cluster, cursor):
    """
    Scan words_stream from cursor (up to 150 words) for first_tok.
    Returns (cluster_id, new_cursor) or (None, cursor).
    """
    limit = min(cursor + 150, len(words_stream))
    for i in range(cursor, limit):
        if words_stream[i]['text'] == first_tok:
            cid = word_cluster.get(id(words_stream[i]))
            return cid, i + 1
    return None, cursor


def cells_from_cluster(cid, cluster_map):
    """Split the cluster's x-sorted words into cells at gaps > COL_GAP."""
    info = cluster_map.get(cid)
    if not info:
        return []
    ws = info['words']
    cells, cur = [], [ws[0]['text']]
    for i in range(1, len(ws)):
        if ws[i]['x0'] - ws[i-1]['x1'] > COL_GAP:
            cells.append(' '.join(cur))
            cur = []
        cur.append(ws[i]['text'])
    cells.append(' '.join(cur))
    return [c for c in cells if c.strip()]

# ── Vocabulary page processor ─────────────────────────────────────────────────
def vocab_page_html(page):
    words = page.extract_words(x_tolerance=5, y_tolerance=4)
    left_ws  = [w for w in words if w['x0'] < VOCAB_COL_X]
    right_ws = [w for w in words if w['x0'] >= VOCAB_COL_X]

    def col_html(ws):
        by_y = {}
        for w in ws:
            yb = round(w['top'] / 5) * 5
            by_y.setdefault(yb, []).append(w)
        lines = []
        for yb in sorted(by_y):
            txt = ' '.join(w['text'] for w in sorted(by_y[yb], key=lambda w: w['x0'])).strip()
            if txt and not RE_PAGE_NUM.match(txt) and txt.upper() != 'VOCABULARY':
                lines.append(esc(txt))
        return '<br>'.join(lines)

    td = 'style="padding:4px 12px;vertical-align:top;width:50%"'
    return f'<tr><td {td}>{col_html(left_ws)}</td><td {td}>{col_html(right_ws)}</td></tr>'

# ── Normal page processor ─────────────────────────────────────────────────────
def process_page(page, builder):
    text = page.extract_text() or ""
    if not text.strip():
        return

    words_stream, cluster_map, word_cluster = build_word_index(page)
    cursor = 0
    used_clusters = set()  # prevent duplicate table rows from the same cluster

    for raw_line in text.split('\n'):
        line = raw_line.strip()
        if not line:
            builder.para_break()
            continue

        # ── Noise ─────────────────────────────────────────────────────────────
        if RE_RUNNING.match(line) or RE_PAGE_NUM.match(line):
            builder.para_break()
            continue

        # ── Major / lesson headings ────────────────────────────────────────────
        if RE_MAJOR_H.match(line):
            builder.heading(line, 2)
            _, cursor = find_cluster_for_line(
                line.split()[0], words_stream, word_cluster, cursor)
            continue

        if RE_LESSON_H.match(line):
            builder.heading(line, 2)
            _, cursor = find_cluster_for_line(
                line.split()[0], words_stream, word_cluster, cursor)
            continue

        # ── Inline section heading: "A. Short title. <prose…>" ────────────────
        m = RE_INLINE_H.match(line)
        if m:
            builder.heading(m.group(1), 3)
            _, cursor = find_cluster_for_line(
                line.split()[0], words_stream, word_cluster, cursor)
            prose_rest = m.group(2) or ""
            if prose_rest:
                builder.para_line(prose_rest)
            continue

        # ── Multi-column detection ─────────────────────────────────────────────
        first_tok = line.split()[0] if line.split() else ""
        cid, cursor = find_cluster_for_line(
            first_tok, words_stream, word_cluster, cursor)

        max_gap = cluster_map[cid]['max_gap'] if cid is not None else 0

        if max_gap >= COL_GAP and cid not in used_clusters:
            cells = cells_from_cluster(cid, cluster_map)
            if len(cells) >= 2:
                builder.table_row(cells)
                used_clusters.add(cid)
                continue

        # ── Regular prose ──────────────────────────────────────────────────────
        builder.para_line(line)

    builder.para_break()

# ── Full book builder ─────────────────────────────────────────────────────────
def build_book_html(pdf_path):
    b = Builder()
    b.heading("Nahuatl as Written", 1)
    b.raw('<p><em>James Lockhart — Stanford University Press / '
          'UCLA Latin American Center Publications, 2001</em></p>')

    in_vocab = False
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for idx, page in enumerate(pdf.pages):
            print(f"  Page {idx+1}/{total}…", end='\r')

            if VOCAB_START <= idx < VOCAB_END:
                if not in_vocab:
                    in_vocab = True
                    b.heading("Vocabulary", 2)
                    b.raw(
                        '<table border="1" cellspacing="0" cellpadding="0"'
                        ' style="border-collapse:collapse;width:100%;margin:6px 0">'
                    )
                b.parts.append(vocab_page_html(page))
                continue

            if in_vocab:
                in_vocab = False
                b.parts.append('</table>')

            process_page(page, b)

    if in_vocab:
        b.parts.append('</table>')

    print(f"\n  Processed {total} pages.")
    return b.build()

# ── Upload ────────────────────────────────────────────────────────────────────
def upload_html(svc, doc_id, html):
    body = html.encode('utf-8')
    media = MediaIoBaseUpload(io.BytesIO(body), mimetype='text/html', resumable=False)
    svc.files().update(fileId=doc_id, media_body=media).execute()
    print(f"  Uploaded {len(body)//1024} KB → {doc_id}")

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("Step 1: Building HTML…")
    body = build_book_html(PDF)

    full_html = (
        '<!DOCTYPE html><html><head><meta charset="utf-8"><style>'
        'body{font-family:Georgia,serif;font-size:11pt;line-height:1.5;margin:40px}'
        'h1{font-size:18pt;margin-top:24px}'
        'h2{font-size:14pt;margin-top:20px;border-bottom:1px solid #ccc}'
        'h3{font-size:12pt;margin-top:14px}'
        'table{border-collapse:collapse;font-size:10pt}'
        'td{border:1px solid #aaa;padding:3px 8px;vertical-align:top}'
        'p{margin:6px 0}'
        '</style></head><body>' + body + '</body></html>'
    )

    local = ("/storage/self/primary/PY_Projects/Piltzin_Tlamantli/"
             "Lockhart_Scraper/lockhart_parsed.html")
    with open(local, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"  Local copy → {local}")

    print("Step 2: Uploading to Google Doc…")
    svc = get_drive_svc()
    upload_html(svc, DOC_ID, full_html)
    print("Done.")
    print(f"  https://docs.google.com/document/d/{DOC_ID}/edit")
