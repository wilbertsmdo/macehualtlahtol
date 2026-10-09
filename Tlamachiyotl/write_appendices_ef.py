import sys, time
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

NAVY  = {'red': 0.11, 'green': 0.20, 'blue': 0.42}
TEAL  = {'red': 0.00, 'green': 0.47, 'blue': 0.47}
ORANGE= {'red': 0.85, 'green': 0.33, 'blue': 0.00}
GRAY  = {'red': 0.42, 'green': 0.42, 'blue': 0.42}
def rgb(c): return {'color': {'rgbColor': c}}

NEW_CONTENT = """\

APPENDIX E — REVENUE STREAMS & STUDENT INCOME PIPELINE
Revenue analysis: student outputs ranked by Phase 0–1 income potential

Each output type is rated across four dimensions: income mechanism, realistic Phase 0–1 earnings, timeline to first payment, and connectivity requirement.

Tier 1 — Immediate revenue (Day 1 viable)

Nahuatl voice corpus recordings
  Income mechanism: Direct data contracts with AI labs (Meta AI, Google, Appen, Scale AI, iMerit) via the academy-registered school cooperative. The school holds the platform account and B2B contract; students are the producers.
  Phase 0–1 income: $50–150/student/month under a standing contract; $250–2,500 per corpus batch sale.
  Timeline to first payment: 3–6 months (time to build corpus sample + negotiate first contract).
  Connectivity requirement: Offline-capable. Students record locally; data syncs during Huejutla connectivity windows.
  Key insight: Nahuatl Huasteco appears on UNESCO and AI4Bharat priority low-resource language lists. Scarcity = pricing power. This is the ONLY reliable Day 1 income channel.

Translated texts (Nahuatl ↔ Spanish)
  Income mechanism: INALI (Instituto Nacional de Lenguas Indígenas), SIL International, government agencies, health/education NGOs pay for quality Nahuatl translations of legal, health, and educational materials.
  Phase 0–1 income: MXN 0.50–2.00/word-equivalent; MXN 500–3,000/document depending on length and technical content.
  Timeline to first payment: 2–4 months.
  Connectivity requirement: Minimal — work done offline, submitted via email.
  Note: Requires students with higher Nahuatl literacy (Tier 2 cohort skill level). Start with simpler health education materials.

Tier 2 — Medium-term revenue (Year 1–2)

Digital art and Nahuatl-themed content
  Income mechanism: Etsy, Redbubble, local cultural festivals, print-on-demand. Nahuatl-themed design has cultural differentiation that competes on identity, not price.
  Phase 0–1 income: Variable. MXN 200–2,000/month for active sellers after building a catalogue.
  Timeline: 6–12 months.
  Connectivity requirement: Moderate. Designs created offline; uploaded in batch.

YouTube / podcast (Macehualli Podcast / Nahuatl channel)
  Income mechanism: YouTube Partner Program (requires 1,000 subscribers + 4,000 watch hours), sponsorship from cultural organisations, Patreon.
  Phase 0–1 income: Near zero until subscriber threshold. Long-term: MXN 2,000–10,000/month for a 10K+ channel.
  Timeline: 12–24 months to first YouTube revenue.
  Note: Build audience as a grant-credibility and community-engagement tool; treat income as Year 2+ bonus.

Tier 3 — Long-term / project-based (Year 2+)

Coded apps and community software
  Income mechanism: Per-contract with a municipality, health clinic, ejido, or NGO. Requires a specific paying client identified before development starts.
  Phase 0–1 income: MXN 5,000–30,000 per project if client identified.
  Timeline: 12–18 months.
  Note: Cold-start freelance is too slow. Only viable with a pre-identified client from Day 1.

Zero-income outputs (portfolio and grant value only)
  Mozilla Common Voice recordings: Mozilla Common Voice does NOT pay contributors. It is a volunteer-donation platform. However, the Nahuatl corpus built there becomes evidence for grant applications and is re-sellable separately via data contracts.
  Nahuatl Wikipedia / Huiquipedia articles: Wikimedia Foundation does not pay per-article. WMF affiliate grants (via Wikimedia México) fund equipment and workshops, not stipends.
  Both outputs are HIGH grant-credibility builders. Budget them as curriculum activities, not income.

APPENDIX F — SITE COMPARISON: HUEJUTLA vs CHICONTEPEC
Detailed comparison to inform Phase 0–1 site decision and Phase 2 expansion

Population and indigenous density

  Huejutla de Reyes, Hidalgo (proposed Phase 0–1 HQ)
    Total municipal population: 122,905 (INEGI 2020)
    Nahuatl speakers: ~62,000 (~51% of total)
    Cabecera (municipal seat): ~38,000 inhabitants
    Localities: 200+ rural communities, most under 2,500 people
    CONEVAL marginalization: High

  Chicontepec de Tejeda, Veracruz (proposed Phase 2 satellite)
    Total municipal population: 50,129 (INEGI 2020)
    Nahuatl speakers: ~35,000 (~70% of total — highest indigenous density of the two)
    Cabecera: ~6,500 inhabitants (13% of municipal total)
    Localities: 320–350 dispersed communities across Sierra terrain
    CONEVAL marginalization: Very High (one level above Huejutla)

Infrastructure comparison

  Factor                        Huejutla             Chicontepec
  ─────────────────────────────────────────────────────────────────
  Internet (household)          25–30%               10–15%
  Medical                       Hospital-grade        Limited clinic
  Higher education              UAEH extension        None
  Banking                       Full branch network   ATM only
  Highway access                Yes (MEX-85D)         No — Sierra roads
  Fiber internet                Available             Not available
  Monthly rental (200 m²)       MXN 14,000–22,000    MXN 6,000–14,000
  Travel from Huejutla          —                    80 km / 2.5–4 hours

Why Chicontepec matters despite the logistics difficulty
  Higher Nahuatl-speaker density (70% vs 51%) makes it the more powerful language-revitalization demonstration site. The Chicontepec Nahua community is also more cohesive — smaller cabecera, tighter social fabric.
  Chicontepec has stronger research partnership potential: the higher indigenous density and Very High marginalization index make it a more compelling case study for UVI / HGSE / IAF research funding.
  The geographical dispersion (320+ localities) is a constraint for a fixed program but is exactly the problem that a remote + mobile outreach model addresses in Phase 2.

Phase recommendation
  Phase 0–1: Huejutla only. Infrastructure, connectivity, medical support, and founder part-time presence all point to Huejutla as the only viable Phase 0–1 HQ.
  Phase 2: Periodic Chicontepec outreach — founder or fellow travels 1–2 days/week, rents classroom space at the local telebachillerato. CESDER (Puebla Sierra Norte) is the operational precedent for this mobile extension model.
  Phase 3: Evaluate a fixed Chicontepec satellite site if demand justifies it and funding supports it. The $9–17K/year dual-site overhead (documented in Site Analysis section) is the budget threshold to clear.

ONLINE CURRICULA & BOOTCAMP RESOURCES
Open-source curricula for the STEM track

The following curricula are freely available, offline-exportable, and have been used in low-resource contexts. The academy's value-add is Nahuatl-language contextualization of all projects and examples.

Core curricula

CS50x — Harvard / edX
  URL: cs50.harvard.edu/x/
  Content: Scratch → C → Python → web development. Complete offline materials. Best overall base for a 4-week bootcamp.
  Used by: Schools on 6 continents; routinely condensed to 4-week intensive formats.

freeCodeCamp
  URL: freecodecamp.org
  Content: 300+ hours across web development, JavaScript, Python, data visualization. Modular and fully offline-exportable.
  Best for: Web / JS track (Concentration 1).

The Odin Project
  URL: theodinproject.com
  Content: Full-stack web development. Browser-based, free, project-driven.
  Best for: Students who complete freeCodeCamp basics and want to go deeper.

Laboratoria Curriculum
  URL: github.com/Laboratoria/curriculum
  Content: LatAm-specific, Spanish-language, designed for low-income women with no prior tech background. Closest demographic match to the Tlamachiyotl cohort.
  Best for: Template for adapting global curricula to Huasteca context.

Kaggle Learn
  URL: kaggle.com/learn
  Content: Data science, machine learning, Python. Free and fully online.
  Best for: Tier 2 AI data labeling track (connects directly to the voice corpus income pipeline).

Hardware / electronics

CONAFE Robótica Educativa
  URL: conafe.gob.mx (search "robótica educativa" or "STEAM")
  Content: CONAFE (Consejo Nacional de Fomento Educativo) runs Arduino-based robotics kits and curriculum for rural telesecundaria level. The program has been piloted in Hidalgo and Veracruz — directly relevant to the Tlamachiyotl catchment area.
  Note: CONAFE is a government program but the curriculum materials are freely available. No government enrollment required to use the pedagogy.

CONALEP (Colegio de Educación Profesional Técnica)
  URL: conalep.edu.mx
  Content: CONALEP offers recognized technical certificates in electronics, computing, and industrial maintenance. Tlamachiyotl students who complete the electronics/robotics concentration could pursue a CONALEP certificate as a dual-enrollment pathway — giving them a nationally recognized credential alongside the academy's own certification.
  Contact: CONALEP Huejutla or CONALEP Poza Rica (nearest to Chicontepec).

THE 4-WEEK BOOTCAMP — TLAMACHIYOTL PISCINE
Curriculum outline for the opening selection bootcamp

Based on École 42's La Piscine model: no prior requirement, peer evaluation only, project-based progression, no lectures. Adapted for Nahuatl-medium delivery.

Week 1 — Visual coding + Nahuatl digital vocabulary
  Day 1–2: Scratch (CS50 Week 0) — build an animated story in Nahuatl using visual code blocks. No typing required. Immediate visible result.
  Day 3–4: Introduce the concept of variables, loops, and conditionals through Scratch puzzles.
  Day 5: Peer showcase — present your Scratch project in Nahuatl to the group.
  Resources: scratch.mit.edu (offline-capable via Scratch Desktop app).

Week 2 — HTML and CSS: build a page in Nahuatl
  Day 1–2: HTML structure — headings, paragraphs, images, links. Students build a personal introduction page in Nahuatl.
  Day 3–4: CSS styling — colours, fonts, layout. Apply Nahuatl cultural aesthetics (Huasteca colours, glyphs as design elements).
  Day 5: Peer review — swap pages with a partner; give structured feedback using a rubric.
  Resources: freeCodeCamp Responsive Web Design (offline PDF export) + VS Code (offline IDE).

Week 3 — Python basics + Nahuatl word app
  Day 1–2: Python syntax — variables, input/output, conditionals (if/else). CS50 Python week.
  Day 3–4: Build a simple Nahuatl word quiz app: program reads a Nahuatl word, user types the Spanish meaning, program confirms. Combines coding with language reinforcement.
  Day 5: Demo day — run each other's apps, note bugs, fix one bug in a partner's code.
  Resources: freeCodeCamp Scientific Computing with Python (offline) + Python 3 (pre-installed on school laptops).

Week 4 — Portfolio commit and peer presentations
  Day 1–2: Students choose their best project from Weeks 1–3 and polish it. Write a README in Nahuatl and English explaining what it does.
  Day 3: GitHub commit — every student pushes their project to a public GitHub repository. This is their first professional portfolio entry.
  Day 4: Public presentations — each student presents their project in 5 minutes (Nahuatl). Family members and community invited.
  Day 5: Cohort decision — which students continue to the full program. Criteria: engagement, peer feedback scores, attendance. NOT academic grade.
  Resources: GitHub (free) + GitHub Pages for hosting HTML projects.

FINANCE MODULE 6 — CRYPTO REMITTANCE RAILS
Research findings for cross-border finance and crypto section

Context: Huasteca families already receive remittances from Mexican migrants in the US — this population is already using informal and formal money-transfer systems. Adding crypto literacy to Module 6 prepares students to participate in and eventually service the fastest-growing segment of Mexican fintech.

Current best platforms for Mexico (as of 2025)

Bitso
  URL: bitso.com
  Status: CNBV-registered (legally compliant in Mexico). Processes $1B+/month in US-MXN remittances via crypto rails.
  How it works: Sender in US buys USD/USDC via Bitso Business API; recipient in Mexico receives MXN via SPEI in minutes. Lower fees than Western Union (typically 1–2% vs 5–7%).
  Class exercise potential: live demo of a $10 transfer from a US wallet to a Mexican account, processed in class.

MoneyGram + Stellar (USDC)
  URL: moneygram.com + stellar.org
  Status: MoneyGram has physical cash-out agents in rural Mexico including Huasteca municipalities. Stellar is the underlying USDC settlement rail.
  Key advantage: No smartphone required at the receiving end — recipient walks to a MoneyGram agent point (often a farmacia or tienda de conveniencia) and collects pesos in cash.
  Best fit for: Huasteca families where the recipient has no smartphone or bank account.

Strike
  URL: strike.me
  Status: Uses Bitcoin Lightning Network for near-zero-fee US→Mexico transfers settled in pesos.
  Limitation: Requires a smartphone on the US sender side. Less relevant for rural recipients but very relevant for older students who may work in the US.

Regulation note
  Mexico Fintech Law (Ley Fintech, 2018) requires ITF (Institución de Tecnología Financiera) registration for any entity offering crypto custody or exchange services to the public.
  A school educational pilot routing a small transfer through Bitso API or MoneyGram as a documented class exercise — without the academy holding crypto custody — almost certainly falls outside ITF scope.
  Any future community remittance cooperative or stablecoin project (Phase 4+) would require legal structuring with a Mexican fintech lawyer. Not a Phase 0–1 decision.

Module 6 class design
  Sessions 1–2: How remittances work today (Western Union, Oxxo Pay, informal). What does each $100 sent cost in fees?
  Sessions 3–4: Crypto rails — what is USDC, how does Bitso work, what does MoneyGram+Stellar look like end-to-end.
  Session 5: Live demonstration — one $10 transfer processed in class, documented step-by-step.
  Capstone essay: Write a one-page proposal in Nahuatl describing how your family could save on remittance fees over one year using Bitso vs Western Union.

LANGUAGES — SPANISH: POSITIONING & PARENT COMMUNICATION
How to address the "what about Spanish?" objection

The objection: "Students will fall behind in Spanish — the dominant language of Mexican commerce, government, and higher education."

The academy's position (three points)
  1. Spanish is preserved, not removed. Students arrive from SEP schools with Spanish proficiency. The academy preserves their current level; it simply does not invest further in developing it. No regression.
  2. English, not Spanish, is the international language investment. Higher cross-border mobility return, higher wage premium for graduates who enter tech, finance, or global NGO careers.
  3. Nahuatl + English + Mandarin is the differentiation. The combination makes graduates rare in the global workforce — the first such multilingual profile in most tech company, UN agency, or cross-border-finance hiring pipelines. Spanish fluency is taken for granted in Mexico and adds no marginal employment premium.

Why this is a strength, not a flaw
  The concern that Nahuatl-medium instruction weakens Spanish is exactly what SEP's own intercultural bilingual education research has failed to resolve. Tlamachiyotl's position — Nahuatl as the full medium of academic instruction — is grounded in the UNESCO / Cummins / RTI International evidence: children taught in their mother tongue outperform on all academic measures including second-language acquisition over time.
  Students who are cognitively stronger (from Nahuatl-medium STEM and finance instruction) will catch up and exceed their Spanish-medium peers in Spanish proficiency as well, because the underlying cognitive capacity transfers across languages. This is the Cummins Threshold Hypothesis: develop one language to a high level and the others benefit.

Enrollment communication — required language
  All enrollment materials (flyers, parent meetings, telebachillerato presentations) must include:
  "El español de su hijo/a se mantiene. El programa no elimina el español — los estudiantes conservan el nivel que ya tienen. La academia invierte en nahuatl + inglés porque eso les abre más puertas globalmente."
  Translation: "Your child's Spanish is maintained. The program does not eliminate Spanish — students keep the level they already have. The academy invests in Nahuatl + English because that opens more global doors."

"""

