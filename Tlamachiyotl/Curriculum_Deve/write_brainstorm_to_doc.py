"""
Create a Google Doc with the Tlamachiyotl Academy brainstorm inside the
'Personal: Email Texts for Guia Futuro' Drive folder.

Pattern mirrors Macehualtlahtol/Sports_Research/write_plan_to_doc.py:
  Phase 1 — insert content
  Phase 2 — apply heading styles (H1 title, H2 sections, H3 subsections)
  Phase 3 — pageBreakBefore on each top-level section + collect headingIds
  Phase 4 — hyperlink TOC entries to their headings

Service account edits content. OAuth user creates the file inside the
target folder so the user owns it (service accounts cannot own files in
a personal Drive).
"""
import json, sys
from google.oauth2.credentials import Credentials as OAuthCreds
from google.oauth2.service_account import Credentials as SACredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SA_KEY     = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
TOKEN_PATH = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json'
SA_EMAIL   = 'ws-financial-analysis@qwen-project-492821.iam.gserviceaccount.com'
FOLDER_ID  = '0B7kFxJCGZsqqTWpManBGb1hvLUE'
DOC_ID     = None  # set to re-run against an existing doc

SA_SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive',
]

sa_creds = SACredentials.from_service_account_file(SA_KEY, scopes=SA_SCOPES)
docs_service = build('docs', 'v1', credentials=sa_creds)

TITLE_LINE = 'Tlamachiyotl Academy — Curriculum & Job Pipeline Brainstorm (v0)'
TOC_HEADER = 'Contents'

SECTIONS = [
    'PREFACE — ANCHORING TO THE 2015 ESSAY',
    'VISION & FRAMING',
    'LOCATION — HUEJUTLA HQ + CHICONTEPEC SATELLITE',
    'STEM CURRICULUM — THE 42-HUASTECA MODEL',
    'FINANCE TRACK — THE EXPLICIT FIFTH LAYER',
    'LANGUAGES — NAHUATL, ENGLISH, MANDARIN',
    'NAHUATL FRAMEWORK & CULTURAL PRODUCTION',
    'SPORTS INTEGRATION',
    'SPACE, EQUIPMENT & CAMPUS STAGING',
    'PARTNERSHIP MATRIX — CURRICULUM',
    'FUNDING STRATEGY — STAGED',
    'JOB PIPELINE — THE SEO-FOR-NAHUA MODEL',
    'LEVERAGING YOUR BACKGROUND — CONCRETE ASKS THIS QUARTER',
    'RISKS & OPEN QUESTIONS',
    'APPENDIX A — CROSSWALK: 2015 ESSAY → 2026 CURRICULUM',
    'APPENDIX B — SUGGESTED NEXT STEPS (30 / 60 / 90 DAYS)',
    'REFERENCES',
]

HEADING_3_PREFIXES = (
    'Phase 0', 'Phase 1', 'Phase 2', 'Phase 3', 'Phase 4', 'Phase 5',
    'Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5',
    'Option A', 'Option B', 'Option C', 'Option D',
    'Concentration', 'Track',
    'Nahuatl —', 'English —', 'Mandarin —',
    'Seed', 'Series', 'Scale', 'Endowment',
    'Curriculum / content', 'Financing', 'Job pipeline',
    'Design principles', 'Core concentrations', 'Project ideas',
    'Why Chinese', 'AI as force', 'Student outputs',
    'The three stacked', 'The one-line vision',
    'Primary artifact', 'Teacher pipeline',
    'What the essay says', 'What the curriculum does',
    '30 days', '60 days', '90 days',
    'Books', 'Programs', 'Benchmarks', 'Mexican context', 'Essay cited',
)

