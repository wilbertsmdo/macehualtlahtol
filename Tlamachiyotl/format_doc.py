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

doc = service.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])

# ── Colour palette ──────────────────────────────────────────────────────────
NAVY  = {'red': 0.11, 'green': 0.20, 'blue': 0.42}
TEAL  = {'red': 0.00, 'green': 0.47, 'blue': 0.47}
ORANGE= {'red': 0.85, 'green': 0.33, 'blue': 0.00}

def rgb(c): return {'color': {'rgbColor': c}}

requests = []

# ── Walk every paragraph in the document ───────────────────────────────────
for elem in body:
    if 'paragraph' not in elem:
        continue
    p     = elem['paragraph']
    pstyle= p.get('paragraphStyle', {}).get('namedStyleType', 'NORMAL_TEXT')
    si    = elem.get('startIndex', 0)
    ei    = elem.get('endIndex',   0)
    if ei <= si:
        continue

    # Collect full text and per-run data
    runs = p.get('elements', [])
    full_text = ''.join(r.get('textRun', {}).get('content', '') for r in runs).rstrip('\n')
    if not full_text.strip():
        continue

    # ── 1. HEADING_2 → navy, bold, 13pt ────────────────────────────────────
    if pstyle == 'HEADING_2':
        requests.append({'updateTextStyle': {
            'range': {'startIndex': si, 'endIndex': ei - 1},
            'textStyle': {
                'foregroundColor': rgb(NAVY),
                'bold': True,
                'fontSize': {'magnitude': 13, 'unit': 'PT'},
            },
            'fields': 'foregroundColor,bold,fontSize'
        }})

    # ── 2. HEADING_3 → teal, bold, 11pt ────────────────────────────────────
    elif pstyle == 'HEADING_3':
        requests.append({'updateTextStyle': {
            'range': {'startIndex': si, 'endIndex': ei - 1},
            'textStyle': {
                'foregroundColor': rgb(TEAL),
                'bold': True,
                'fontSize': {'magnitude': 11, 'unit': 'PT'},
            },
            'fields': 'foregroundColor,bold,fontSize'
        }})

    # ── 3. HEADING_1 (my new section titles added last session) → upgrade ──
    #    Change to HEADING_2 style to match document structure
    elif pstyle == 'HEADING_1' and si > 60:   # skip title at idx=1
        requests.append({'updateParagraphStyle': {
            'range': {'startIndex': si, 'endIndex': ei},
            'paragraphStyle': {'namedStyleType': 'HEADING_2'},
            'fields': 'namedStyleType'
        }})
        requests.append({'updateTextStyle': {
            'range': {'startIndex': si, 'endIndex': ei - 1},
            'textStyle': {
                'foregroundColor': rgb(NAVY),
                'bold': True,
                'fontSize': {'magnitude': 13, 'unit': 'PT'},
            },
            'fields': 'foregroundColor,bold,fontSize'
        }})

    # ── 4. NORMAL_TEXT — selective bolding of labels ────────────────────────
    elif pstyle == 'NORMAL_TEXT':
        txt = full_text.strip()

        # 4a. "Risk —" labels → bold + orange for the label portion
        if txt.startswith('Risk —') or txt.startswith('Risk —'):
            dash_pos = txt.find('—')
            if dash_pos == -1:
                dash_pos = txt.find('-')
            # Bold the entire "Risk — [first sentence up to period or newline]"
            period = txt.find('.', dash_pos)
            label_end = period + 1 if period != -1 else min(len(txt), 80)
            # In doc coordinates: si + label_end (approximate, no multi-run issues for short labels)
            end_idx = min(si + label_end + 1, ei - 1)
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': end_idx},
                'textStyle': {
                    'bold': True,
                    'foregroundColor': rgb(ORANGE),
                },
                'fields': 'foregroundColor,bold'
            }})

        # 4b. "Mitigation." → bold + teal
        elif txt.startswith('Mitigation.') or txt.startswith('Mitigation '):
            label_end = min(si + 12, ei - 1)
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': label_end},
                'textStyle': {
                    'bold': True,
                    'foregroundColor': rgb(TEAL),
                },
                'fields': 'foregroundColor,bold'
            }})

        # 4c. "Phase 0 / Phase 1 / Phase 2 / Phase 3" in SPACE section → bold label
        elif txt.startswith('Phase ') and ('month' in txt.lower() or 'year' in txt.lower() or 'cost' in txt.lower()):
            paren = txt.find('(')
            label_end = paren if paren != -1 else min(len(txt), 12)
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': si + label_end},
                'textStyle': {'bold': True},
                'fields': 'bold'
            }})

        # 4d. Numbered/bulleted module lines "Module 1 —", "Module 2 —" etc → bold label
        elif txt.startswith('Module ') and '—' in txt:
            dash = txt.find('—')
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': si + dash + 1},
                'textStyle': {'bold': True},
                'fields': 'bold'
            }})

        # 4e. "Stage 1 —", "Stage 2 —", "Stage 3 —" → bold
        elif txt.startswith('Stage ') and '—' in txt:
            dash = txt.find('—')
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': si + dash + 1},
                'textStyle': {'bold': True},
                'fields': 'bold'
            }})

        # 4f. "Tier 1 —", "Tier 2 —" … (new sections) → bold label
        elif txt.startswith('Tier ') and ('—' in txt or ':' in txt):
            sep = txt.find('—') if '—' in txt else txt.find(':')
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': si + sep + 1},
                'textStyle': {'bold': True},
                'fields': 'bold'
            }})

        # 4g. "Concentration N —" lines → bold
        elif txt.startswith('Concentration ') and '—' in txt:
            dash = txt.find('—')
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': si + dash + 1},
                'textStyle': {'bold': True},
                'fields': 'bold'
            }})

        # 4h. "Seed (year…" / "Series A…" / "Scale…" / "Endowment…" → bold first token
        elif txt.startswith(('Seed (', 'Series A', 'Scale (', 'Endowment (')):
            paren = txt.find('(')
            label_end = paren if paren != -1 else 12
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': si + label_end},
                'textStyle': {'bold': True, 'foregroundColor': rgb(NAVY)},
                'fields': 'bold,foregroundColor'
            }})

        # 4i. "Option A —", "Option B —" etc → bold
        elif txt.startswith('Option ') and ('.' in txt[:10] or '—' in txt[:15]):
            sep = txt.find('.')
            if sep == -1 or sep > 15:
                sep = txt.find('—')
            if sep != -1:
                requests.append({'updateTextStyle': {
                    'range': {'startIndex': si, 'endIndex': si + sep + 1},
                    'textStyle': {'bold': True},
                    'fields': 'bold'
                }})

        # 4j. "Why dual-site works." / "Why Finance is…" → bold first sentence label
        elif txt.startswith('Why ') and '.' in txt[:60]:
            period = txt.find('.')
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': si + period + 1},
                'textStyle': {'bold': True},
                'fields': 'bold'
            }})

        # 4k. Lines starting with key named entities in new sections (e.g. "  Kellogg Foundation:")
        elif txt.strip().startswith(('W.K. Kellogg', 'Ford Foundation', 'IDB Invest', 'Christensen', 'Builders Vision',
                                      'Ceniarth', 'ImpactAssets', 'Raven Indigenous', 'Adobe Capital',
                                      'AIESEC', 'Enseña por', 'Codeando', 'Catchafire',
                                      'Karya', 'Remotasks', 'TELUS AI', 'Outlier',
                                      'Village Capital', 'Yunus', 'Potencia', 'African Entrepreneur')):
            colon = txt.find(':')
            dash  = txt.find('—')
            sep   = min([x for x in [colon, dash] if x != -1], default=-1)
            if sep == -1:
                sep = min(len(txt), 40)
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': si + sep + 1},
                'textStyle': {'bold': True},
                'fields': 'bold'
            }})

        # 4l. Inline comment lines left by WS → italicize
        elif 'WS comment' in txt or 'WS to AI' in txt or 'Comment to Claude' in txt:
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': ei - 1},
                'textStyle': {'italic': True, 'foregroundColor': rgb(ORANGE)},
                'fields': 'italic,foregroundColor'
            }})

        # 4m. "What the essay says" inline in NORMAL_TEXT → italic
        elif txt.startswith('What the essay says') or txt.startswith('The essay says'):
            period = txt.find('.')
            end = period + 1 if period != -1 else min(len(txt), 60)
            requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': si + end},
                'textStyle': {'italic': True, 'foregroundColor': rgb(TEAL)},
                'fields': 'italic,foregroundColor'
            }})

print(f"Total formatting requests: {len(requests)}")

# ── Execute in batches of 50 ────────────────────────────────────────────────
sent = 0
chunk_size = 50
for i in range(0, len(requests), chunk_size):
    chunk = requests[i:i+chunk_size]
    service.documents().batchUpdate(
        documentId=DOC_ID,
        body={'requests': chunk}
    ).execute()
    sent += len(chunk)
    print(f"  Applied {sent}/{len(requests)} requests")

print("Done.")
