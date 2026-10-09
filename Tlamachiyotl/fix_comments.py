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
ORANGE = {'red': 0.85, 'green': 0.33, 'blue': 0.00}
def rgb(c): return {'color': {'rgbColor': c}}

# ── All insertions — DESCENDING INDEX ORDER (safe single batchUpdate) ────────

insertions = []  # list of (target_index, text)

# ── #1 — Fix misplaced IAF sentence (si=59621, currently formatted as HEADING)
# Add a contextual label before the paragraph text so it's clear where it belongs.
# We'll insert a small label before it at 59621 to reframe it.
IAF_LABEL = "[Research Funding Note — cross-reference with FUNDING STRATEGY > Research Track]\n"
insertions.append((59621, IAF_LABEL))

# ── #2 — Co-partner sourcing (after "Who is the person on the ground", ei=38287)
COPARTNER = (
    "\nCo-partner and ground-person sourcing — platforms and approaches\n"
    "Finding the right ground person is the single most important hire. Sourcing paths:\n"
    "  Ashoka México (ashoka.org/mexico): Network of social entrepreneurs already embedded in communities. "
    "Best source for a Mexican co-founder with field credibility.\n"
    "  Sistema B México (sistemab.org/mexico): B Corp entrepreneur community. "
    "Mission-aligned, vetted, Mexico-based founders.\n"
    "  Endeavor México (endeavor.org.mx): High-growth entrepreneur network. "
    "More commercial profile but strong execution track record.\n"
    "  LinkedIn — search: 'Huasteca', 'Veracruz', 'Hidalgo', 'educación indígena', 'desarrollo comunitario'. "
    "Filter for: returnee diaspora, UAEH/UV alumni, Enseña por México alumni.\n"
    "  Enseña por México alumni network: Former corps members are high-quality ground-person candidates — "
    "they have field experience in exactly this geography and population.\n"
    "  UAEH (Universidad Autónoma del Estado de Hidalgo) and UV (Universidad Veracruzana): "
    "Social work, education, and development faculty often know motivated local leaders.\n"
    "  AZLera network: The founders' own 15-year network from Mozambique contains people with "
    "exactly the profile needed — mission-driven, experienced in resource-constrained field operations.\n"
)
insertions.append((38287, COPARTNER))

# ── #3 — Spanish literacy baseline clarification (after ei=38147)
SPAN_CLARITY = (
    "\nWhat this question actually asks: Students in Nahuatl-speaking Huasteca communities have typically "
    "attended Spanish-medium public schools (SEP). They arrive with Spanish literacy but often with "
    "limited formal Nahuatl literacy (oral competence yes, written and academic no). This baseline "
    "determines how quickly the program can go Nahuatl-primary in academic instruction. "
    "A student who reads Spanish at grade level can transition to Nahuatl-medium instruction faster "
    "than one who struggles in both languages. "
    "DECISION: Administer a simple oral Nahuatl proficiency assessment at enrollment (conducted by a "
    "community elder or Nahuatl-proficient staff). No minimum Spanish-literacy requirement for admission — "
    "the academy is not a Spanish-medium institution. Use the assessment to calibrate starting group.\n"
)
insertions.append((38147, SPAN_CLARITY))

# ── #4 — Hybrid recruitment decision (after "The academy's answer..." ei=38034)
RECRUIT_DECISION = (
    "\nDECISION: Hybrid model. Year 1 cohort recruited through direct school visits — "
    "telebachilleratos and secundarias in Huejutla and Chicontepec — following the AZLera/Mozambique "
    "school-recruitment approach. Show up, explain the program, identify interested students. "
    "Community-open applications from Year 2 once word-of-mouth reputation is established. "
    "Merit criteria should be lightweight: motivation and community commitment, not academic grades.\n"
)
insertions.append((38034, RECRUIT_DECISION))

# ── #5 — Gender target decision (after gender paragraph ei=37770)
GENDER_DECISION = (
    "\nDECISION: Co-ed from Day 1. Both boys and girls. "
    "Explicit girl-recruitment quota: minimum 40% female in the first cohort and every subsequent cohort. "
    "Dedicated women-in-tech mentorship track and Lean In circles embedded from Year 1. "
    "Reference: the 2015 essay (pp. 25-27) argued forcefully for women as a priority population; "
    "the Clontarf Foundation boys-only model is not the template here.\n"
)
insertions.append((37770, GENDER_DECISION))