CONTENT = r"""Tlamachiyotl Academy — Curriculum & Job Pipeline Brainstorm (v0)
By Wilbert Sánchez · 2026-10-01 · Working document
Based on and operationalizing: "¿Y si nos dejáramos de quejar? Tendríamos que educarnos" (Sánchez, 2015)

Contents
PREFACE — ANCHORING TO THE 2015 ESSAY
VISION & FRAMING
LOCATION — HUEJUTLA HQ + CHICONTEPEC SATELLITE
STEM CURRICULUM — THE 42-HUASTECA MODEL
FINANCE TRACK — THE EXPLICIT FIFTH LAYER
LANGUAGES — NAHUATL, ENGLISH, MANDARIN
NAHUATL FRAMEWORK & CULTURAL PRODUCTION
SPORTS INTEGRATION
SPACE, EQUIPMENT & CAMPUS STAGING
PARTNERSHIP MATRIX — CURRICULUM
FUNDING STRATEGY — STAGED
JOB PIPELINE — THE SEO-FOR-NAHUA MODEL
LEVERAGING YOUR BACKGROUND — CONCRETE ASKS THIS QUARTER
RISKS & OPEN QUESTIONS
APPENDIX A — CROSSWALK: 2015 ESSAY → 2026 CURRICULUM
APPENDIX B — SUGGESTED NEXT STEPS (30 / 60 / 90 DAYS)
REFERENCES

PREFACE — ANCHORING TO THE 2015 ESSAY

This brainstorm is the operational implementation of the manifesto you wrote eleven years ago, "¿Y si nos dejáramos de quejar? Tendríamos que educarnos." The essay's "Mente" chapter already names the four pillars of the curriculum below — English, Sciences, Engineering/Programación, Finanzas — plus the two population priorities (children and women) and the two attitudinal foundations (confianza-humildad, dejar de quejarse). This document does not propose a different program; it specifies how to build the one the essay already called for, in a specific place (Northern Veracruz / Huasteca), with specific partners, a specific funding stack, and a specific job pipeline.

Essay cited verbatim at the top of each curriculum section below, so the operational decisions can always be traced back to the stated intent. Appendix A provides the full crosswalk.

Two deltas vs. the 2015 essay, both earned by eleven years of context:

First, the curriculum is delivered in Nahuatl as medium of instruction, not merely as cultural heritage. The essay (p. 32-33) argued that lenguas indígenas are "soluciones a problemas humanos" of equal rank to any other language and specifically asked whether Nahuatl might be excellent for abstract or scientific concepts the way yiddish is for emotional ones. The academy answers that question by using Nahuatl as the working language and producing cultural artifacts in it at scale. This is only now possible because of AI tooling (your own Nahuatl translator + TTS projects, Mozilla Common Voice, LLM-mediated bilingual instruction).

Second, the sports pillar — not in the 2015 essay — enters because the Macehualtlahtol Sports_Research work (2026) completed a 648-line program design showing that elite-athlete pathways are achievable with ~MXN $150K/year for 30 athletes using the Clontarf scholar-athlete inversion ("no school → no training"). Sports was the one piece the 2015 essay implicitly left out, and the sports research supplies it. The two pillars are mutually reinforcing: STEM feeds the sports program (health data, screening apps, measurement) and sports attendance drives STEM retention (daily belonging anchor).


VISION & FRAMING

The three stacked reference models.

No single existing program does what you want. The closest shape is a stack of five models, each contributing one layer:

Harlem Children's Zone (Geoffrey Canada) — whole-child, cradle-to-career wrap-around. Borrow: integrated model, measurement rigor, the pipeline is the program.

Clontarf Foundation (Australia, Aboriginal boys) — sport + culture + school discipline. Borrow: the "no school → no training" inversion, 150+ site replicability. Already your sports anchor.

École 42 (Paris + global) — peer-learning STEM without a degree. Borrow: project-based, no teachers, admission by Piscine, employable skills.

Plan Ceibal (Uruguay) + Masakhane (African NLP) + First Voices (Canada) — hardware-at-scale + indigenous NLP + language-tech artifact production. Borrow: students are producers of cultural tooling, not just consumers.

SEO (your alma mater) + QuestBridge + Posse — elite ladder from marginalized community to top institutions. Borrow: explicit placement pipeline, alumni flywheel, corporate partners pay for pipeline access.

The one-line vision.

A Nahua academy where every student, in Nahuatl, builds things with code, with their hands, and with their body — and leaves with a passport to global work and global sport without ever leaving who they are.

What the essay says. "La educación es la clave para que nuestro país esté del proverbial 'otro lado'" (p. 13). "La única manera es soñar en grande, pues los problemas de México y el mundo no son problemas que afecten a unas pocas personas" (p. 29). This brainstorm takes those two sentences literally.


LOCATION — HUEJUTLA HQ + CHICONTEPEC SATELLITE

Recommendation: Huejutla de Reyes (Hidalgo) as HQ + Chicontepec or Ixhuatlán de Madero (Veracruz) as satellite, from year 2. Not either/or.

Option A — Huejutla (HGO). Pros: ~130K population, UAEH extension campus, hospital-grade medical, highway, fiber internet available, airport access via Tampico/Pachuca, banking and supplier infrastructure. Cons: less Nahuatl immersion in central town; service-town culture dilutes language goal.

Option B — Chicontepec (VZ). Pros: Nahuatl-dominant daily life, strong traditional governance, authentic immersion. Cons: weak internet, no clinic-grade medical, hard to attract teachers to live there, limited supplier access for makerspace parts.

Option C — Ixhuatlán de Madero (VZ). Pros: midway, Nahua / Tepehua / Otomí trilingual zone, access to Papantla cultural circuit. Cons: smallest; thinnest infrastructure.

Option D — Zongolica (VZ). Flagged by Sports_Research for altitude physiology, but it is a different Nahuatl variant from Huasteca Nahuatl, and splits focus from the Huejutla-Chicontepec corridor. Not recommended as primary.

Why dual-site works. Huejutla houses the computers, fiber, teachers who need adult services, visiting partners, and the sports campus purchase. The satellite in Chicontepec/Ixhuatlán keeps the program honest about Nahuatl immersion and recruits kids from villages too far to commute. Weekly rotation (3 days Huejutla / 2 days satellite, or similar) is also the natural answer to "I live elsewhere part-time" — one axis of the week in each site, one or two days back at your base.


STEM CURRICULUM — THE 42-HUASTECA MODEL

What the essay says. "Si tuviera que darle un consejo a alguien que esté pensando en qué carrera seguir, sería este: programación" (p. 20). "En países como los nuestros, en donde se requiere un gran crecimiento en infraestructura e innovar en maquinaria y sistemas, los ingenieros son esenciales… necesitaríamos aproximadamente 40 % más de ingenieros" (p. 19). The curriculum operationalizes exactly this.

Design principles (lifted from École 42).

No teachers in the traditional sense; "pisciniers" (coaches) and peer review.

Project-based. Levels / XP. Students grade each other.

Admission by La Piscine — a 4-week bootcamp open to anyone 15+ with no prior requirement.

Free, with a social contract (you give back later).

Core concentrations (launch with 2–3; add over time).

Concentration 1 — Software. Python → web (JS/HTML/CSS) → data → agents/LLM tooling. Market: nearshore remote jobs, direct freelance.

Concentration 2 — Hardware & IoT. Arduino, ESP32, Raspberry Pi, sensors. Market: environmental monitoring, ag-tech, local manufacturing.

Concentration 3 — Digital fabrication. 3D print, CNC, laser, basic electronics. Market: local artisan modernization + maker culture.

Concentration 4 — Data & AI. Statistics, Python data stack, model fine-tuning. Immediate paid work: data-labeling (Scale AI, Surge, Appen), with Nahuatl annotation at premium rates.

Concentration 5 — CAD / mechanical engineering. Fusion 360, SolidWorks via Autodesk Education free licenses. Market: mechanical design, drafting, nearshore engineering firms.

Concentration 6 — Media & content production. Video, audio, graphic design in Nahuatl. Market: cultural artifact pipeline (section below) plus freelance.

Concentration 7 — Finance (full section follows).

Project ideas that are STEM + Nahuatl + community-serving — these double as the fundraising narrative and the real-world portfolio pieces.

IoT water-quality sensors on local arroyos; dashboard in Nahuatl.

A Nahuatl voice assistant — direct line to your existing translator + TTS stack.

Weather stations on milpa fields; yield forecasting from historical climate.

Drone mapping of ejido parcels + GIS land registry.

Health kiosks that run the HemoCue iron screening the sports program needs.

A Nahuatl Minecraft server (and modded Minecraft is a globally proven on-ramp to real programming).

A Nahuatl Mozilla Common Voice dataset contribution — pays dividends for every voice-tech student downstream and is a tangible open-source citizenship line on every student's résumé.

Pedagogical foundation leveraging your history. Your Mozambique LOGO work places you one email from Mitch Resnick's Lifelong Kindergarten group at MIT (Scratch, the direct intellectual descendant of LOGO). Scratch → micro:bit → Python → projects is the pipeline. Resnick is the single most relevant academic ally and he responds to warm intros.


FINANCE TRACK — THE EXPLICIT FIFTH LAYER

What the essay says. "El dinero forma parte de todos los aspectos de nuestra vida, nos guste o no. Conocimientos básicos sobre finanzas y administración son necesarios para infinidad de asuntos" (p. 21). "Sociedades como la judía… discuten y debaten estos conceptos como parte de su discurso jurídico-religioso" (p. 21). "Ser humilde no es ser pobre y ser pobre no significa ser virtuoso" (p. 30). The academy makes this a formal track.

Why Finance is a full track, not an elective.

The marginalized-indigenous → wage-labor pipeline is the default outcome without this layer. With it, students become their own employers, understand the price of their work, and interact with capital (loans, savings, equity, cooperatives) as peers.

The ejido/cargo system is already a cooperative-finance institution. Teaching formal finance alongside the traditional governance structure means students can bridge both — modernizing ejido-level decision-making without destroying it.

Chicano and remittance-economy context: these families are already moving money across borders. Formal literacy converts remittance recipients into remittance investors.

Curriculum outline (year-one scope, roughly 120 hours of study + project work).

Module 1 — Personal money. Budgeting, saving, debt mechanics, remittance flows, inflation, informal lending, tandas/cundinas. Materials in Nahuatl using local market pricing.

Module 2 — Household and small-business accounting. Cash flow for a changarro, a milpa, a seasonal micro-enterprise. QuickBooks / Google Sheets. Taxation basics (SAT RFC, régimen simplificado).

Module 3 — Corporate and ejido finance. How capital structures work. Reading an income statement, balance sheet, cash flow. Cooperative-model finance (ejido, caja popular, SOFIPO). Case: how a cooperative buys shared equipment.

Module 4 — Capital markets. Stocks, bonds, ETFs. CETES Directo (direct Mexican government bond platform open to any Mexican with CURP — accessible from day one). Mexican fintech ecosystem (Nu, Albo, Clip, Bitso).

Module 5 — Entrepreneurship and venture. Business model canvas, lean startup, pitch mechanics. Fundraising paths for a Nahua founder (grants, incubators, impact VC). Case: tracing how a local founder built FEMSA (Mexican reference) and parallel case internationally.

Module 6 — Cross-border finance. Remittance mechanics, FX, international wire, crypto rails for underbanked diaspora. The economics of migration decisions.

Capstone — Every student runs a real portfolio. Minimum MXN $500 (seeded by the academy or earned through data-labeling work) deployed in CETES or a Mexican broker account; monthly reporting required; Nahuatl financial literacy YouTube series produced by the cohort explaining what they are doing.

Materials and partners for Finance track.

Coursera (Fundación Lemann already translated several, as noted in the 2015 essay p. 22) — Introduction to Finance, Business Strategy. Free.

Khan Academy — personal finance series in Spanish; Nahuatl translation pilot via your translator project.

CFA Institute Investment Foundations — free online certificate, globally recognized, first rung for finance careers.

CETES Directo — Mexican government platform; students age 15+ with CURP can open an account.

Instituto Mexicano de Ejecutivos de Finanzas (IMEF) — scholarship / mentorship pathway for standout students.

Your personal network. Your banking career (Hong Kong, New York) is the single asset for this track. Alumni from UBS, Goldman, JP Morgan, Citi — any one of whom can commit to 2 hours/month of remote tutoring for the top finance students. Mexican banking families (Garza, Hank, Larrea extended networks) can be approached for in-country internships.

Teacher pipeline for Finance. The hardest track to staff locally. Three-pronged solution: (1) your personal network for remote tutors; (2) a Comexus Fulbright-García Robles fellow placed as the resident finance teacher; (3) grow-your-own — the top year-3 students become year-4 finance teachers of year-1 students (classic 42-model peer teaching).

Why Finance is also an attitudinal intervention. The 2015 essay (p. 30) explicitly identifies "el preconcepto que se tiene contra el dinero en México" as a central mental block. Teaching finance to Nahua youth in Nahuatl, as a dignified discipline alongside wrestling and software, is itself the counter-cultural act the essay called for.


LANGUAGES — NAHUATL, ENGLISH, MANDARIN

Nahuatl — medium.
English and Mandarin — curricula embedded as modular tracks, not standalone subjects.

Nahuatl — medium of instruction. The essay (p. 17) argued against sustituir el español por el inglés while acknowledging English as lengua franca. Here we go a step further: Nahuatl is the working language of the academy for all pedagogy, documentation, and student output. Spanish is accepted and used — this is not a monolingual institution — but Nahuatl is the default. Rationale: (a) answers directly the essay's p. 32-33 question of whether Nahuatl can carry technical and abstract content; (b) your existing translator + TTS projects make this feasible for the first time; (c) differentiates graduates from every other Mexican tech-trained youth.

English — delivery and partners.

AI tutor (Claude / ChatGPT voice mode) for daily 20-min speaking practice — this intervention was literally impossible 24 months ago and is now the highest-leverage per-dollar language investment available.

Weekly live tutor (remote, VIPKid-style — US / Philippines / South African tutors $8–15/hr).

Annual 3-week intensive camp with native-speaker visitors (Fulbright ETA placement).

Partners. US State Dept English Access Microscholarship Program (explicitly for underserved 13–20 year-olds, $5K–$150K grants); Comexus / Fulbright English Teaching Assistants (place a Fulbright teacher at the academy); British Council; Peace Corps alumni network (Mexico program ended but alumni are responsive).

Mandarin — delivery and partners.

Online tutor pool (ItalKi, Preply — Taiwan-based tutors preferred for less politically-charged exposure).

HSK test prep as the structured ladder (HSK 1 → 6 maps cleanly to proficiency bands).

Annual intensive summer trip (3-week immersion with Taiwan ICDF support — their scholarship fund actively looks for projects like this).

Partners. Taiwan ICDF (direct scholarships for Mandarin learners from LatAm — politically simpler than mainland China Hanban/Confucius Institutes which carry baggage); NTNU International Chinese Language Program (Taipei) for curriculum consult; UNAM Facultad de Estudios Orientales as Mexico-based bridge; COLMEX Centro de Estudios de Asia y África for pedagogy.

Why Mandarin despite the obvious friction. China is the #1 or #2 trading partner of most LatAm countries; CDMX has ~5x more Mandarin learners than a decade ago; Mexico lacks Mandarin-English-Spanish trilinguals. Adding Nahuatl + English + Mandarin makes a graduate functionally globally rare. The essay (p. 17, Lee Kuan Yew / Singapore section) is the direct intellectual precedent: lengua franca for mobility, mother tongue for identity. Here the mother tongue happens to be Nahuatl.

AI as force-multiplier. Pair every student with an LLM-powered conversation partner for daily speaking practice in each target language. This was not possible even two years ago; it is now the single highest-leverage language intervention per dollar in history.


NAHUATL FRAMEWORK & CULTURAL PRODUCTION

Treat students as cultural producers, not consumers.

The 2015 essay (p. 36) warned: "No dejemos que nuestra cultura sea reducida a piezas de museo. Cambiemos." The following outputs are the operational response — students producing in Nahuatl, for external audiences, with measurable reach.

Student outputs — the full artifact pipeline.

Macehualli Podcast — weekly in Nahuatl, distributed via Spotify / Anchor (free hosting). News, elder interviews, music, STEM explained in Nahuatl.

Nahuatl YouTube / TikTok channel — Khan-Academy-style explainers in Nahuatl; viral potential (NativLang on YouTube is the English-language proof-of-concept).

Huiquipedia (Wikipedia in Nahuatl) expansion — formal partnership with Wikimedia México; students earn curriculum credit for sourced edits.

Open-source localization bounty — Firefox, Signal, LibreOffice, Linux desktops into Nahuatl. Mozilla pays for Common Voice; the translation commons work is portfolio gold.

Oral history archive of elders — videotaped, transcribed, published open-access; feeds the TTS and translator training data.

Student-authored Nahuatl children's book series — print + e-book; local sales + regional distribution via SEP indigenous ed.

Short films in Nahuatl — submit to Morelia Film Festival, Sundance Native Lab, imagineNATIVE (Toronto).

Nahuatl TTS voices — released as public dataset; every voice contribution becomes a line item on a student résumé.

Primary artifact goal: external audience metrics. Spotify downloads, Wikipedia edit counts, GitHub stars, Common Voice hours contributed. These are the metrics that convert cultural production from make-work into real motivation and real credentials. Measurement is the discipline — without it, cultural production becomes a hobby and students know it.


SPORTS INTEGRATION

Everything in Sports_Research_Program_Design.md stands. See the full Google Doc at docs.google.com/document/d/1AQ0MttlO8zFa1nDrWGXdDc7IuicQn53P9TcXHMxiNrQ. Age stages (Tlapaloa 12-15, Icuilioa 15-18, Tlahtoa 18-22), sport selection (Wrestling, Boxing, Judo, Weightlifting; distance running + road cycling for highland cohorts), scholar-athlete model, ejido governance, nutrition protocol all carry over.

One integration note worth making explicit: the STEM program feeds the sports program and the sports program feeds the STEM program.

STEM feeds Sports. IoT students build the HemoCue data capture app and anthropometry forms. Data students run the longitudinal analysis for university research partners (the Universidad Veracruzana ask). Film students produce the recruitment and funder-pitch video. English students become the pathway brokers for NCAA correspondence. Finance students manage the scholarship-fund administration and prepare budget reports for CONADE grants.

Sports feeds STEM. Attendance is the single biggest predictor of retention in programs targeting indigenous youth, and the daily training room provides the belonging anchor that keeps students coming to the STEM program the next afternoon. Scholar-athlete model enforces school attendance as prerequisite to sport.

A note on the 2015 essay's absence of sports. The essay did not discuss sport. The Sports_Research work (2026) adds it, with the Clontarf evidence that sport is the single most reliable belonging-anchor for marginalized indigenous youth and that elite-athlete pathways are achievable at low cost. The academy integrates both — if either runs alone, outcomes degrade substantially.


SPACE, EQUIPMENT & CAMPUS STAGING

Phase 0 (months 0–6, cost ~$8–15K USD). No space. Borrow a classroom in an existing telebachillerato or ejido community house 2–3 afternoons/week. Pilot cohort of 20 students. Fully portable: 10 laptops + a projector + a 3D printer + a crate of micro:bits + hand tools.

Phase 1 (months 6–18, cost ~$35–70K USD). Rent 150–250 m² in Huejutla with reliable fiber + grid power. 20 workstations + maker corner (3D printer, laser cutter, basic electronics bench, hand tools, Arduino kits). This single footprint is simultaneously classroom, makerspace, and sports-program medical/screening room.

Phase 2 (months 12–24, cost ~$20–40K USD). Satellite space in Chicontepec or Ixhuatlán — smaller, 1 teacher-coach, same model, lower density.

Phase 3 (year 2–4, cost $300K–1M+). Land purchase for sports campus. Target 5–10 hectares outside Huejutla with road access and water. Phased build: track + combat-sports palapa first, then dorms, then full academic building.

Equipment reality check — the big-ticket items that are hard to source in-country without planning.

3D printers — Prusa or Creality, $300–600 each.

Laser cutter (safety-trained adult use only), $2–5K.

CNC router, $1.5–4K.

Basic electronics inventory, $1–2K.

Twenty refurbished laptops — Dell Latitude 5420 refurb is the sweet spot at $200–400 each. Do not buy new.

Reliable mesh wifi + UPS backup power + Starlink (if fiber unreliable), $2–4K + $150/month.


PARTNERSHIP MATRIX — CURRICULUM

Curriculum / content partners — organized by curriculum area.

STEM pedagogy — École 42 / 42 Foundation (direct campus affiliate conversation; Nicolas Sadirac is the originator). MIT Lifelong Kindergarten (Mitch Resnick) — your Mozambique LOGO history is the warm intro. Harvard CS50 (David Malan) — free, your HGSE alumni status matters. Carnegie Mellon CS Academy — free K-12 CS.

Programming for kids — Code.org, Scratch, Raspberry Pi Foundation Code Clubs. All free, all have Spanish, Nahuatl pilot negotiable.

Hands-on hardware — BBC micro:bit Foundation, free teacher training.

Fabrication — Fab Foundation (MIT), + Fab Lab Xalapa (Universidad Veracruzana already has one — direct relationship).

Finance — CFA Institute Investment Foundations, your personal banking network, IMEF, CETES Directo, Khan Academy personal finance series.

English — US State Dept English Access Microscholarship Program, Comexus / Fulbright ETA, British Council.

Mandarin — Taiwan ICDF, NTNU, UNAM Facultad de Estudios Orientales, COLMEX.

Indigenous NLP — Masakhane community (African indigenous NLP network, directly translatable model), Mozilla Common Voice.

Language revitalization — UNESCO International Decade of Indigenous Languages 2022–2032 (currently active funding window — direct submission possible).

Teacher training — Enseña por México (Teach for All affiliate) — place 2-year corps members.


FUNDING STRATEGY — STAGED

Seed (year 0, ~$150–300K). Self-funding + 1–2 anchor donors from your personal network + Draper Richards Kaplan / Echoing Green fellowship applications. Prove the model with 20 students in borrowed space.

Series A equivalent (year 1–2, ~$500K–1M). Major foundation combination: FEMSA Foundation (Mexico HQ, education + development focus — the single biggest Mexican corporate option), Ford Foundation Mexico (indigenous rights portfolio), Chan Zuckerberg Initiative (education + indigenous languages intersection), IDB Lab (indigenous youth + digital economy). Hardware grants from tech philanthropies (Dell, Microsoft TEALS, Google.org). Sports-specific stack (Nike N7, Laureus Sport for Good) applied in parallel to the STEM stack.

Scale (year 2–5). Corporate partners paying for job pipeline access (the SEO model — companies pay to recruit from the pipeline, which fundraises the pipeline itself). Government money (CONAFE, SEP indigenous education, CONADE / IDERV, Secretaría de Economía digital agenda). Earned revenue — Nahuatl datasets sold to AI companies, consulting, enterprise language training.

Endowment (year 5+). For sports campus land + buildings. Named-gift model drawing on your HGSE + SEO + Mexican diaspora alumni networks.

Tier 1 — multilaterals and big foundations (grant size $50K–$500K+).

FEMSA Foundation — Mexico HQ, education + development focus.

Ford Foundation Mexico — indigenous rights grantmaking.

IDB Lab (BID) — indigenous youth + digital economy.

Inter-American Foundation (IAF) — US government, grassroots LatAm, indigenous specifically. Mandate match is near-perfect.

Chan Zuckerberg Initiative — education + indigenous languages.

Jacobs Foundation (Zurich) — youth development.

Lemelson Foundation — invention education; perfect match for makerspace.

Hewlett Foundation — Mexican education portfolio.

Open Society Foundations — indigenous rights.

Mastercard Foundation — youth employment (Scholars Program may not fit MX but worth asking).

Tier 2 — tech company philanthropies (grants + hardware).

Google.org — indigenous languages, STEM.

Microsoft Philanthropies / TEALS — CS teaching.

Meta Reality Labs — indigenous language preservation program is active.

Amazon Future Engineer.

Apple Community Education Initiative.

Salesforce.org.

Cisco Networking Academy — free networking cert curriculum.

Oracle Education Foundation.

Dell Technologies — hardware donations or deep refurb discounts.

Tier 3 — fellowships (for you personally, early stage).

Draper Richards Kaplan Foundation — 3-year, $300K unrestricted. Exactly your profile.

Echoing Green — $90K + fellowship.

Skoll Foundation — later-stage.

Ashoka — fellowship + global network.

Mulago Foundation Rainer Arnhold Fellows — direct-fit for scalable social enterprises.

Tier 4 — sports-specific (stackable with CONADE/IDERV already in your sports plan).

Nike N7 Fund — explicitly indigenous youth sport in the Americas.

Laureus Sport for Good — Clontarf is a Laureus grantee, direct precedent.

Right to Play.

Beyond Sport.

Peace & Sport (Monaco).

Tier 5 — Mexican corporates.

Fundación Bimbo, Fundación Televisa, Fundación Banorte, Fundación Citibanamex, Fundación BBVA México.

CEMEX, Grupo Modelo.

Coca-Cola Mexico Foundation (politically fraught given the essay's own critique of Coca-Cola on p. 149 of ENSANUT nutrition data, but $$ and Mexico-focused — call separately).


JOB PIPELINE — THE SEO-FOR-NAHUA MODEL

Structure the pipeline in three stages, modeled directly on SEO:

Stage 1 — Opportunity Program. The academy itself. Entry at age 12–15. Daily programming + sport + language. Three-year scholar-athlete track.

Stage 2 — Scholars Program. Placement of top students into feeder institutions: UVI (Universidad Veracruzana Intercultural), UAEH, Prepa Yankuikej, boarding scholarships like PASE, international summer programs. Age 15–18.

Stage 3 — Career Program. Direct internships + full-time offers with corporate partners. Age 18–22. This is where SEO's genius lies — the corporate partner commitment IS the fundraising mechanism.

SEO Letters (SEO Latin America) is your direct ask as alum. Pathway for 1–2 students/year into their program; co-brand a "Nahua Scholars" cohort.

Direct SEO parallels and feeder programs.

SEO Letters (SEO Latin America) — direct alum ask.

QuestBridge — US college match for low-income students.

Posse Foundation — cohort-based college placement.

Fundación México en Harvard — Mexican alumni + scholarships.

Comexus / Fulbright-García Robles — graduate school pathway.

Rhodes Scholarship Mexico — elite long-tail.

Fundación Beca, Fundación Jenkins — Mexican scholarship funds.

Tech bootcamps with job placement (LatAm presence).

Henry — LatAm bootcamp with ISA, Mexico presence.

Platzi — Mexican online learning, strong placement network.

Microverse — remote dev training with income-share, global network.

Laboratoria — women in tech bootcamp with job placement, Mexico presence.

Nearshore IT shops (junior dev hire pipeline).

Wizeline, Globant, Encora, EPAM Mexico. All actively hiring juniors.

IBM Mexico, Microsoft Mexico, Google Mexico, Oracle Mexico.

Mexican tech scale-ups (internship + hire pipeline).

Kavak, Clip, Clara, Bitso, Konfio, Jüsto, Belvo, Kueski, Albo.

Immediate paid work (available to students in training).

Scale AI, Surge AI, Appen — data labeling. Nahuatl annotation at premium rates. Students can earn income from year 1 of program while still training.

Toptal, Deel-managed remote work — freelance market for seniors.


LEVERAGING YOUR BACKGROUND — CONCRETE ASKS THIS QUARTER

These are warm introductions available to you specifically that most founders in this space would not have.

Mitch Resnick (MIT Lifelong Kindergarten). "I ran a LOGO-based program in Mozambique in 2008. Building the next-generation version with indigenous Mexican youth, want to use Scratch as pedagogical spine." Likely yes to a letter of support and name on the advisory board.

Fernando Reimers (Harvard GSE Global Education). Direct cold email about the project — he actively advocates for exactly this profile and is Mexican. Ask for three funder introductions.

SEO Letters office. Alumni ask — "Would SEO consider a formal pipeline partnership with a Nahua academy I'm founding?"

Harvard DRCLAS Mexico office. Grants + visibility + Harvard student fellows for summer research.

Fundación México en Harvard. Seat at their table as a founder; direct scholarship pipeline for your students.

École 42 / 42 Foundation. Direct campus-affiliate conversation.

IAF (Inter-American Foundation) Mexico program officer. Their mandate is literally this.

UNESCO Decade of Indigenous Languages secretariat. Register the project; opens doors to parallel initiatives.

MATT (Mexicans and Americans Thinking Together) — the chicano-deportado talent network referenced in your 2015 essay (p. 35). Direct partnership for teacher pipeline — bilingual deportees already in Mexico who need meaningful work.

Your AZlera / Project Ocean / Chiapas essay-competition history is the fundraising asset. "I did this at smaller scale in Mozambique and Chiapas; this is the scaled version at home" is the lede of every pitch.


RISKS & OPEN QUESTIONS

Risk — Teacher and coach pipeline is the single hardest bottleneck.
Mitigation. Enseña por México corps + Fulbright ETA + remote tutors + grow-your-own (older students teach younger). Budget for 2 full-time hires minimum year 1. MATT chicano/deportado talent pool is the under-exploited source.

Risk — Brain drain, where best students leave the community permanently.
Mitigation. Explicit "return home" track in the SEO-style career program; remote-work pipeline so graduates can work globally while staying physically rooted. The 2015 essay (p. 12) explicitly says "para otros, que ya han acumulado algunos recursos y conocimiento, puede que sea la hora de regresar" — build the regresar loop into the program design, not left as an afterthought.

Risk — Nutrition / stunting undercuts both STEM cognition and sports performance.
Mitigation. The Sports_Research protocol (iron screening, deworming, quelites restoration) already addresses this. Must integrate full breakfast + lunch program. DIF / BIENESTAR partnership. Nutrition is non-negotiable.

Risk — Political fragility — Confucius Institutes, foreign funding sensitivities.
Mitigation. Default Taiwan over PRC for Mandarin. US gov money (English Access, IAF) is less fraught than it looks. Keep a Mexican AC (Asociación Civil) entity as the legal face of all operations.

Risk — Scope sprawl kills ambition. This is your AZlera lesson.
Mitigation. Launch with ONE cohort, TWO sports, TWO STEM concentrations, Nahuatl immersion. Earn the right to expand. No new verticals until the first cohort finishes year 1.

Risk — Safeguarding and child protection in a semi-residential model.
Mitigation. Build this into Phase 1, not Phase 3. Clontarf has model policies that can be adopted directly.

Risk — Internet reliability in Huasteca.
Mitigation. Starlink as backup from day one. Design curriculum to be offline-capable; sync when possible.

Open questions to resolve before Phase 1 launch.

Target first-cohort size — my guess: 25–30.

Gender target — Clontarf is boys-only; HCZ is co-ed. The 2015 essay (p. 25-27) argued forcefully for women. Co-ed with explicit girl-recruitment quota is the recommended default.

Age range for cohort 1 — the sports plan has 12–22. Is the STEM cohort the same ages, or a tighter band?

Recruited vs. community-open — SEO is merit-selected; HCZ is geographic cohort. Totally different programs. The academy's answer sets its entire character.

Spanish-literacy baseline for cohort 1 — determines how aggressive Nahuatl-primary instruction can be in week 1.

Who is the person on the ground when you are not there — the single biggest hire. Mexican founder or expat / returnee? Dual national ideal.


APPENDIX A — CROSSWALK: 2015 ESSAY → 2026 CURRICULUM

What the essay says — Three premises (pp. 7-12). (1) Innate creativity is the tool. (2) Even the smallest can impact; even the largest can be challenged. (3) Economic power is a means of enormous help.
What the curriculum does. Project-based learning puts creative problem-solving at the center. The Finance track and the entire "no permission needed, build it yourself" ethos operationalize premises 2 and 3.

What the essay says — "Aprendizaje: hoy y siempre" (p. 14). Education is the lever; Global Creativity Index tier correlates with GDP per capita.
What the curriculum does. The academy is an education-first institution with explicit metrics tied to the GCI's three T's (talent, technology, tolerancia).

What the essay says — "Inglés" (pp. 16-18). English as lengua franca; Lee Kuan Yew / Singapore model; mother tongue retained alongside.
What the curriculum does. English as embedded modular track with AI tutoring + Fulbright ETA + English Access grants. Nahuatl retained as medium (going further than the essay by using indigenous language as working language, not just preserved as heritage).

What the essay says — "Ciencias" and "Ingeniería y diseño" (pp. 18-20). Khan Academy, Coursera, MIT OCW; need for more engineers, especially programmers; Obama's Hour of Code.
What the curriculum does. 42-Huasteca peer-learning model with all 6 STEM concentrations grounded in exactly these free resources, extended with the 2026 LLM-era tooling the essay could not anticipate.

What the essay says — "Finanzas y conocimientos de negocios" (pp. 21-22). Finance is daily-life literacy; Jewish community reference; Carlos Slim as early-finance exposure example; Coursera + Lemann Foundation materials.
What the curriculum does. Finance is a full seven-module track with a real-money capstone, grounded in CETES Directo, Khan Academy, Coursera (per the essay's own recommendations), and your personal banking network as remote tutor pool.

What the essay says — "Los niños" (pp. 22-24). Brain development curves; early childhood is formative; 27M Mexicans in 0-11 age range are the latent asset.
What the curriculum does. Core cohort is 12–22 (sports plan boundary). Opens Phase 4 question — does the academy add a 5–11 or 0–5 early-childhood arm later? Recommended: year 3 add a Zero-to-Five Nahuatl immersion pre-K using the Vroom-style parent-coaching model the essay cites (p. 24).

What the essay says — "Las mujeres" (pp. 25-27). 51.6% of population; women crucial; Bill Gates "half the talent"; Lean In circles; mother's education most-predicts child's.
What the curriculum does. Co-ed with explicit girl-recruitment quota and dedicated Lean In circles for every cohort. Opens question of boys-only sport (Clontarf) vs. integrated. Recommendation: integrated with parallel girls-only training groups within the same academy, not segregated institutions.

What the essay says — "Confianza y humildad" + "Ser humilde no es ser pobre" (pp. 29-31). Attitudinal foundations; abandon the diminutive and "ojalá/aunque sea/hubiera"; dinero is not sucio.
What the curriculum does. These are the character-formation layer and belong to the daily culture of the institution, not a separate module. Explicit language norms (Nahuatl high register, no diminutive excess in Spanish, confidence drills in English and Mandarin presentation). Finance track directly rebuts the dinero-sucio preconception.

What the essay says — "Ninguna cultura es inferior" + "Estemos abiertos a la innovación" (pp. 31-35). Nahuatl potentially rich for technical/abstract content; look to India, Singapore, Korea, Brazil for models; chicano / deportado / afromexicano / LGBTQ communities as untapped talent.
What the curriculum does. Nahuatl as working language proves the first claim. International partner matrix (section above) looks to India (Infosys/Satyam reference per essay), Singapore (Lee Kuan Yew model), Taiwan, Brazil (Fundación Lemann already cited). MATT and chicano/deportado teacher pipeline operationalize the second.

What the essay says — "Acerca de la confianza: trabajemos juntos" (pp. 36-37). Chinese immigrant lending-network model; social trust as prerequisite for collective action.
What the curriculum does. Cohort-based pedagogy at every level (42-model peer review, Lean In circles, ejido-model student governance from the sports plan). Trust is built structurally, not exhorted.

What the essay says — "El negativismo o la crítica… solo una actitud positiva nos puede dar una salida" (pp. 38-39). Mexico-US proximity reframed as asset not curse; Modi Madison Square Garden speech as model.
What the curriculum does. The entire SEO-for-Nahua Career Program is the operational answer. Direct feeder relationships into US and global institutions, with explicit return-home loop so proximity becomes brain-circulation, not brain-drain.


APPENDIX B — SUGGESTED NEXT STEPS (30 / 60 / 90 DAYS)

30 days.
— Legal entity: incorporate the Mexican Asociación Civil.
— Send the eight warm-intro emails listed in "Leveraging your background."
— Decide on primary cohort gender target and age range.
— Decide on dual-site vs. single-site launch.
— Hire the ground person (single most important hire).

60 days.
— Site visit to Huejutla + Chicontepec + Ixhuatlán (if not already done); meet 3 ejido assemblies, 2 telebachilleratos, 1 UAEH extension office.
— Finalize Phase 0 budget sheet.
— Submit UNESCO Decade of Indigenous Languages registration.
— File English Access Microscholarship Program grant application.
— First concept-note (2-page) ready to send to funders.

90 days.
— Open applications for first cohort of 20–30 students (Piscine model — no prerequisite).
— Secure Phase 0 borrowed space.
— Confirm first two STEM concentrations and first two sports.
— Order Phase 0 equipment ($8–15K).
— Public launch event in Nahuatl at an ejido assembly in Chicontepec or Huejutla.


REFERENCES

Books.
Sánchez, W. "¿Y si nos dejáramos de quejar? Tendríamos que educarnos." 2015. (Foundational manifesto for this project.)
Oppenheimer, A. "¡Basta de historias!" Random House Mondadori, 2010.
Lee, Kuan Yew. "From Third World to First: The Singapore Story." HarperCollins, 2000.
Lee, Kuan Yew. "Hard Truths to Keep Singapore Going." Straits Times Press, 2011.
Sandberg, S. "Lean In." Random House, 2013.
Diamond, J. "The World Until Yesterday." Penguin Books, 2012.
Mill, J. S. "On Liberty." Penguin Classics, 1988.
Marchand, H. "Apuesta México." horaciomarchand.com, 2014.
Castañeda, C. "Las Enseñanzas de Don Juan." University of California Press, 1968.

Programs and institutions cited.
École 42 (Paris) — 42.fr
Harlem Children's Zone — hcz.org
Clontarf Foundation (Australia) — clontarf.org.au
MIT Lifelong Kindergarten / Scratch — scratch.mit.edu
Harvard CS50 — cs50.harvard.edu
Code.org, Khan Academy, Coursera, MIT OCW, freeCodeCamp
Raspberry Pi Foundation Code Clubs
BBC micro:bit Educational Foundation
Fab Foundation (MIT Fab Lab network)
US State Dept English Access Microscholarship Program
Comexus / Fulbright-García Robles — comexus.org.mx
Taiwan ICDF — icdf.org.tw
Mozilla Common Voice — commonvoice.mozilla.org
Masakhane (African NLP) — masakhane.io
UNESCO International Decade of Indigenous Languages 2022–2032
SEO Letters (SEO Latin America) — seoletters.org
QuestBridge, Posse Foundation
MATT (Mexicans and Americans Thinking Together) — matt.org
Henry, Platzi, Microverse, Laboratoria
CETES Directo — cetesdirecto.com
CFA Institute Investment Foundations

Benchmarks and sister references.
Macehualtlahtol Sports_Research_Program_Design.md — docs.google.com/document/d/1AQ0MttlO8zFa1nDrWGXdDc7IuicQn53P9TcXHMxiNrQ
Plan Ceibal (Uruguay)
AISES (American Indian Science and Engineering Society)
First Voices (Canada) — firstvoices.com
Rising Voices (Global Voices program) — rising.globalvoices.org
Universidad Veracruzana Intercultural (UVI)

Mexican context.
CONADE / IDERV (Veracruz) / CODEH (Hidalgo)
SEP indigenous education
CONAFE
Fundación FEMSA, Fundación Televisa, Fundación Banorte, Fundación Citibanamex, Fundación BBVA México
Fundación Lemann (Brazil — translation partner cited in 2015 essay)

End of document. Working file; revise freely.
"""

