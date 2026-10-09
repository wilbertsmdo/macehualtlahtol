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
GRAY   = {'red': 0.42, 'green': 0.42, 'blue': 0.42}

def rgb(c): return {'color': {'rgbColor': c}}

# ── All insertions in DESCENDING index order ─────────────────────────────────

# 1. Harvard Art Museums international partner (after Silkroad paragraph, ei=137555)
HARVARD_ART = (
    "\nHarvard Art Museums — Mesoamerican Collection and Education Partnership: Harvard's museums hold one of the "
    "strongest pre-Columbian Mesoamerican collections in the United States, with significant Nahuatl-tradition "
    "objects (codices, ceramics, textiles, featherwork). Professor Tom Cummins (Harvard Anthropology / HAA) "
    "specialises in pre-Columbian indigenous visual culture in Latin America — the precise tradition the "
    "academy's arts curriculum draws from. His course (HAA 19Z, 24-lecture survey of Latin American pre-"
    "Columbian art) was completed by the academy's founder. Pathways: (a) remote classroom session using "
    "Harvard Art Museums' open-access object database (harvardartmuseums.org/collections); (b) academic "
    "partnership with Prof. Cummins for arts curriculum design and HGSE/Harvard research collaboration on "
    "indigenous arts pedagogy; (c) codex facsimiles from FAMSI (Foundation for the Advancement of "
    "Mesoamerican Studies) for classroom use — freely available online. Contact: "
    "harvardartmuseums.org/study/academic-program.\n"
)

# 2. Codex literacy curriculum item (after Visual arts line, ei=133185)
CODEX_LITERACY = (
    "\nCodex literacy: Reading and interpreting pre-Columbian Nahuatl codices — the Borgia Group and Codex "
    "Mendoza — as an advanced arts + Nahuatl language + history activity. Pre-Columbian codices use a "
    "pictographic-ideographic visual system; teaching students to read them is simultaneously an arts practice "
    "and a high-register Nahuatl literacy exercise, connecting the visual arts curriculum to the Nahuatl "
    "language track. High-quality digital facsimiles are freely available via FAMSI (famsi.org) and the "
    "Library of Congress digital collections. This is a genuine differentiator — no other coding academy "
    "in Mexico offers codex literacy. Source framework: HAA 19Z (Harvard, Pre-Columbian Latin American "
    "Art History).\n"
)

# 3. Kilman/Emdin evidence (after Language development paragraph, ei=126419)
KILMAN_EMDIN = (
    "\nTwo research-backed precedents from informal learning design directly support this approach. "
    "Kilman (2006, Teaching Tolerance) documented the use of traditional Lakota indigenous music to "
    "transmit vocabulary and cultural identity in a reservation school — the most direct published "
    "precedent for the Nahuatl huapango approach. Emdin (2016, For White Folks Who Teach in the "
    "Hood) demonstrates the motivational and retention advantage of using culturally resonant musical "
    "forms — hip-hop in his case, huapango in ours — as the delivery medium for academic content. "
    "Shapiro (2018, Joan Ganz Cooney Center) adds evidence for music-based digital play as a global "
    "citizenship learning vehicle for underserved youth. Sources reviewed at HGSE (HT 123 J-term).\n"
)

# 4. New academic references block (before "End of Academic References", at si=74585)
NEW_REFS = (
    "\n-- HGSE course library — language development and biliteracy (EDU H700) --\n"
    "Yow, W.Q. & Flynn, E. (2016). A bilingual advantage in task switching. Bilingualism: Language and Cognition, 19(3), 81–100.\n"
    "Uccelli, P. et al. (2019). Core academic language skills and bilingual learners. Child Development, 90(5).\n"
    "Treiman, R. & Zukowski, A. (1991). Levels of phonological awareness. In Phonological Processes in Literacy. Erlbaum, pp. 67–83.\n"
    "Rowe, M.L. (2013). Decontextualized language input and preschoolers' school readiness. Topics in Language Disorders, 33(2), 177–189.\n"
    "Scarborough, H.S. (2001). Connecting early language and literacy to later reading disabilities. In Handbook of Early Literacy Research. Guilford, pp. 97–110.\n"
    "Lieven, E. (2019). Input, interaction, and learning in early language development. In Learning through Language. Cambridge University Press.\n"
    "\n-- HGSE course library — neuroscience of education (H126) --\n"
    "Gaab, N. & Nelson, C.A. (2019). Neuroscience and Education: From Research to Practice. MIT Press.\n"
    "Blair, C. & Raver, C.C. (2016). Poverty, stress, and brain development: New directions for prevention and intervention. Academic Pediatrics, 16(3S), S30–S36.\n"
    "\n-- HGSE course library — learning design and pedagogy (HPL / How People Learn) --\n"
    "Bronfenbrenner, U. (1979). The Ecology of Human Development. Harvard University Press.\n"
    "CAST (2018). Universal Design for Learning Guidelines version 2.2. cast.org.\n"
    "Wiggins, G. (2006). Authentic assessment. Relearning by Design.\n"
    "Hattie, J. & Yates, G.C.R. (2013). Visible Learning and the Science of How We Learn. Routledge.\n"
    "Colvin, G. (2008). Talent is Overrated. Portfolio.\n"
    "Schwartz, D.L., Tsang, J.M. & Blair, K.P. (2016). The ABCs of How We Learn. Norton.\n"
    "Henderson, A. (2011). A Guide to the Theory and Practice of Inclusion. pp. 43–63.\n"
    "\n-- HGSE course library — arts and informal learning (HT 123 J-term; HAA 19Z) --\n"
    "Kilman, C. (2006). Learning Lakota. Teaching Tolerance, 30, 28–35.\n"
    "Emdin, C. (2016). For White Folks Who Teach in the Hood. Beacon Press.\n"
    "Shapiro, J. (2018). Digital Play for Global Citizens. Joan Ganz Cooney Center.\n"
    "Bolduc, J. (2009). Effects of music instruction on emergent literacy capacities. Early Childhood Education Journal, 37(1), 45–52.\n"
    "Hetland, L. & Winner, E. (2004). Cognitive transfer from arts education to non-arts outcomes. In Handbook of Research and Policy in Art Education.\n"
    "Catterall, J.S., Chaparro, S.A. & Iwanaga, J.M. (2012). Doing well and doing good by doing art. Champions of Change. Arts Education Partnership.\n"
    "\n-- HGSE course library — immersive design and constructionism (MIT 2.S972; T581) --\n"
    "Resnick, M. (2017). Lifelong Kindergarten: Cultivating Creativity through Projects, Passion, Peers, and Play. MIT Press.\n"
    "Papert, S. (1980). Mindstorms: Children, Computers, and Powerful Ideas. Basic Books.\n"
)

