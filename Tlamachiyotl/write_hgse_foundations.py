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

HGSE_TEXT = """\

HGSE COURSE FOUNDATIONS — RESEARCH, FRAMEWORKS & DESIGN CONNECTIONS

Overview

The academy's founder studied at Harvard Graduate School of Education (HGSE) and at MIT, accumulating a body of coursework that is directly relevant to Tlamachiyotl's design. This section maps each course's key frameworks and authors to specific aspects of the academy's design, identifies references to add to existing doc sections, and flags potential faculty contacts for partnership. All citations here are drawn from course readings, essays, and design projects completed during study.

Courses reviewed: H126 (Neuroscience of Education), H700 (Language Development and Literacy), HPL / How People Learn + Module 6 Design Proposal, HT 123 J-term (Large-Scale Informal Learning Design), MIT 2.S972 (Immersive and Interactive Design), T581 (Learning Design and EdTech), HAA 19Z (Pre-Columbian Art History), ANTHRO 2175 (Anthropology of Knowledge), EDU S043 + S022 (Statistics and Quantitative Methods).

Language development and biliteracy — EDU H700

H700 (Language Development and Literacy) is the single most directly applicable course to the academy's language medium decision and curriculum design. The course covered: word learning in home and preschool settings (Week 4), phonological awareness (Week 5), bilingualism and word learning (Week 7), instructional approaches for lexical development in bilingual learners (Week 8), morphology and syntax (Week 9), academic language development (Week 11), and decontextualized language as a predictor of reading comprehension.

Key findings and their design implications for Tlamachiyotl:

Dual-language exposure and bilingual development. Research reviewed in H700 (Yow & Flynn, 2016; dual language exposure papers) demonstrates that bilingual children who receive structured input in both languages from early stages develop metalinguistic awareness — the ability to reflect on language structure — at higher rates than monolinguals. This is directly relevant to the Nahuatl-primary + Spanish-as-second-language design: students who are taught to read and write in Nahuatl first, then in Spanish, gain a cross-language literacy advantage documented in the Cummins Common Underlying Proficiency model (already in doc). H700 provided the empirical grounding for that model.

Academic language (decontextualized language). A central theme of H700 was the distinction between everyday conversational language and the academic register required for school success. Rowe (2013) and work by Uccelli et al. (2019, Child Development) documented that decontextualized language — language that extends beyond the immediate context, used in storytelling, explanation, and argument — is the strongest predictor of later reading comprehension. Implication for Tlamachiyotl: academic Nahuatl must include this register. Huapango verse, oral history narration, and the décima tradition (already in the Arts section) are precisely the vehicles through which academic Nahuatl register is transmitted in the Huasteca oral tradition. This frames the arts curriculum not just as enrichment but as academic language instruction.

Phonological awareness in indigenous languages. H700 Week 5 covered phonological awareness as the foundational prerequisite for reading acquisition (Treiman & Zukowski, 1991; LDOnLine, phonological awareness guidelines). In a Nahuatl-medium program, phonological awareness must be built in Nahuatl before Spanish literacy is introduced. The research makes clear that phonological awareness transfers across languages (within the same script system); a student who achieves phonological awareness in Nahuatl will have a head start in Spanish reading — not a handicap. This is the empirical rebuttal to the common parental objection that Nahuatl-medium instruction delays Spanish literacy.

Extended discourse and teacher talk. A specific paper from H700 (Support for Extended Discourse in Teacher Talk with Linguistically Diverse Preschoolers) documented that the linguistic quality of teacher speech — specifically the use of extended narrative and explanation rather than simple question-answer exchanges — predicts student academic language gains. This frames the teacher training requirement (Step 0, Appendix B) in concrete terms: Nahuatl-fluent teachers need training in extended discourse pedagogy in Nahuatl, not just fluency.

References to add to existing doc sections (H700):
  Yow, W.Q. & Flynn, E. (2016). A bilingual advantage in task switching. Bilingualism: Language and Cognition, 19(3), 81–100.
  Uccelli, P. et al. (2019). Toward a linguistic theory of academic language. Child Development.
  Treiman, R. & Zukowski, A. (1991). Levels of phonological awareness. In Phonological Processes in Literacy, pp. 67–83.
  Rowe, M.L. (2013). Decontextualized language input and preschoolers' school readiness. Early Education and Development.

Neuroscience of learning — EDU H126

H126 (Neuroscience of Education) covered the neural bases of poverty and neglect, brain plasticity in language development, and the science of cognitive load. Three findings are directly applicable to the academy:

Neural bases of poverty and neglect. H126 presented research showing that chronic poverty and environmental neglect produce measurable structural differences in the developing brain — particularly in the prefrontal cortex (executive function) and hippocampus (memory). These effects are partially reversible with high-quality environmental intervention in early and middle childhood. This frames the academy not merely as an educational program but as a developmental intervention: the enriched, relationship-based, stimulus-rich environment of the academy is itself a form of cognitive remediation for students who have experienced the effects of marginalization.

Brain plasticity and language. H126 covered the critical period hypothesis for language acquisition and the evidence for plasticity beyond the canonical critical period. The key finding for Tlamachiyotl: Nahuatl-medium instruction at the academy age range (roughly 12–18 years) is not "too late" for phonological acquisition in Nahuatl — adolescent learners retain significant plasticity for language within an already-known language family. Students who are heritage Nahuatl speakers (oral competence, limited formal literacy) are in a far more favorable position than true adult L2 learners.

Executive function and academic readiness. H126 covered the role of executive function — working memory, cognitive flexibility, and inhibitory control — in academic performance. The finding that arts instruction and physical education (sports) both strengthen executive function circuits in the developing brain provides the neurological justification for the academy's integrated model: Nahuatl language + STEM + finance + sports + arts is not a scattered curriculum — it is a multi-system intervention on the circuits that underlie all academic learning.

References to add (H126):
  Gaab, N. & Nelson, C.A. (eds., 2019). Neuroscience and Education: From Research to Practice.
  Fogler, J. (2019). Executive function in academic settings [H126 lecture notes, HGSE].
  Scarborough, H.S. (2001). Connecting early language and literacy to later reading (dis)abilities. In Handbook of Early Literacy Research.

How People Learn — pedagogical design frameworks

The HPL course — and in particular the Module 6 Design Proposal — is the most structurally important course for Tlamachiyotl because the design proposal was literally about this program. The proposal, submitted in 2020 and graded at HGSE, outlined a flexible-hour out-of-school education program for young indigenous girls in rural Latin American communities. It articulated the same core design principles that now underpin the academy: relationships, motivation, and cultural relevance.

Bronfenbrenner's ecological model. The design proposal used Bronfenbrenner's model of child development — which describes the nested environments (microsystem, mesosystem, exosystem, macrosystem) that shape a learner's development — to frame the program's multi-actor design: learner, parent, teacher, school, and community. Tlamachiyotl should explicitly adopt this framework for its student support model: not just classroom instruction, but intentional design of the parent relationship (family outreach), the peer relationship (cohort structure), the teacher relationship (community recruitment, small group), and the community relationship (public performances, cooperative).

Universal Design for Learning (UDL). HPL Module 3 covered UDL extensively — the framework developed by CAST (Center for Applied Special Technology) that designs learning experiences for the full range of learners from the outset rather than retrofitting accommodations. UDL's three principles — multiple means of representation, action and expression, and engagement — map directly to what the academy already intends: Nahuatl-medium (representation), project-based assessment rather than exams (action and expression), and arts + sports + digital income as motivation levers (engagement). The academy should explicitly adopt UDL as its pedagogical framework — it provides a defensible, internationally recognised language for describing what the curriculum does.

Authentic assessment (Wiggins, 2006). HPL Module 5 introduced the concept of authentic assessment — "Assessment should determine whether you can use your learning, not merely whether you learned stuff" (Wiggins, 2006). This is the research foundation for the academy's no-exam policy (already referenced) and the Piscine-style peer-validated project assessment (bootcamp section). Wiggins' authentic assessment framework is a citable, HGSE-standard justification for the assessment design.

Visible learning — Hattie & Yates (2013). HPL Module 5 assigned Hattie & Yates, Visible Learning and the Science of How We Learn (2013). Hattie's meta-analysis of 800+ educational studies identified the effect sizes of different interventions; the highest-effect items relevant to Tlamachiyotl are: feedback (d=0.73), teacher-student relationships (d=0.72), peer tutoring (d=0.55), and cooperative learning (d=0.41). These effect sizes provide a rank ordering for where to invest limited teaching time — and they all point toward the academy's relationship-first, peer-validated, cohort-based design.

Deliberate practice — Colvin (2008). HPL Module 5 also assigned Colvin, Talent is Overrated (2008), a summary of Ericsson's deliberate practice research. The core finding — that domain expertise is produced by structured, repetitive, feedback-rich practice, not innate talent — is the research foundation for the Piscine bootcamp format (daily coding practice with peer code review) and for the music curriculum (daily instrument practice, not just exposure).

References to add (HPL):
  Bronfenbrenner, U. (1979). The Ecology of Human Development. Harvard University Press.
  CAST (2018). Universal Design for Learning Guidelines version 2.2. cast.org.
  Wiggins, G. (2006). Healthful eating as a model for authentic education. In Exeter Plenary Lecture.
  Hattie, J. & Yates, G. (2013). Visible Learning and the Science of How We Learn. Routledge.
  Colvin, G. (2008). Talent is Overrated: What Really Separates World-Class Performers from Everybody Else. Portfolio.
  Schwartz, D.L., Tsang, J.M., & Blair, K.P. (2016). The ABCs of How We Learn. Norton.

Arts and informal learning — HT 123 J-term and HAA 19Z

HT 123 (J-term, Large-Scale Informal Learning Design) directly prefigures the arts section now in this document. The J-term brainstorm produced two project ideas that map directly to Tlamachiyotl: (1) using music and popular music to transmit content — specifically vocabulary and literacy — for learners from diverse cultural backgrounds; and (2) a gamification approach to vocabulary learning (Tamagotchi/Pokémon style). The brainstorm explicitly cited: Kilman (2006), Learning Lakota (Teaching Tolerance, 30, 28–35) — a case study of using traditional indigenous music to transmit language — and Chris Emdin's hip-hop pedagogy (For White Folks Who Teach in the Hood) as a model for culturally responsive music-based instruction. Both are directly applicable to the Nahuatl music track.

HAA 19Z (Pre-Columbian Latin American Art History) is the single most underutilised resource in the academy's current design. The course was a 24-lecture survey of pre-Columbian Latin American art taught by Professor Tom Cummins at Harvard — covering codices, textiles, ceramics, ritual objects, architectural programmes, and the visual culture of the Mexica, Maya, Zapotec, Inca, and regional cultures. The Huasteca region and its material culture were part of this survey. This gives the founder first-hand academic grounding in the visual arts tradition that the bordado huasteco, amate, and codex-based curriculum content in the Arts section derives from.

Professor Tom Cummins (Harvard Art Museums / HAA) is a potential faculty contact for the academy's arts curriculum and for a potential HGSE/Harvard research partnership on indigenous visual arts pedagogy. His research focuses on indigenous visual and material culture in Latin America — exactly the content the academy will teach.

Implications for the arts section:
  Add explicit codex-literacy component to the visual arts curriculum — reading and interpreting pre-Columbian Nahuatl codices (Borgia Group, Mendocino) is an advanced arts + history + Nahuatl language activity.
  Kilman (2006) and Emdin citations should be added to the Arts section evidence base.
  A field trip or remote session with the Harvard Art Museums collections (strong Mesoamerican holdings) is a low-cost, high-credibility programme element.

References to add (HT 123 + HAA 19Z):
  Kilman, C. (2006). Learning Lakota. Teaching Tolerance, 30, 28–35. [Indigenous language revival through traditional music — direct precedent]
  Emdin, C. (2016). For White Folks Who Teach in the Hood… and the Rest of Y'all Too. Beacon Press. [Hip-hop pedagogy and culturally responsive instruction]
  Shapiro, J. (2018). Digital Play for Global Citizens. Joan Ganz Cooney Center. [Digital play and global citizenship literacy for underserved youth]
  Cummins, T. (multiple). Harvard Art Museums faculty publications on pre-Columbian Nahuatl visual culture.

Immersive and interactive design — MIT 2.S972

MIT 2.S972 (Immersive Design, Fall 2018) introduced Unity VR/AR development, interactive narrative design, and the pedagogical case for immersive learning environments. Key takeaways for Tlamachiyotl:

VR for motivation and transfer. The course's foundational argument was that immersive environments increase motivation and improve transfer of knowledge by placing the learner inside the subject matter. For the academy's STEM track, this suggests a long-term aspiration: Nahuatl-language VR experiences of pre-Columbian Huasteca environments, Nahuatl cosmology, and traditional craft processes — produced by students as senior capstone projects. This connects STEM (Unity/coding), Arts (visual design), and Language (Nahuatl narration in the VR experience) in a single high-complexity project.

Storytelling in immersive media. A key insight from MIT 2.S972 was that VR requires fundamentally different narrative design than 2D media — spatial storytelling, embodied perspective, and non-linear agency. These are design skills distinct from traditional coding. A student who can design an immersive experience in Nahuatl about traditional agriculture or the huapango tradition has a rare, defensible portfolio asset that no other student in Mexico is likely to have.

Unity as shared tool. Both MIT 2.S972 and T581 (Learning Design) used Unity. The founder's familiarity with Unity enables direct teaching of the platform in the academy's STEM concentration without requiring an external instructor for the introductory module.

References to add:
  MIT Media Lab / HGSE. Immersive Learning Experiences [course materials, 2.S972, 2018].

Learning design and EdTech — T581

T581 (Learning Design and EdTech) covered the full design process for educational technology, including Scratch game design, Unity 2D, and the historical lineage of learning-through-play from Froebel (inventor of kindergarten) through Pestalozzi, Montessori, and contemporary game-based learning. Key design principle for Tlamachiyotl: the distinction between high-impact curriculum products (designed with clear pedagogical goals and measurable outcomes) and low-impact management/administrative ed-tech tools. The academy should be conservative about adopting ed-tech that does not meet this standard.

The Scratch → Unity → professional development environment progression from T581 maps directly to the academy's STEM curriculum ladder: Scratch (Year 1 bootcamp, Week 1), HTML/CSS (Week 2), Python (Week 3), GitHub (Week 4), Unity 2D (Year 2 concentration).

The toy-design lineage covered in T581 (Froebel's kindergarten philosophy, Montessori materials, Pestalozzi's hands-on learning) provides the theoretical foundation for the makerspace track: physical making, tinkering, and construction are historically the oldest and most validated forms of active learning.

Data and evaluation — EDU S043 and S022

S043 and S022 covered quantitative methods including R, exploratory data analysis (EDA), IRB research design, regression, and descriptive statistics. The founder's statistical training directly supports the academy's research agenda (see Research Gaps section and equivalent sections in Arts and Language areas). Specifically:

IRB design. The four research questions the academy can answer (language outcomes, out-migration, cooperative sustainability, content market demand) all require IRB-approved research protocols. S043 covered IRB submission and human subjects research ethics — the founder can design and submit these protocols without hiring external researchers.

Quantitative outcome tracking. S022's R curriculum provides the tools to build a simple longitudinal student tracking system: enrollment data, assessment scores (UDL-style portfolio assessments, not standardised tests), attendance, and outcome variables. This is the infrastructure for the academy's own research function and for reporting to funders.

Faculty contacts — potential HGSE / Harvard partnerships

Based on the course portfolio, the following Harvard/MIT faculty are potential research partners or warm-contact introductions:

Professor Meredith Rowe (HGSE, H700): World-leading researcher on language development, decontextualized language, and early literacy in bilingual populations. Her work is already the empirical backbone of the academy's language medium section. A research partnership framed as a Nahuatl biliteracy longitudinal study would be a natural fit for her lab — and she is explicitly named in the 8 warm-intro emails already listed.

Professor Nadine Gaab (HGSE, H126): Neuroscience of reading and language; early identification of reading difficulties. A partnership on tracking phonological awareness development in Nahuatl-medium learners would produce genuinely novel data — no existing longitudinal dataset exists for Nahuatl literacy acquisition.

Professor Tom Cummins (Harvard, HAA 19Z): Pre-Columbian visual culture and indigenous material culture. Direct connection to the arts curriculum content; potential advisor for the codex-literacy component and for a possible Harvard Art Museums educational partnership.

Professor Mitch Resnick (MIT Media Lab): Creator of Scratch. The connection between the academy's STEM curriculum (Scratch as entry point) and the MIT Media Lab's Lifelong Kindergarten group is a natural partnership. Resnick is already named in the warm-intro email list. The HAA/HGSE coursework strengthens the pitch: the Tlamachiyotl founder is an HGSE-trained learning designer who used Scratch in graduate coursework.

Fernando Reimers (HGSE, T522): Global citizenship education, education policy in Latin America. T522 covered civic engagement and global citizenship — Reimers is the leading HGSE voice on education in the Global South. Already named in warm-intro list.

"""