# ── create doc if DOC_ID is None ──────────────────────────────────────────────

if DOC_ID is None:
    with open(TOKEN_PATH) as f:
        tok = json.load(f)
    oauth_creds = OAuthCreds(
        token=tok['token'], refresh_token=tok['refresh_token'],
        token_uri=tok['token_uri'], client_id=tok['client_id'],
        client_secret=tok['client_secret'], scopes=tok['scopes'],
    )
    if oauth_creds.expired and oauth_creds.refresh_token:
        oauth_creds.refresh(Request())
    user_drive = build('drive', 'v3', credentials=oauth_creds)
    created = user_drive.files().create(
        body={
            'name': 'Tlamachiyotl Academy — Curriculum & Pipeline Brainstorm v0',
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [FOLDER_ID],
        },
        fields='id, parents',
        supportsAllDrives=True,
    ).execute()
    DOC_ID = created['id']
    print(f'Created: https://docs.google.com/document/d/{DOC_ID}/edit')
    print(f'Parents: {created.get("parents")}')
    user_drive.permissions().create(
        fileId=DOC_ID,
        body={'type': 'user', 'role': 'writer', 'emailAddress': SA_EMAIL},
    ).execute()
    print(f'Shared with service account: {SA_EMAIL}')
else:
    print(f'Updating: https://docs.google.com/document/d/{DOC_ID}/edit')