# 5. Phonological transfer argument (after CLAIM 1 item 4 Mexico study, ei=56860)
PHONOLOGICAL_TRANSFER = (
    "\nPhonological awareness transfer — H700 evidence. Research in language development establishes that "
    "phonological awareness — the ability to perceive and manipulate the sound structure of language — "
    "transfers across languages within the same learner (Treiman & Zukowski, 1991). A student who "
    "achieves phonological awareness in Nahuatl transfers that metalinguistic skill to Spanish reading "
    "acquisition without remediation. This is the empirical rebuttal to the parental objection that "
    "Nahuatl-medium instruction delays Spanish literacy: it does not delay it — it builds the foundational "
    "cognitive prerequisite that accelerates Spanish literacy when introduced as L2. The transfer effect "
    "is strongest when both languages share a phonological system (which Nahuatl and Spanish largely do, "
    "both being syllable-timed, with high phoneme-grapheme correspondence). "
    "Source: Treiman & Zukowski (1991); Rowe, M.L., EDU H700, HGSE 2019.\n"
)

# 6. UDL / Bronfenbrenner / Hattie pedagogy block (after "cohort-based pedagogy" paragraph, ei=50063)
UDL_BLOCK = (
    "\nPedagogical framework — Universal Design for Learning (UDL). The academy's curriculum aligns with "
    "UDL (CAST, 2018) — the internationally recognised learning design standard developed at Harvard. "
    "UDL's three principles map directly to what the academy already does: (1) Multiple means of "
    "representation: Nahuatl-medium instruction + visual arts + music + hands-on making; (2) Multiple "
    "means of action and expression: project-based portfolio assessment, peer code review, artisan "
    "production, public performance — no single-modality exams; (3) Multiple means of engagement: "
    "digital income as intrinsic motivation, sports, arts, and cohort belonging as engagement levers. "
    "Labelling the curriculum as UDL-compliant provides a recognised framework for grant applications "
    "and partnership conversations with HGSE and international education organisations.\n"
    "\nEcological design — Bronfenbrenner's model. The academy intervenes on multiple levels of the "
    "student's environment simultaneously (Bronfenbrenner, 1979): microsystem (cohort peer relationships, "
    "teacher-student relationship), mesosystem (school-family outreach, parent information sessions), "
    "exosystem (cooperative employment for graduates, artisan market, digital income), macrosystem "
    "(Nahuatl cultural revival, Mexico EIB policy context). Programs that intervene only at the classroom "
    "level produce smaller and less durable effects. The academy's multi-actor design is the structural "
    "response to this research.\n"
    "\nVisible learning — effect size evidence (Hattie & Yates, 2013). Meta-analysis of 800+ educational "
    "studies identifies what actually moves the needle. Highest-effect interventions relevant to the "
    "academy: feedback (d=0.73), teacher-student relationships (d=0.72), peer tutoring (d=0.55), "
    "cooperative learning (d=0.41). Lowest-effect: homework alone (d=0.29), class size reduction alone "
    "(d=0.21). These effect sizes confirm the academy's design priorities — relationship-first, "
    "peer-validated, feedback-rich learning — and give funders a quantitative reason why the model "
    "is better than simply hiring more teachers.\n"
)