# ── #6 — Starlink connectivity research (after internet reliability mitigation ei=37497)
STARLINK = (
    "\nConnectivity stack — research findings (knowledge base August 2025; verify current MXN prices):\n"
    "Starlink in Mexico: Available nationwide including Hidalgo and Veracruz. "
    "Cost: ~MXN 799–1,399/month (residential); hardware one-time ~MXN 5,499–7,499. "
    "Speeds: 50–200 Mbps down; latency 25–60 ms. Mountain terrain requires clear southern sky — "
    "elevated roof mount resolves most obstruction issues in Sierra Huasteca.\n"
    "CFE Telecomunicaciones / Internet para Todos: Partial coverage in Huejutla cabecera by 2024; "
    "Chicontepec had limited or no confirmed deployment. Shared bandwidth (10–25 Mbps per hotspot). "
    "Program continuity post-2024 is uncertain — do not rely on as primary.\n"
    "Cellular: Telcel has best rural Huasteca coverage (700 MHz band). Huejutla: solid 4G. "
    "Chicontepec cabecera: 4G/3G reported; outlying rancherías: 2G or no signal. "
    "AT&T: decent in Huejutla, sparse in Chicontepec. Movistar: urban only, not recommended.\n"
    "Recommended stack:\n"
    "  Huejutla main site: Local fiber ISP (~MXN 500–900/month) + Starlink as backup (~MXN 1,399/month)\n"
    "  Mobile unit (Chicontepec days): Telcel 60 GB hotspot (~MXN 500–600/month)\n"
    "  Total estimated monthly connectivity cost: MXN 1,100–1,700 without Starlink Roam; "
    "~MXN 3,000–3,500 with Starlink Roam (portable) on the van\n"
    "  Verify current pricing: starlink.com/mx and telcel.com before finalising budget.\n"
)
insertions.append((37497, STARLINK))

# ── #7 — Safeguarding / after-school model decision (after risk paragraph ei=37241)
SAFEGUARD_FIX = (
    "\nDECISION: No residential component in Phase 0–1. The program runs as an after-school / "
    "afternoon program only (e.g. 2–6pm daily). Students go home each evening. "
    "This framing is intentional: an after-school program avoids the regulatory and political "
    "complexity of operating as a formal educational institution in Phase 0–1. "
    "It also lowers the safeguarding burden significantly. Residential option revisited in Year 3+ "
    "only if demand from distant communities (e.g. students travelling from remote Chicontepec "
    "rancherías) clearly justifies it and funding supports it.\n"
    "Mitigation: Adopt Clontarf Foundation safeguarding policy as template from Day 1 "
    "(available on their website). Parental consent forms, two-adult rule, clear reporting chain "
    "even in an after-school context.\n"
)
insertions.append((37241, SAFEGUARD_FIX))

# ── #8 — Scope sprawl clarification (after risk paragraph ei=36995)
SCOPE_NOTE = (
    "\nNote: Broad research at the planning stage is intentional and correct. "
    "The brainstorm document is designed to be comprehensive — it maps the full possibility space. "
    "Scope discipline applies at execution, not at planning. "
    "The execution plan (Phase 0–1) is deliberately narrow: one cohort, two sports, "
    "two STEM concentrations, Nahuatl immersion. Earn the right to add each subsequent layer.\n"
)
insertions.append((36995, SCOPE_NOTE))

# ── #11 — Teacher pipeline AZLera model (after teacher risk paragraph ei=35666)
TEACHER_AZLERA = (
    "\nMitigation — AZLera self-financing volunteer model: "
    "International volunteers who contribute $150–300/month toward their own lodging and materials "
    "while providing skills. AZLera received 1–2 unsolicited inquiries per week without active "
    "recruiting. Structure this formally: define a 2–3 month rotation, set required skills "
    "(Nahuatl interest a plus, not required), post on Idealist, AIESEC, UN Volunteers Online, "
    "and GoOverseas. A small monthly contribution from volunteers directly offsets program costs "
    "while creating a renewable international talent pipeline — exactly as AZLera operated.\n"
)
insertions.append((35666, TEACHER_AZLERA))

# ── #12 — Tech company philanthropies links (after heading ei=30467)
TECH_LINKS = (
    "\nDirect application / program links (verify currency — URLs correct as of 2025):\n"
    "  Google.org grants: google.org/our-work/\n"
    "  Microsoft Philanthropies / TEALS: microsoft.com/en-us/corporate-responsibility/philanthropies "
    "and aka.ms/teals\n"
    "  Meta — Indigenous Language Initiative: about.meta.com/actions/connectivity/ and "
    "research.facebook.com/downloads/\n"
    "  Amazon Future Engineer: amazonfutureengineer.com\n"
    "  Apple Community Education Initiative: apple.com/education/k12/\n"
    "  Salesforce.org grants: salesforce.org/grants/\n"
    "  Cisco Networking Academy: netacad.com (free curriculum + teacher training)\n"
    "  Oracle Education Foundation: oracle.com/corporate/citizenship/education/\n"
    "  Dell Technologies Social Impact / hardware donations: delltechnologies.com/en-us/social-impact/\n"
)
insertions.append((30467, TECH_LINKS))