# ── helpers ────────────────────────────────────────────────────────────────────

def para_text(element):
    para = element.get('paragraph', {})
    return ''.join(
        r.get('textRun', {}).get('content', '')
        for r in para.get('elements', [])
    ).strip()

def batch(service, doc_id, reqs):
    if reqs:
        service.documents().batchUpdate(
            documentId=doc_id, body={'requests': reqs}
        ).execute()


# ── phase 1: clear + insert content ───────────────────────────────────────────

doc = docs_service.documents().get(documentId=DOC_ID).execute()
body_content = doc.get('body', {}).get('content', [])
end_index = body_content[-1].get('endIndex', 1) if body_content else 1

reqs = []
if end_index > 2:
    reqs.append({'deleteContentRange': {'range': {'startIndex': 1, 'endIndex': end_index - 1}}})
reqs.append({'insertText': {'location': {'index': 1}, 'text': CONTENT}})
batch(docs_service, DOC_ID, reqs)
print('Phase 1: content inserted')


# ── phase 2: apply heading styles ─────────────────────────────────────────────

doc = docs_service.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])

style_reqs = []
for element in body:
    para = element.get('paragraph')
    if not para:
        continue
    text  = para_text(element)
    start = element.get('startIndex', 0)
    end   = element.get('endIndex', 0)

    if text == TITLE_LINE:
        style_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': 'HEADING_1'},
            'fields': 'namedStyleType',
        }})
    elif text == TOC_HEADER or text in SECTIONS:
        style_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': 'HEADING_2'},
            'fields': 'namedStyleType',
        }})
    elif any(text.startswith(p) for p in HEADING_3_PREFIXES):
        style_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': 'HEADING_3'},
            'fields': 'namedStyleType',
        }})