# Get current doc end index
doc = service.documents().get(documentId=DOC_ID).execute()
body = doc['body']['content']
end_index = body[-1].get('endIndex', 1) - 1

print(f"Appending {len(NEW_CONTENT)} chars at index {end_index}...")
service.documents().batchUpdate(
    documentId=DOC_ID,
    body={'requests': [{'insertText': {'location': {'index': end_index}, 'text': NEW_CONTENT}}]}
).execute()
print("Inserted. Re-reading for formatting...")
time.sleep(1)

doc2 = service.documents().get(documentId=DOC_ID).execute()
body2 = doc2['body']['content']

# Headings to format
HEADINGS = {
    'APPENDIX E — REVENUE STREAMS':          ('HEADING_2', NAVY, 13),
    'APPENDIX F — SITE COMPARISON':          ('HEADING_2', NAVY, 13),
    'ONLINE CURRICULA & BOOTCAMP RESOURCES': ('HEADING_2', NAVY, 13),
    'THE 4-WEEK BOOTCAMP — TLAMACHIYOTL':    ('HEADING_2', NAVY, 13),
    'FINANCE MODULE 6 — CRYPTO REMITTANCE':  ('HEADING_2', NAVY, 13),
    'LANGUAGES — SPANISH: POSITIONING':      ('HEADING_2', NAVY, 13),
    'Revenue analysis: student outputs':     ('HEADING_3', TEAL, 11),
    'Tier 1 — Immediate revenue':            ('HEADING_3', TEAL, 11),
    'Tier 2 — Medium-term revenue':          ('HEADING_3', TEAL, 11),
    'Tier 3 — Long-term / project-based':    ('HEADING_3', TEAL, 11),
    'Zero-income outputs':                   ('HEADING_3', TEAL, 11),
    'Population and indigenous density':     ('HEADING_3', TEAL, 11),
    'Infrastructure comparison':             ('HEADING_3', TEAL, 11),
    'Why Chicontepec matters despite':       ('HEADING_3', TEAL, 11),
    'Phase recommendation':                  ('HEADING_3', NAVY, 11),
    'Core curricula':                        ('HEADING_3', TEAL, 11),
    'Hardware / electronics':                ('HEADING_3', TEAL, 11),
    'Curriculum outline for the opening':    ('HEADING_3', TEAL, 11),
    'Week 1 — Visual coding':               ('HEADING_3', TEAL, 11),
    'Week 2 — HTML and CSS':                ('HEADING_3', TEAL, 11),
    'Week 3 — Python basics':               ('HEADING_3', TEAL, 11),
    'Week 4 — Portfolio commit':            ('HEADING_3', TEAL, 11),
    'Current best platforms for Mexico':    ('HEADING_3', TEAL, 11),
    'Regulation note':                      ('HEADING_3', ORANGE, 11),
    'Module 6 class design':               ('HEADING_3', TEAL, 11),
    'The objection':                        ('HEADING_3', ORANGE, 11),
    "The academy's position":              ('HEADING_3', NAVY, 11),
    'Why this is a strength':              ('HEADING_3', TEAL, 11),
    'Enrollment communication':            ('HEADING_3', NAVY, 11),
}

fmt = []
for elem in body2:
    if 'paragraph' not in elem: continue
    si, ei = elem.get('startIndex',0), elem.get('endIndex',0)
    text = ''.join(r.get('textRun',{}).get('content','') for r in elem['paragraph'].get('elements',[])).strip()
    for key, (style, col, sz) in HEADINGS.items():
        if text.startswith(key[:35]):
            fmt += [
                {'updateParagraphStyle': {
                    'range': {'startIndex': si, 'endIndex': ei},
                    'paragraphStyle': {'namedStyleType': style},
                    'fields': 'namedStyleType'
                }},
                {'updateTextStyle': {
                    'range': {'startIndex': si, 'endIndex': ei - 1},
                    'textStyle': {'foregroundColor': rgb(col), 'bold': True,
                                  'fontSize': {'magnitude': sz, 'unit': 'PT'}},
                    'fields': 'foregroundColor,bold,fontSize'
                }},
            ]
            break

print(f"Applying {len(fmt)} formatting requests...")
for i in range(0, len(fmt), 50):
    service.documents().batchUpdate(documentId=DOC_ID, body={'requests': fmt[i:i+50]}).execute()
    time.sleep(0.2)
print("Done.")