# Get current doc end index
doc = service.documents().get(documentId=DOC_ID).execute()
body_content = doc.get('body', {}).get('content', [])
insert_idx = body_content[-1].get('endIndex', 1) - 1
print(f"Appending {len(HGSE_TEXT)} chars at index {insert_idx}...")

service.documents().batchUpdate(
    documentId=DOC_ID,
    body={'requests': [{'insertText': {
        'location': {'index': insert_idx},
        'text': HGSE_TEXT
    }}]}
).execute()
print("Inserted. Re-reading for formatting...")

# Re-read and format
doc2 = service.documents().get(documentId=DOC_ID).execute()
body2 = doc2.get('body', {}).get('content', [])

H2_HEADINGS = {'HGSE COURSE FOUNDATIONS — RESEARCH, FRAMEWORKS & DESIGN CONNECTIONS'}

H3_TEAL = {
    'Overview',
    'Language development and biliteracy — EDU H700',
    'Neuroscience of learning — EDU H126',
    'How People Learn — pedagogical design frameworks',
    'Arts and informal learning — HT 123 J-term and HAA 19Z',
    'Immersive and interactive design — MIT 2.S972',
    'Learning design and EdTech — T581',
    'Data and evaluation — EDU S043 and S022',
    'Faculty contacts — potential HGSE / Harvard partnerships',
}