batch(docs_service, DOC_ID, style_reqs)
print(f'Phase 2: {len(style_reqs)} heading styles applied')


# ── phase 3: pageBreakBefore + collect headingIds ─────────────────────────────

doc = docs_service.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])

seen_texts       = set()
page_break_reqs  = []
heading_id_map   = {}
toc_entry_ranges = {}

for element in body:
    para = element.get('paragraph', {})
    style = para.get('paragraphStyle', {})
    named = style.get('namedStyleType', '')
    heading_id = style.get('headingId')
    text  = para_text(element)
    start = element.get('startIndex', 0)
    end   = element.get('endIndex', 0)

    if named != 'HEADING_2':
        continue

    if text == TOC_HEADER:
        page_break_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'pageBreakBefore': True},
            'fields': 'pageBreakBefore',
        }})
        continue

    if text in SECTIONS:
        if text not in seen_texts:
            toc_entry_ranges[text] = (start, end)
            seen_texts.add(text)
        else:
            page_break_reqs.append({'updateParagraphStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'paragraphStyle': {'pageBreakBefore': True},
                'fields': 'pageBreakBefore',
            }})
            if heading_id:
                heading_id_map[text] = heading_id

batch(docs_service, DOC_ID, page_break_reqs)
print(f'Phase 3: pageBreakBefore applied to {len(page_break_reqs)} headings')
print(f'         headingIds collected: {len(heading_id_map)} / {len(SECTIONS)}')


# ── phase 4: hyperlink TOC entries ────────────────────────────────────────────

link_reqs = []
BLUE = {'red': 0.07, 'green': 0.33, 'blue': 0.80}

for section in SECTIONS:
    if section not in toc_entry_ranges or section not in heading_id_map:
        continue
    start, end = toc_entry_ranges[section]
    hid = heading_id_map[section]
    link_reqs.append({'updateTextStyle': {
        'range': {'startIndex': start, 'endIndex': end - 1},
        'textStyle': {
            'link': {'headingId': hid},
            'underline': True,
            'foregroundColor': {'color': {'rgbColor': BLUE}},
        },
        'fields': 'link,underline,foregroundColor',
    }})

batch(docs_service, DOC_ID, link_reqs)
print(f'Phase 4: {len(link_reqs)} TOC hyperlinks applied')

print(f'\nDONE — https://docs.google.com/document/d/{DOC_ID}/edit')
