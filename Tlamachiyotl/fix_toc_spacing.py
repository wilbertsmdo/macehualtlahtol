import sys
sys.path.insert(0, '/data/data/com.termux/files/usr/lib/python3.13/site-packages')
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

DOC_ID = '1VB9eKJhOUtligj2oiBiFcqVkWrWS-ghBjW66qzsokZ4'
SCOPES = ['https://www.googleapis.com/auth/documents']
creds = Credentials.from_service_account_file(
    '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json',
    scopes=SCOPES
)
service = build('docs', 'v1', credentials=creds)

NAVY = {'red': 0.11, 'green': 0.20, 'blue': 0.42}
TEAL = {'red': 0.00, 'green': 0.47, 'blue': 0.47}

def rgb(c): return {'color': {'rgbColor': c}}
def pt(n): return {'magnitude': n, 'unit': 'PT'}

CATEGORY_LABELS = {
    'CORE SECTIONS',
    'CURRICULUM AREAS (added 2026)',
    'ACADEMY DESIGN & OPERATIONS',
    'APPENDICES',
    'RESEARCH & EVIDENCE',
}

doc = service.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])

requests = []

for elem in body:
    si = elem.get('startIndex', 0)
    ei = elem.get('endIndex', 0)
    if 'paragraph' not in elem:
        continue

    p = elem['paragraph']
    text = ''.join(r.get('textRun', {}).get('content', '') for r in p.get('elements', [])).strip()
    named = p.get('paragraphStyle', {}).get('namedStyleType', '')

    # ── TOC "Table of Contents" title ────────────────────────────────────────
    if si == 477 and text == 'Table of Contents':
        # Keep as HEADING_2 but set compact spacing (no inherited large heading gap)
        requests.append({'updateParagraphStyle': {
            'range': {'startIndex': si, 'endIndex': ei},
            'paragraphStyle': {
                'spaceAbove': pt(0),
                'spaceBelow': pt(4),
                'lineSpacing': 100,
            },
            'fields': 'spaceAbove,spaceBelow,lineSpacing'
        }})
        continue

    # ── TOC entries (si 495–1972): all currently HEADING_2, fix to NORMAL_TEXT ─
    if 495 <= si <= 1972 and named == 'HEADING_2':
        is_cat = text in CATEGORY_LABELS

        # Change paragraph style to NORMAL_TEXT with tight spacing
        requests.append({'updateParagraphStyle': {
            'range': {'startIndex': si, 'endIndex': ei},
            'paragraphStyle': {
                'namedStyleType': 'NORMAL_TEXT',
                'spaceAbove': pt(6) if is_cat else pt(0),
                'spaceBelow': pt(1) if is_cat else pt(0),
                'lineSpacing': 110,
                'indentStart': pt(0),
                'indentFirstLine': pt(0),
            },
            'fields': 'namedStyleType,spaceAbove,spaceBelow,lineSpacing,indentStart,indentFirstLine'
        }})

        if is_cat:
            # Category label: bold navy 9.5pt
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': ei - 1},
                'textStyle': {
                    'bold': True,
                    'foregroundColor': rgb(NAVY),
                    'fontSize': pt(9.5),
                },
                'fields': 'bold,foregroundColor,fontSize'
            }})
        else:
            # Link entry: teal 9pt with link already applied — just lock in spacing/size
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': ei - 1},
                'textStyle': {
                    'bold': False,
                    'foregroundColor': rgb(TEAL),
                    'fontSize': pt(9),
                },
                'fields': 'bold,foregroundColor,fontSize'
            }})

        print(f"  {'CAT ' if is_cat else 'LINK'} si={si:5d}: {text[:65]}")
        continue

    # ── Actual PREFACE heading at si=1973 — restore correct H2 style ─────────
    if si == 1973 and 'PREFACE' in text:
        # Remove the accidental link + teal color applied by the previous script
        requests.append({'updateTextStyle': {
            'range': {'startIndex': si, 'endIndex': ei - 1},
            'textStyle': {
                'link': None,               # null clears the link field
                'foregroundColor': rgb(NAVY),
                'bold': True,
                'fontSize': pt(13),
            },
            'fields': 'link,foregroundColor,bold,fontSize'
        }})
        print(f"  FIXD si={si:5d}: PREFACE heading restored")
        continue

print(f"\nApplying {len(requests)} requests...")
for i in range(0, len(requests), 50):
    service.documents().batchUpdate(
        documentId=DOC_ID, body={'requests': requests[i:i+50]}
    ).execute()
    print(f"  {min(i+50, len(requests))}/{len(requests)}")

print("Done.")