# Bold orange labels for specific key terms
ORANGE_LABELS = [
    'Dual-language exposure',
    'Academic language',
    'Phonological awareness',
    'Extended discourse',
    'Neural bases of poverty',
    'Brain plasticity',
    'Executive function',
    'Bronfenbrenner',
    'Universal Design for Learning',
    'Authentic assessment',
    'Visible learning',
    'Deliberate practice',
    'VR for motivation',
    'Storytelling in immersive',
    'Unity as shared tool',
    'IRB design',
    'Quantitative outcome',
]

fmt = []
for elem in body2:
    if 'paragraph' not in elem:
        continue
    si = elem.get('startIndex', 0)
    ei = elem.get('endIndex', 0)
    p = elem['paragraph']
    text = ''.join(r.get('textRun', {}).get('content', '') for r in p.get('elements', [])).strip()

    if text in H2_HEADINGS:
        fmt.append({'updateParagraphStyle': {
            'range': {'startIndex': si, 'endIndex': ei},
            'paragraphStyle': {'namedStyleType': 'HEADING_2'},
            'fields': 'namedStyleType'
        }})
        fmt.append({'updateTextStyle': {
            'range': {'startIndex': si, 'endIndex': ei - 1},
            'textStyle': {
                'foregroundColor': rgb(NAVY),
                'bold': True,
                'fontSize': {'magnitude': 13, 'unit': 'PT'},
            },
            'fields': 'foregroundColor,bold,fontSize'
        }})
        print(f"  H2: {text[:60]}")
        continue

    matched_h3 = False
    for h3 in H3_TEAL:
        if text.startswith(h3[:40]):
            fmt.append({'updateParagraphStyle': {
                'range': {'startIndex': si, 'endIndex': ei},
                'paragraphStyle': {'namedStyleType': 'HEADING_3'},
                'fields': 'namedStyleType'
            }})
            fmt.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': ei - 1},
                'textStyle': {
                    'foregroundColor': rgb(TEAL),
                    'bold': True,
                    'fontSize': {'magnitude': 11, 'unit': 'PT'},
                },
                'fields': 'foregroundColor,bold,fontSize'
            }})
            print(f"  H3: {text[:60]}")
            matched_h3 = True
            break

    if not matched_h3:
        for label in ORANGE_LABELS:
            if text.startswith(label):
                period = text.find('.')
                end_idx = min(si + period + 1, ei - 1) if period != -1 and period < 60 else min(si + len(label) + 1, ei - 1)
                fmt.append({'updateTextStyle': {
                    'range': {'startIndex': si, 'endIndex': end_idx},
                    'textStyle': {'bold': True, 'foregroundColor': rgb(ORANGE)},
                    'fields': 'bold,foregroundColor'
                }})
                break

print(f"\nApplying {len(fmt)} formatting requests...")
for i in range(0, len(fmt), 50):
    service.documents().batchUpdate(
        documentId=DOC_ID, body={'requests': fmt[i:i+50]}
    ).execute()
    print(f"  {min(i+50, len(fmt))}/{len(fmt)}")

print("Done.")
