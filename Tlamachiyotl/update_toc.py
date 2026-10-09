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

NAVY   = {'red': 0.11, 'green': 0.20, 'blue': 0.42}
TEAL   = {'red': 0.00, 'green': 0.47, 'blue': 0.47}
GRAY   = {'red': 0.55, 'green': 0.55, 'blue': 0.55}

def rgb(c): return {'color': {'rgbColor': c}}

# ── TOC structure: (display_text, headingId, is_category_label) ──────────────
TOC = [
    ("CORE SECTIONS",                                         None,                 True),
    ("PREFACE — ANCHORING TO THE 2015 ESSAY",                "h.uys0mks063ty",     False),
    ("VISION & FRAMING",                                     "h.t17h1zmf4jur",     False),
    ("LOCATION — HUEJUTLA HQ + CHICONTEPEC SATELLITE",       "h.r0ql3kapglvo",     False),
    ("STEM CURRICULUM — THE 42-HUASTECA MODEL",              "h.kzkdajo06pwx",     False),
    ("FINANCE TRACK — THE EXPLICIT FIFTH LAYER",             "h.o21hc4nfks4l",     False),
    ("LANGUAGES — NAHUATL, ENGLISH, MANDARIN",               "h.o45nn6895tn2",     False),
    ("NAHUATL FRAMEWORK & CULTURAL PRODUCTION",              "h.ntthsql5ceui",     False),
    ("SPORTS INTEGRATION",                                   "h.fzp4fcum54u",      False),
    ("SPACE, EQUIPMENT & CAMPUS STAGING",                    "h.v3e88y6dq3la",     False),
    ("PARTNERSHIP MATRIX — CURRICULUM",                      "h.eypsk0ubehn9",     False),
    ("FUNDING STRATEGY — STAGED",                            "h.eadabpo8v2su",     False),
    ("JOB PIPELINE — THE SEO-FOR-NAHUA MODEL",               "h.7iq7wqtz5ygo",     False),
    ("LEVERAGING YOUR BACKGROUND — CONCRETE ASKS",           "h.gws4tzjrihyz",     False),
    ("RISKS & OPEN QUESTIONS",                               "h.p4z6mvgpgqq0",     False),

    ("CURRICULUM AREAS (added 2026)",                        None,                 True),
    ("ARTS & MUSIC — CURRICULUM AREA",                       "h.cij363rb0odp",     False),
    ("ONLINE CURRICULA & BOOTCAMP RESOURCES",                "h.r19s5txeps6h",     False),
    ("THE 4-WEEK BOOTCAMP — TLAMACHIYOTL PISCINE",           "h.nv2wdl7eaw5",      False),
    ("FINANCE MODULE 6 — CRYPTO REMITTANCE RAILS",           "h.6sooeo2blwjs",     False),
    ("LANGUAGES — SPANISH: POSITIONING & COMMUNICATION",     "h.3sxup0th22jo",     False),
    ("STUDENT DIGITAL INCOME PIPELINE",                      "h.pi90k76hm85u",     False),

    ("ACADEMY DESIGN & OPERATIONS",                          None,                 True),
    ("VENTURE BUILDER — SEPARATE ENTITY",                    "h.z888fvmy5pz8",     False),
    ("TALENT RECRUITMENT PIPELINE",                          "h.16wsos5az3y4",     False),
    ("FROM MOZAMBIQUE TO HUASTECA — AZLERA LESSONS",         "h.jqcfqh92sihi",     False),
    ("EARLY CHILDHOOD ANCHOR — TALKLET CONNECTION",          "h.ce6cvo176m7",      False),
    ("NUTRITION AND COGNITIVE DEVELOPMENT",                  "h.2cjzfqk24oqp",     False),

    ("APPENDICES",                                           None,                 True),
    ("APPENDIX A — CROSSWALK: 2015 ESSAY → 2026 CURRICULUM","h.j86a4rvaxdro",     False),
    ("APPENDIX B — SUGGESTED NEXT STEPS (30/60/90 DAYS)",   "h.jk0mtafrl2jg",     False),
    ("APPENDIX C — PE FUND: LP CAPITAL LANDSCAPE",          "h.oe4lnjxs823a",     False),
    ("APPENDIX D — SPACE & REAL ESTATE RESEARCH",           "h.echd4ifi8cud",     False),
    ("APPENDIX E — REVENUE STREAMS & STUDENT INCOME",       "h.c3m96rhqwvf",      False),
    ("APPENDIX F — SITE COMPARISON: HUEJUTLA vs CHICONTEPEC","h.b9axv7eumr7i",    False),

    ("RESEARCH & EVIDENCE",                                  None,                 True),
    ("EVIDENCE BASE & RESEARCH NOTES",                       "h.d5v49em4jemy",     False),
    ("ACADEMIC REFERENCES (added 2026-10-01)",               "h.c0l8ynnvq8n3",     False),
    ("HGSE COURSE FOUNDATIONS — RESEARCH & FRAMEWORKS",      "h.e14n35mvrftq",     False),
]