print(f"Prepared {len(insertions)} insertions")
for idx, txt in sorted(insertions, key=lambda x: -x[0]):
    print(f"  → insert at {idx}: '{txt[:60].strip()}...'")

# ── Execute in DESCENDING INDEX ORDER in one batchUpdate ────────────────────
requests = []
for target_idx, text in sorted(insertions, key=lambda x: -x[0]):
    requests.append({'insertText': {
        'location': {'index': target_idx},
        'text': text
    }})

service.documents().batchUpdate(
    documentId=DOC_ID, body={'requests': requests}
).execute()
print("\nAll insertions applied.")

# ── Re-read doc to format new headings ──────────────────────────────────────
doc2 = service.documents().get(documentId=DOC_ID).execute()
body2 = doc2.get('body', {}).get('content', [])

new_headings = {
    'Co-partner and ground-person sourcing — platforms and approaches': ('HEADING_3', TEAL),
    'What this question actually asks:': ('HEADING_3', TEAL),
    'DECISION: Hybrid model.': ('HEADING_3', NAVY),
    'DECISION: Co-ed from Day 1.': ('HEADING_3', NAVY),
    'Connectivity stack — research findings': ('HEADING_3', TEAL),
    'Recommended stack:': ('HEADING_3', TEAL),
    'DECISION: No residential component in Phase 0–1.': ('HEADING_3', NAVY),
    'Note: Broad research at the planning stage': ('HEADING_3', TEAL),
    'Mitigation — AZLera self-financing volunteer model:': ('HEADING_3', TEAL),
    'Direct application / program links': ('HEADING_3', TEAL),
    '[Research Funding Note': ('HEADING_3', ORANGE),
}

# Also bold DECISION labels
DECISION_LABELS = ['DECISION:', 'Mitigation —', 'Note:', 'Co-partner and', 'Connectivity stack',
                   'Recommended stack', 'Direct application', 'What this question']

fmt_requests = []
for elem in body2:
    if 'paragraph' not in elem: continue
    si = elem.get('startIndex', 0)
    ei = elem.get('endIndex', 0)
    p = elem['paragraph']
    text = ''.join(r.get('textRun',{}).get('content','') for r in p.get('elements',[])).strip()

    for key, (style, col) in new_headings.items():
        if text.startswith(key[:30]):
            fmt_requests.append({'updateParagraphStyle': {
                'range': {'startIndex': si, 'endIndex': ei},
                'paragraphStyle': {'namedStyleType': style},
                'fields': 'namedStyleType'
            }})
            fmt_requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': ei - 1},
                'textStyle': {
                    'foregroundColor': rgb(col),
                    'bold': True,
                    'fontSize': {'magnitude': 11, 'unit': 'PT'},
                },
                'fields': 'foregroundColor,bold,fontSize'
            }})
            print(f"  Formatted heading: '{text[:60]}'")
            break

    # Bold DECISION: labels within body text
    for label in DECISION_LABELS:
        if text.startswith(label):
            end = min(si + len(label) + 1, ei - 1)
            fmt_requests.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': end},
                'textStyle': {'bold': True, 'foregroundColor': rgb(NAVY)},
                'fields': 'bold,foregroundColor'
            }})
            break

# Also fix the IAF paragraph style (si range: find it by content)
for elem in body2:
    if 'paragraph' not in elem: continue
    si = elem.get('startIndex', 0)
    ei = elem.get('endIndex', 0)
    p = elem['paragraph']
    style = p.get('paragraphStyle', {}).get('namedStyleType', '')
    text = ''.join(r.get('textRun',{}).get('content','') for r in p.get('elements',[])).strip()
    if 'These gaps are funders' in text and style == 'HEADING_3':
        # Change to NORMAL_TEXT
        fmt_requests.append({'updateParagraphStyle': {
            'range': {'startIndex': si, 'endIndex': ei},
            'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'},
            'fields': 'namedStyleType'
        }})
        fmt_requests.append({'updateTextStyle': {
            'range': {'startIndex': si, 'endIndex': ei - 1},
            'textStyle': {
                'foregroundColor': rgb({'red': 0.3, 'green': 0.3, 'blue': 0.3}),
                'bold': False,
                'italic': True,
            },
            'fields': 'foregroundColor,bold,italic'
        }})
        print(f"  Fixed IAF paragraph style at si={si}")

print(f"\nApplying {len(fmt_requests)} formatting requests...")
for i in range(0, len(fmt_requests), 50):
    service.documents().batchUpdate(
        documentId=DOC_ID, body={'requests': fmt_requests[i:i+50]}
    ).execute()
print("Done.")
