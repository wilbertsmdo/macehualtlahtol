import sys, time
sys.path.insert(0, '/data/data/com.termux/files/usr/lib/python3.13/site-packages')
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

DOC_ID = '1VB9eKJhOUtligj2oiBiFcqVkWrWS-ghBjW66qzsokZ4'
creds = Credentials.from_service_account_file(
    '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json',
    scopes=['https://www.googleapis.com/auth/documents']
)
docs = build('docs', 'v1', credentials=creds)

def get_doc():
    return docs.documents().get(documentId=DOC_ID).execute()

def get_h2_sections(doc):
    body = doc.get('body', {}).get('content', [])
    doc_end = body[-1].get('endIndex', 0) if body else 0
    headings = []
    for elem in body:
        if 'paragraph' not in elem: continue
        ps = elem['paragraph'].get('paragraphStyle', {})
        if ps.get('namedStyleType') != 'HEADING_2': continue
        hid = ps.get('headingId', '')
        text = ''.join(r.get('textRun',{}).get('content','')
                       for r in elem['paragraph'].get('elements',[])).strip()
        headings.append({'hid': hid, 'text': text,
                         'si': elem['startIndex'], 'ei': elem['endIndex']})
    for i, h in enumerate(headings):
        h['section_end'] = headings[i+1]['si'] if i+1 < len(headings) else doc_end
    return headings

def find_sec(sections, hid=None, prefix=None):
    for s in sections:
        if hid and s['hid'] == hid: return s
        if prefix and s['text'].startswith(prefix): return s
    return None

def get_elems(doc, start, end):
    body = doc.get('body', {}).get('content', [])
    out = []
    for elem in body:
        if elem.get('endIndex', 0) <= start: continue
        if elem.get('startIndex', 0) >= end: break
        out.append(elem)
    return out

def extract_ps(ps):
    r, f = {}, []
    for field in ['namedStyleType', 'alignment', 'lineSpacing']:
        if field in ps:
            r[field] = ps[field]; f.append(field)
    for field in ['spaceAbove', 'spaceBelow', 'indentStart', 'indentEnd', 'indentFirstLine']:
        if field in ps and isinstance(ps[field], dict) and 'magnitude' in ps[field]:
            r[field] = ps[field]; f.append(field)
    return r, f

def extract_ts(ts):
    r, f = {}, []
    for field in ['bold', 'italic', 'underline', 'strikethrough', 'smallCaps']:
        if field in ts:
            r[field] = ts[field]; f.append(field)
    if 'fontSize' in ts:
        r['fontSize'] = ts['fontSize']; f.append('fontSize')
    if 'foregroundColor' in ts and ts['foregroundColor']:
        r['foregroundColor'] = ts['foregroundColor']; f.append('foregroundColor')
    if 'link' in ts and ts['link']:
        lnk = ts['link']
        if lnk.get('url') or lnk.get('headingId') or lnk.get('bookmarkId'):
            r['link'] = lnk; f.append('link')
    if ts.get('baselineOffset', 'NONE') != 'NONE':
        r['baselineOffset'] = ts['baselineOffset']; f.append('baselineOffset')
    return r, f

def build_requests(elems, insert_at):
    reqs = []
    full = ''
    for elem in elems:
        if 'paragraph' not in elem: continue
        for run in elem['paragraph'].get('elements', []):
            full += run.get('textRun', {}).get('content', '')
    if not full:
        return reqs, 0
    reqs.append({'insertText': {'location': {'index': insert_at}, 'text': full}})
    pos = insert_at
    for elem in elems:
        if 'paragraph' not in elem: continue
        p = elem['paragraph']
        para = ''.join(r.get('textRun',{}).get('content','') for r in p.get('elements',[]))
        if not para: continue
        para_end = pos + len(para)
        ps, pf = extract_ps(p.get('paragraphStyle', {}))
        if ps:
            reqs.append({'updateParagraphStyle': {
                'range': {'startIndex': pos, 'endIndex': para_end},
                'paragraphStyle': ps, 'fields': ','.join(pf)}})
        rpos = pos
        for run_elem in p.get('elements', []):
            tr = run_elem.get('textRun', {})
            if not tr: continue
            rc = tr.get('content', '')
            rend = rpos + len(rc)
            ts, tf = extract_ts(tr.get('textStyle', {}))
            if ts:
                reqs.append({'updateTextStyle': {
                    'range': {'startIndex': rpos, 'endIndex': rend},
                    'textStyle': ts, 'fields': ','.join(tf)}})
            rpos = rend
        pos = para_end
    return reqs, len(full)

def batch(reqs, label):
    n = len(reqs)
    if n == 0: print(f"  {label}: 0 reqs"); return
    print(f"  {label}: {n} reqs", end='', flush=True)
    for i in range(0, n, 50):
        docs.documents().batchUpdate(
            documentId=DOC_ID, body={'requests': reqs[i:i+50]}).execute()
        print('.', end='', flush=True)
    print(' done')