# Build the TOC text block
toc_lines = []
for (text, hid, is_cat) in TOC:
    if is_cat:
        toc_lines.append(text)        # category label line
    else:
        toc_lines.append("  " + text) # indented entry
toc_text = "\n".join(toc_lines) + "\n"

print(f"TOC text: {len(toc_text)} chars, {len(toc_lines)} lines")

# ── Step 1: Delete old TOC entries [495, 1105) and insert new TOC ────────────
# Old TOC entries run from si=495 to just before PREFACE content at si=1105
# We delete [495, 1105) and insert new text at 495 in one batchUpdate
print("Step 1: Replace old TOC entries...")
service.documents().batchUpdate(
    documentId=DOC_ID,
    body={'requests': [
        {'deleteContentRange': {'range': {'startIndex': 495, 'endIndex': 1105}}},
        {'insertText': {'location': {'index': 495}, 'text': toc_text}},
    ]}
).execute()
print("  Replaced. Re-reading doc...")

# ── Step 2: Find new TOC paragraph positions and apply links + styles ─────────
doc2 = service.documents().get(documentId=DOC_ID).execute()
body2 = doc2.get('body', {}).get('content', [])

# Build a lookup: display_text_stripped → headingId
# We need to find each TOC paragraph (they're near the start of the doc, si < 2000)
link_map = {}
cat_set = set()
for (text, hid, is_cat) in TOC:
    if is_cat:
        cat_set.add(text)
    elif hid:
        key = text.strip()
        link_map[key] = hid

fmt_requests = []
found = 0

for elem in body2:
    if 'paragraph' not in elem:
        continue
    si = elem.get('startIndex', 0)
    ei = elem.get('endIndex', 0)
    if si > 2500:   # TOC is near the top; stop searching past it
        break

    text = ''.join(r.get('textRun',{}).get('content','') for r in elem['paragraph'].get('elements',[])).strip()
    if not text:
        continue

    # Category label → bold navy, no link
    if text in cat_set:
        fmt_requests.append({'updateTextStyle': {
            'range': {'startIndex': si, 'endIndex': ei - 1},
            'textStyle': {
                'bold': True,
                'foregroundColor': rgb(NAVY),
                'fontSize': {'magnitude': 9, 'unit': 'PT'},
            },
            'fields': 'bold,foregroundColor,fontSize'
        }})
        print(f"  CAT  si={si}: {text[:60]}")
        found += 1
        continue

    # Entry → look up headingId, add link + teal style
    stripped = text.lstrip()
    matched_hid = None
    for key, hid in link_map.items():
        if stripped.startswith(key[:30]) or key.startswith(stripped[:30]):
            matched_hid = hid
            break

    if matched_hid:
        fmt_requests.append({'updateTextStyle': {
            'range': {'startIndex': si, 'endIndex': ei - 1},
            'textStyle': {
                'link': {'url': f'#heading={matched_hid}'},
                'foregroundColor': rgb(TEAL),
                'fontSize': {'magnitude': 9, 'unit': 'PT'},
                'bold': False,
            },
            'fields': 'link,foregroundColor,fontSize,bold'
        }})
        print(f"  LINK si={si}: {text[:60]} → {matched_hid}")
        found += 1

print(f"\nFound {found}/{len(TOC)} entries. Applying {len(fmt_requests)} format requests...")
for i in range(0, len(fmt_requests), 50):
    service.documents().batchUpdate(
        documentId=DOC_ID, body={'requests': fmt_requests[i:i+50]}
    ).execute()
    print(f"  {min(i+50, len(fmt_requests))}/{len(fmt_requests)}")

print("Done.")