# 7. Extended discourse + academic language (after IDIEZ section, ei=19250)
EXTENDED_DISCOURSE = (
    "\nAcademic language and extended discourse — H700 evidence. Research from HGSE's EDU H700 (Language "
    "Development and Literacy) adds a further dimension to the monolingual Nahuatl decision: the register "
    "in which instruction is delivered matters as much as the language itself. Decontextualized language "
    "— language that extends beyond the immediate context to narrate, explain, argue, and hypothesise — "
    "is the strongest predictor of academic reading comprehension and school success (Rowe, 2013; "
    "Uccelli et al., 2019). In the Huasteca, decontextualized Nahuatl is preserved and actively practiced "
    "through the huapango tradition: the décima, the oral historical narrative, the improvised verse "
    "duel. Teaching through these forms delivers academic register instruction in Nahuatl — this is the "
    "empirical link between the arts curriculum and the language medium decision. It reframes the arts "
    "track not as enrichment but as a core academic language class.\n"
    "\nImplication for teacher training (Step 0): Nahuatl-medium instruction requires teachers capable "
    "of extended discourse in Nahuatl — sustained narrative, explanation, and argumentation — not just "
    "conversational fluency. The teacher training protocol (IDIEZ or UV Intercultural partnership) must "
    "include explicit extended discourse pedagogy in Nahuatl as a required competency, not an optional "
    "enhancement. Source: EDU H700 lecture readings, HGSE; Rowe (2013); Uccelli et al. (2019).\n"
)

# ── Execute all insertions in descending order in one batchUpdate ─────────────
insertions = [
    (137555, HARVARD_ART),
    (133185, CODEX_LITERACY),
    (126419, KILMAN_EMDIN),
    (74585,  NEW_REFS),
    (56860,  PHONOLOGICAL_TRANSFER),
    (50063,  UDL_BLOCK),
    (19250,  EXTENDED_DISCOURSE),
]

requests = []
for idx, text in sorted(insertions, key=lambda x: -x[0]):
    requests.append({'insertText': {
        'location': {'index': idx},
        'text': text
    }})
    print(f"  Queued insert at {idx}: {text[:60].strip()}...")

print(f"\nSending {len(requests)} insertions...")
service.documents().batchUpdate(
    documentId=DOC_ID, body={'requests': requests}
).execute()
print("Insertions done. Re-reading for formatting...")

# ── Re-read and format new content ───────────────────────────────────────────
doc2 = service.documents().get(documentId=DOC_ID).execute()
body2 = doc2.get('body', {}).get('content', [])

# Bold orange labels for key terms within new paragraphs
ORANGE_START = [
    'Phonological awareness transfer',
    'Pedagogical framework',
    'Ecological design',
    'Visible learning',
    'Academic language and extended discourse',
    'Implication for teacher training',
    'Codex literacy',
    'Two research-backed precedents',
]
TEAL_START = [
    '-- HGSE course library',
    'Harvard Art Museums',
]
GRAY_REFS = [
    'Yow, W.Q.',
    'Uccelli, P.',
    'Treiman, R.',
    'Rowe, M.L.',
    'Scarborough,',
    'Lieven, E.',
    'Gaab, N.',
    'Blair, C.',
    'Bronfenbrenner,',
    'CAST (',
    'Wiggins, G.',
    'Hattie, J.',
    'Colvin, G.',
    'Schwartz, D.',
    'Henderson, A.',
    'Kilman, C.',
    'Emdin, C.',
    'Shapiro, J.',
    'Bolduc, J.',
    'Hetland, L.',
    'Catterall, J.',
    'Resnick, M.',
    'Papert, S.',
]

fmt = []
for elem in body2:
    if 'paragraph' not in elem:
        continue
    si = elem.get('startIndex', 0)
    ei = elem.get('endIndex', 0)
    text = ''.join(r.get('textRun', {}).get('content', '') for r in elem['paragraph'].get('elements', [])).strip()

    for label in ORANGE_START:
        if text.startswith(label):
            dash = text.find('—')
            period = text.find('.')
            end_char = min([x for x in [dash, period] if x > 0], default=len(label))
            end_idx = min(si + end_char + 1, ei - 1)
            fmt.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': end_idx},
                'textStyle': {'bold': True, 'foregroundColor': rgb(ORANGE)},
                'fields': 'bold,foregroundColor'
            }})
            break

    for label in TEAL_START:
        if text.startswith(label):
            dash = text.find('—')
            colon = text.find(':')
            sep = min([x for x in [dash, colon] if x > 0], default=40)
            end_idx = min(si + sep + 1, ei - 1)
            fmt.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': end_idx},
                'textStyle': {'bold': True, 'foregroundColor': rgb(TEAL)},
                'fields': 'bold,foregroundColor'
            }})
            break

    for label in GRAY_REFS:
        if text.startswith(label):
            fmt.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': ei - 1},
                'textStyle': {
                    'foregroundColor': rgb(GRAY),
                    'fontSize': {'magnitude': 8, 'unit': 'PT'},
                    'italic': True,
                },
                'fields': 'foregroundColor,fontSize,italic'
            }})
            break

print(f"Applying {len(fmt)} formatting requests...")
for i in range(0, len(fmt), 50):
    service.documents().batchUpdate(
        documentId=DOC_ID, body={'requests': fmt[i:i+50]}
    ).execute()
    print(f"  {min(i+50, len(fmt))}/{len(fmt)}")

print("Done.")
