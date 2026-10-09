import sys, time
sys.path.insert(0, '/data/data/com.termux/files/usr/lib/python3.13/site-packages')
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

DOC_ID = '1VB9eKJhOUtligj2oiBiFcqVkWrWS-ghBjW66qzsokZ4'
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(
    '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json',
    scopes=SCOPES
)
service = build('docs', 'v1', credentials=creds)

GRAY = {'red': 0.42, 'green': 0.42, 'blue': 0.42}
NAVY = {'red': 0.11, 'green': 0.20, 'blue': 0.42}
TEAL = {'red': 0.00, 'green': 0.47, 'blue': 0.47}
def rgb(c): return {'color': {'rgbColor': c}}

NEW_HUEJUTLA_PARA = (
    "Why Huejutla-first works. Phase 0–1 is a single site: Huejutla de Reyes. "
    "Infrastructure: fiber, hospital-grade medical, UAEH extension campus, banking, "
    "highway access — everything needed to operate a program and for the founder to live. "
    "Nahuatl-speaker population ~62,000 in the municipality: more than sufficient to fill "
    "a first cohort of 20–30 students from the cabecera and nearby communities. "
    "The founder is part-time on-site. Chicontepec (70% Nahuatl speakers, highest density) "
    "is the Phase 2 expansion once the Huejutla model is proven. "
    "Chicontepec-cabecera students who want to join in Phase 0–1 commute by colectivo (~45 min).\n"
)

# ── PASS 1: Text edits ───────────────────────────────────────────────────────
print("Pass 1: text edits...")
p1 = [
    # Fix "globally rare" → "high employability" framing
    {'replaceAllText': {
        'containsText': {'text': 'makes a graduate functionally globally rare', 'matchCase': True},
        'replaceText': 'makes a graduate rare in the global workforce and highly employable'
    }},
    # Clarify XP
    {'replaceAllText': {
        'containsText': {'text': 'Levels / XP.', 'matchCase': True},
        'replaceText': 'Levels / XP (Experience Points: students advance by completing and having peers validate projects, not by exams).'
    }},
    # Rewrite "Why dual-site works" paragraph
    {'deleteContentRange': {'range': {'startIndex': 6069, 'endIndex': 6549}}},
    {'insertText': {'location': {'index': 6069}, 'text': NEW_HUEJUTLA_PARA}},
]
service.documents().batchUpdate(documentId=DOC_ID, body={'requests': p1}).execute()
print("  Pass 1 done.")

# Style new heading
time.sleep(1)
doc = service.documents().get(documentId=DOC_ID).execute()
body = doc['body']['content']
fmt = []
for elem in body:
    if 'paragraph' not in elem: continue
    si, ei = elem.get('startIndex',0), elem.get('endIndex',0)
    text = ''.join(r.get('textRun',{}).get('content','') for r in elem['paragraph'].get('elements',[])).strip()
    if text.startswith('Why Huejutla-first works'):
        fmt += [
            {'updateParagraphStyle': {
                'range': {'startIndex': si, 'endIndex': ei},
                'paragraphStyle': {'namedStyleType': 'HEADING_3'},
                'fields': 'namedStyleType'
            }},
            {'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': ei - 1},
                'textStyle': {'foregroundColor': rgb(TEAL), 'bold': True,
                              'fontSize': {'magnitude': 11, 'unit': 'PT'}},
                'fields': 'foregroundColor,bold,fontSize'
            }},
        ]
        print(f"  Styled heading: '{text[:60]}'")
        break
if fmt:
    service.documents().batchUpdate(documentId=DOC_ID, body={'requests': fmt}).execute()

# ── PASS 2: Citations ────────────────────────────────────────────────────────
print("\nPass 2: finding citation targets...")
doc = service.documents().get(documentId=DOC_ID).execute()
body = doc['body']['content']

CITATION_MAP = [
    # (content_prefix_to_match, citation_text)
    ('First, the curriculum is delivered in Nahuatl as a medium',
     ' (UNESCO, 2010; Cummins, 2001; Olko & Sullivan, 2014)'),
    ('Clontarf Foundation (Australia, Aboriginal boys)',
     ' (NSW CESE, 2017)'),
    ('Why Finance is also an attitudinal intervention',
     ' (OECD, 2014; Luhrmann et al., 2023; Lusardi & Mitchell, 2014)'),
    ('The original brainstorm text noted',
     ' (Olko & Sullivan, 2014; UNESCO, 2010)'),
    ('Attendance is the single biggest predictor of retention',
     ' (Hancock et al., 2013; Dumuid et al., 2021)'),
    ('A note on the 2015 essay’s absence of sports',
     ' (NSW CESE, 2017; Macquarie Group, 2023)'),
    ('Risk — Nutrition / stunting undercuts',
     ' (Lozoff et al., Pediatrics; Kang et al., PLoS ONE 2014; Vendt et al., 2023)'),
    ('Nahuatl Huasteco has genuine scarcity value for LLM training',
     ' (UNESCO; Endangered Languages Project; AI4Bharat, 2023)'),
]

insertions = []
matched = set()
for elem in body:
    if 'paragraph' not in elem: continue
    si, ei = elem.get('startIndex',0), elem.get('endIndex',0)
    text = ''.join(r.get('textRun',{}).get('content','') for r in elem['paragraph'].get('elements',[])).strip()
    for key, cite in CITATION_MAP:
        if key not in matched and text.startswith(key[:45]):
            insertions.append((ei - 1, cite, key[:50]))
            matched.add(key)
            break

insertions.sort(key=lambda x: -x[0])
print(f"  Found {len(insertions)} citation targets:")
for idx, cite, key in insertions:
    print(f"    idx={idx}: {key[:50]} → {cite}")

requests_p2 = []
for idx, cite, _ in insertions:
    requests_p2.append({'insertText': {
        'location': {'index': idx},
        'text': cite
    }})
    requests_p2.append({'updateTextStyle': {
        'range': {'startIndex': idx, 'endIndex': idx + len(cite)},
        'textStyle': {
            'foregroundColor': rgb(GRAY),
            'fontSize': {'magnitude': 8, 'unit': 'PT'},
            'italic': True
        },
        'fields': 'foregroundColor,fontSize,italic'
    }})

if requests_p2:
    service.documents().batchUpdate(documentId=DOC_ID, body={'requests': requests_p2}).execute()
    print(f"  Applied {len(requests_p2)} citation requests.")
print("Done.")
