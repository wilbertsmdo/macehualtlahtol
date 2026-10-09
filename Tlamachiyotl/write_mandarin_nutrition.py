import sys
sys.path.insert(0, '/data/data/com.termux/files/usr/lib/python3.13/site-packages')
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

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

# ── Get current doc end index ────────────────────────────────────────────────
doc = service.documents().get(documentId=DOC_ID).execute()
body_content = doc.get('body', {}).get('content', [])
end_index = body_content[-1].get('endIndex', 1) - 1
print(f"Current doc end index: {end_index}")

# ── Build the two new sections ───────────────────────────────────────────────
MANDARIN_SECTION = """\

MANDARIN FOR LATAM YOUTH — RESEARCH FINDINGS
Why Mandarin at a Nahuatl academy?

The 2015 essay proposed Mandarin as the fourth language track (after Nahuatl, Spanish, English). This is a differentiating signal: no other indigenous academy in Mexico offers it. The case is economic and cultural — China is Mexico's second-largest trading partner; Mandarin fluency will be a rare asset for Huasteca youth entering the global economy.

Confucius Institutes in the academy's catchment area
The two closest Confucius Institutes to the Huasteca are:
  UV Xalapa — Universidad Veracruzana, Xalapa, Veracruz (~3h from Huejutla). Institute code: CI-UV. Contact: confucio@uv.mx. Established 2010, HSK prep courses, teacher training for secondary schools.
  UAEH Pachuca — Universidad Autónoma del Estado de Hidalgo, Pachuca (~2h from Huejutla). Institute code: CI-UAEH. Contact: institutodeconfucio@uaeh.edu.mx. HSK preparation and cultural programming.

Strategic entry point: Taiwan TECRO
The Taiwan Economic and Cultural Representative Office (TECRO) in Mexico City offers the Hua-Guang Scholarship and Taiwan Scholarship for Mexican students. More actionable for a small academy than a PRC government CI partnership: TECRO is smaller, faster-moving, and Taiwan-based Mandarin pedagogy (TOCFL exams) is politically uncomplicated in Mexico. Contact: Mexico City TECRO — tecro.org.tw/mx

Free platform for student self-study
HelloChinese (iOS/Android) — free, gamified, Mandarin course from zero. Best free standalone tool for student self-study outside class hours. Supplement with HSK mock exams from CI-UV or CI-UAEH.

DECISION: Mandarin track — implementation path
Phase 0–1: Partner with CI-UV or CI-UAEH for one weekly Mandarin session — their teachers visit or teach via video. No dedicated hire needed in Year 1.
Phase 2+: Add a Mandarin teaching fellow (AIESEC sourcing from China, Taiwan, or Singapore). Target outcome: HSK 2 (basic conversational) by Year 3 for motivated students.
Contact priority: CI-UAEH (Pachuca) first — shorter distance, same state (Hidalgo), easier logistics for a visiting teacher arrangement.

"""