def move_back(target_hid, target_prefix, sec_hid, sec_prefix):
    """Move section backward: insert copy at target.section_end, delete original."""
    doc = get_doc()
    secs = get_h2_sections(doc)
    tgt = find_sec(secs, hid=target_hid, prefix=target_prefix)
    sec = find_sec(secs, hid=sec_hid, prefix=sec_prefix)
    if not tgt: print(f"  ERROR: target not found ({target_prefix})"); return
    if not sec: print(f"  ERROR: section not found ({sec_prefix})"); return
    ins = tgt['section_end']
    s_si, s_end = sec['si'], sec['section_end']
    print(f"  BACK [{sec['text'][:45]}] -> after [{tgt['text'][:35]}] ins={ins} sec=[{s_si},{s_end})")
    elems = get_elems(doc, s_si, s_end)
    reqs, tlen = build_requests(elems, ins)
    reqs.append({'deleteContentRange': {'range': {
        'startIndex': s_si + tlen, 'endIndex': s_end + tlen}}})
    batch(reqs, sec['text'][:30])
    time.sleep(1)

def move_fwd(sec_hid, sec_prefix, target_hid, target_prefix):
    """Move section forward: delete original, insert at shifted target."""
    doc = get_doc()
    secs = get_h2_sections(doc)
    sec = find_sec(secs, hid=sec_hid, prefix=sec_prefix)
    tgt = find_sec(secs, hid=target_hid, prefix=target_prefix)
    if not sec: print(f"  ERROR: section not found ({sec_prefix})"); return
    if not tgt: print(f"  ERROR: target not found ({target_prefix})"); return
    s_si, s_end = sec['si'], sec['section_end']
    tgt_ins = tgt['section_end']
    slen = s_end - s_si
    print(f"  FWD  [{sec['text'][:45]}] -> after [{tgt['text'][:35]}]")
    elems = get_elems(doc, s_si, s_end)
    # Delete first
    batch([{'deleteContentRange': {'range': {'startIndex': s_si, 'endIndex': s_end}}}],
          f"del {sec['text'][:20]}")
    time.sleep(1)
    # Insert at adjusted target
    adj = tgt_ins - slen
    reqs, _ = build_requests(elems, adj)
    batch(reqs, f"ins {sec['text'][:20]}")
    time.sleep(1)

# ══════════════════════════════════════════════════════════════════
# BACKWARD MOVES  (highest current_si first)
# ══════════════════════════════════════════════════════════════════
print("=== BACKWARD MOVES ===")

print("1. ARTS & MUSIC → after SPORTS")
move_back('h.fzp4fcum54u', 'SPORTS', 'h.cij363rb0odp', 'ARTS & MUSIC')

print("2. LANGUAGES SPANISH → after LANGUAGES NAHUATL")
move_back('h.o45nn6895tn2', 'LANGUAGES — NAHUATL', 'h.3sxup0th22jo', 'LANGUAGES — SPANISH')

print("3. FINANCE MODULE 6 → after FINANCE TRACK")
move_back('h.o21hc4nfks4l', 'FINANCE TRACK', 'h.6sooeo2blwjs', 'FINANCE MODULE 6')

print("4. ONLINE CURRICULA + 4-WEEK BOOTCAMP → after STEM (combined move)")
doc = get_doc()
secs = get_h2_sections(doc)
stem   = find_sec(secs, hid='h.kzkdajo06pwx', prefix='STEM')
online = find_sec(secs, prefix='ONLINE CURRICULA')
boot   = find_sec(secs, prefix='THE 4-WEEK BOOTCAMP')
if stem and online and boot:
    ins = stem['section_end']
    combined_si  = online['si']
    combined_end = boot['section_end']
    print(f"  combined [{online['text'][:30]}]+[{boot['text'][:25]}] ins={ins}")
    elems = get_elems(doc, combined_si, combined_end)
    reqs, tlen = build_requests(elems, ins)
    reqs.append({'deleteContentRange': {'range': {
        'startIndex': combined_si + tlen, 'endIndex': combined_end + tlen}}})
    batch(reqs, 'ONLINE+BOOTCAMP')
    time.sleep(1)
else:
    print("  ERROR finding STEM / ONLINE / BOOTCAMP sections")

print("5. STUDENT DIGITAL INCOME → after ARTS & MUSIC")
move_back(None, 'ARTS & MUSIC', 'h.pi90k76hm85u', 'STUDENT DIGITAL INCOME')

print("6. JOB PIPELINE → after STUDENT DIGITAL INCOME")
move_back(None, 'STUDENT DIGITAL INCOME', 'h.7iq7wqtz5ygo', 'JOB PIPELINE')

# ══════════════════════════════════════════════════════════════════
# FORWARD MOVES  (lowest current_si first)
# ══════════════════════════════════════════════════════════════════
print("\n=== FORWARD MOVES ===")

print("7. APPENDIX A → after NUTRITION")
move_fwd('h.j86a4rvaxdro', 'APPENDIX A', 'h.2cjzfqk24oqp', 'NUTRITION')

print("8. APPENDIX B → after APPENDIX A")
move_fwd('h.jk0mtafrl2jg', 'APPENDIX B', None, 'APPENDIX A')

print("9. APPENDIX C → after APPENDIX B")
move_fwd('h.oe4lnjxs823a', 'APPENDIX C', None, 'APPENDIX B')

print("10. EVIDENCE BASE → after APPENDIX F")
move_fwd('h.d5v49em4jemy', 'EVIDENCE BASE', 'h.b9axv7eumr7i', 'APPENDIX F')

print("11. ACADEMIC REFERENCES → after EVIDENCE BASE")
move_fwd('h.c0l8ynnvq8n3', 'ACADEMIC REFERENCES', None, 'EVIDENCE BASE')

print("\n=== DONE — printing new section order ===")
doc = get_doc()
secs = get_h2_sections(doc)
for s in secs:
    if s['si'] > 2000:
        print(f"  si={s['si']:7d}  {s['text'][:70]}")