NUTRITION_SECTION = """\

NUTRITION AND COGNITIVE DEVELOPMENT — RESEARCH FINDINGS
The evidence base

Iron deficiency is the single most prevalent nutritional cause of impaired cognition in school-age children in rural Mexico, particularly in indigenous communities with high rates of anaemia. Evidence summary:
  WHO / UNICEF: Iron-deficiency anaemia affects ~30% of school-age children in rural Mexican states including Hidalgo and Veracruz. Effect: reduced attention, working memory, and processing speed — all directly relevant to STEM and language learning.
  Lozoff et al. (2006, Pediatrics): Children with early iron deficiency showed persistent cognitive and learning disadvantages into adolescence even after treatment — early intervention is critical.
  Grantham-McGregor & Ani (2001, J. Nutrition): Weekly iron supplementation reduces anaemia prevalence by 50–70% in 10–12 weeks. Effect size on cognitive tasks: 0.3–0.6 SD improvement on attention and learning measures.
  Deworming (Taylor-Robinson et al., Cochrane 2019): Effect on school performance in high-burden contexts is positive but smaller than previously estimated. Still included in the package as cost is near zero and risk minimal.

Practical intervention protocol — HemoCue model
Screen at enrollment: HemoCue Hb 201+ fingerprick haemoglobin test. Cost: ~MXN 50/student (~$3 USD). Takes 30 seconds, no lab needed.
Weekly iron supplementation (for screen-positive and as universal prevention): Ferrous sulfate 200 mg weekly (proven equivalent to daily dosing for prevention; lower GI side effects). Cost: ~MXN 35/student/year (~$2 USD/year).
Deworming: Single-dose albendazole 400 mg twice per year. Cost: ~MXN 35/student/year (~$2 USD/year).
Daily snack: One nutritious mid-session snack (e.g., bean/egg protein + fruit). Estimated cost: ~MXN 1,400/student/year (~$80 USD/year at MXN 6/snack × 230 days).

Total cost per student per year: ~MXN 1,500 (~$84–90 USD)

This is one of the highest-ROI investments the academy can make. The snack also functions as a family incentive — students who attend receive a meal that families might not otherwise provide. Mirrors the school meal logic used in AZLera and in CONAFE's Telesecundaria model.

DECISION: Include nutrition package from Day 1 of Phase 1
Budget line: MXN 1,500/student/year in operating budget.
Procurement: Weekly iron tablets via local farmacia (Farmacias del Ahorro / Similares); albendazole via IMSS-Bienestar (donated or at cost to registered community programs); snacks via a local supplier or volunteer-cooked.
Tracking: HemoCue test at enrollment and at 3-month and 6-month marks. Record haemoglobin alongside academic performance data — this creates a genuine internal evidence base for the research partnership track.

"""

# Combine both sections into one insertion
NEW_TEXT = MANDARIN_SECTION + NUTRITION_SECTION

# ── Insert at end of doc ─────────────────────────────────────────────────────
insert_requests = [
    {'insertText': {
        'location': {'index': end_index},
        'text': NEW_TEXT
    }}
]

service.documents().batchUpdate(
    documentId=DOC_ID, body={'requests': insert_requests}
).execute()
print(f"Inserted {len(NEW_TEXT)} chars at index {end_index}")

# ── Re-read doc to format new headings ──────────────────────────────────────
doc2 = service.documents().get(documentId=DOC_ID).execute()
body2 = doc2.get('body', {}).get('content', [])

# Headings to format: (prefix_to_match, style, colour)
new_headings = {
    'MANDARIN FOR LATAM YOUTH': ('HEADING_2', NAVY),
    'Why Mandarin at a Nahuatl academy?': ('HEADING_3', TEAL),
    'Confucius Institutes in the academy': ('HEADING_3', TEAL),
    'Strategic entry point: Taiwan TECRO': ('HEADING_3', TEAL),
    'Free platform for student self-study': ('HEADING_3', TEAL),
    'DECISION: Mandarin track': ('HEADING_3', NAVY),
    'NUTRITION AND COGNITIVE DEVELOPMENT': ('HEADING_2', NAVY),
    'The evidence base': ('HEADING_3', TEAL),
    'Practical intervention protocol': ('HEADING_3', TEAL),
    'Total cost per student per year:': ('HEADING_3', TEAL),
    'DECISION: Include nutrition package': ('HEADING_3', NAVY),
}

fmt_requests = []
for elem in body2:
    if 'paragraph' not in elem:
        continue
    si = elem.get('startIndex', 0)
    ei = elem.get('endIndex', 0)
    p = elem['paragraph']
    text = ''.join(r.get('textRun', {}).get('content', '') for r in p.get('elements', [])).strip()

    for key, (style, col) in new_headings.items():
        if text.startswith(key[:35]):
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
                    'fontSize': {'magnitude': 13 if style == 'HEADING_2' else 11, 'unit': 'PT'},
                },
                'fields': 'foregroundColor,bold,fontSize'
            }})
            print(f"  Formatted: '{text[:60]}'")
            break

print(f"\nApplying {len(fmt_requests)} formatting requests...")
for i in range(0, len(fmt_requests), 50):
    service.documents().batchUpdate(
        documentId=DOC_ID, body={'requests': fmt_requests[i:i+50]}
    ).execute()
print("Done.")
