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
body_content = doc.get('body', {}).get('content', [])
end_index = body_content[-1]['endIndex'] - 1

# ── Build text content ──────────────────────────────────────────────────────
# Each entry: (text_string, style)
# style: None | 'H1' | 'H3' | 'BOLD_LABEL'
ENTRIES = [

("SITE ANALYSIS — POPULATION, COSTS & OPERATIONAL MODEL", "H1"),
("""

INEGI 2020 Census: Both Sites Compared""", "H3"),
("""

Huejutla de Reyes (Hidalgo) — HQ
  Total population: 122,905
  Nahuatl speakers: ~62,000 (51% of total)
  Cabecera (municipal seat): ~38,000 inhabitants (31%)
  Remaining localities: 200+ rural communities, most under 2,500 people
  CONEVAL marginalization index: High
  Household internet penetration: ~25–30%
  Infrastructure: Hospital-grade medical, UAEH extension campus, fiber internet, banking, highway access

Chicontepec de Tejeda (Veracruz) — Satellite
  Total population: 50,129
  Nahuatl speakers: ~35,000 (70% of total — higher indigenous density than Huejutla)
  Cabecera (municipal seat): ~6,500 inhabitants (13%)
  Localities: 320–350 dispersed communities across Sierra terrain, many without paved road access
  CONEVAL marginalization index: Very High (one step above Huejutla)
  Household internet penetration: ~10–15%
  Constraint: Weak internet, no clinic-grade medical, limited supplier access

Key finding: Chicontepec has higher Nahuatl-speaker density (70% vs 51%) but extreme geographic dispersion. Huejutla has the infrastructure. Neither alone satisfies both the immersion goal and the operational requirements.

""", None),

("Why Dual-Site Is Expensive", "H3"),
("""
Huejutla–Chicontepec road distance: ~80 km through Sierra Huasteca terrain — 2.5–4 hours in dry season; blocked or impassable during rainy season (June–October) due to landslides. No reliable direct transit; most trips require a transfer and effectively take a full day round-trip.

Annual dual-site overhead above a single-site model:
  Vehicle transport / rotation:         $2,400–4,200/year
  Second facilitator salary:            $3,600–6,000/year
  Equipment duplication (one-time):     $2,000–4,000
  Second facility rental:               $1,200–3,000/year
  Total added cost:                     ~$9–17K/year above single-site

Budget validation: The doc's Phase 1 ($10–20K setup, Huejutla only) is tight but achievable. Phase 2 ($20–40K satellite) is credible at $25–35K if a vehicle is included; $20K only works with donated space.

""", None),

("Recommended Alternative: Mobile Unit", "H3"),
("""
A used van ($8–10K) + outfitting ($3–5K) + annual fuel/maintenance ($2–3K) = $12–18K total for Phase 2 access to the Chicontepec zone. Eliminates the second facility cost entirely. Accepts higher vehicle maintenance exposure on sierra roads. This compresses Phase 2 cost by $8–20K vs a fixed satellite.

Precedent: CESDER (Centro de Estudios para el Desarrollo Rural, Puebla Sierra Norte) ran a mobile extension team model into Nahuatl communities for decades. The model works in this terrain and with this population.

Decision point: If the connectivity issue at Chicontepec improves (CFE Telecomunicaciones / Internet para Todos expansion in Veracruz), revisit a fixed satellite in Year 2–3. In Year 1, the mobile unit is the right call.

""", None),

("STUDENT DIGITAL INCOME PIPELINE", "H1"),
("""
Constraints applied: income earned by students directly, digital only, 100% private sector, no government programs. Students are the earners — not families. Scalability is the primary criterion.

""", None),

("Structural Unlock: Academy as Data Cooperative", "H3"),
("""
The academy registers as an asociación civil or data cooperative, holds platform accounts, contracts with AI companies as a B2B vendor, assigns tasks to students, distributes stipends. This removes the 18+ age floor (the contract is institutional, not individual), creates a formal auditable financial relationship, and scales with student count. The cooperative and the academy should be distinct legal entities for tax, liability, and grant-eligibility reasons.

Operational model: Karya (India) — rural AI data cooperative, mobile-first, low-connectivity design, school as intermediary. Students and community members earn from voice/text data work. Direct outreach to Karya for Mexico expansion or franchise partnership is the highest-leverage near-term action.

""", None),

("Tier 1 — Year 1: Nahuatl Voice Corpus Sales", "H3"),
("""
Nahuatl Huasteco has genuine scarcity value for LLM training. It appears on the priority low-resource language lists of Meta MMS (Massively Multilingual Speech) and Google USM (Universal Speech Model). No standing commercial Nahuatl Huasteco audio dataset exists — the market is open.

Revenue model:
  Recording session (10 students, 5 hours clean audio): $250–$2,500 per corpus sale to AI data companies (Appen, iMerit, Defined.ai, LDC)
  Standing voice collection contract via university partner: $50–150/student/month
  One hour of labeled audio from multiple speakers: $50–500 depending on quality and buyer rarity premium

Connectivity advantage: Recording is offline-capable. Students record locally; data syncs during Huejutla days. Strong fit for Chicontepec's limited connectivity.

No age floor for voice recording with parental consent. School as data controller simplifies the legal structure and consent process.

Path to standing contract: Partner with Universidad Veracruzana's Nahuatl linguistics program to apply for an NSF DEL (Documenting Endangered Languages) or LDC corpus grant. Grant funds flow to the academy cooperative as institutional payment. Lead time: 6–18 months. This is also the second funding track for the academy (research track, independent of program grants).

""", None),

("Tier 2 — Month 12: AI Data Labeling via School Cooperative", "H3"),
("""
Academy cooperative registers as a B2B vendor with Remotasks (Scale AI) or TELUS AI (formerly Lionbridge Smart Crowd). Students do text annotation, translation quality review, bilingual Spanish/Nahuatl tasks. Nahuatl-specific annotation tasks do not currently exist on these platforms — this is a gap and a premium opportunity.

Earnings: $80–200/student/month at 10 hours/week. Remotasks and TELUS AI pay via PayPal/Payoneer, both accessible in Mexico via OXXO.
Connectivity: 4G minimum for upload; text-only tasks workable on intermittent connection.
Profile: Outlier.ai (Scale AI subsidiary) specializes in language generation rating and translation quality tasks — directly relevant for bilingual Nahuatl-Spanish students.

""", None),

("Tier 3 — Month 18–36: Nahuatl Content Channel", "H3"),
("""
School entity holds the TikTok/YouTube account. Students produce Nahuatl-language content: language lessons, cultural knowledge, STEM explainers in Nahuatl, traditional ecological knowledge. The algorithm boosts genuinely rare-language content — Nahuatl TikTok creators have documented 100K–500K follower counts (documented by Rest of World and Vice, 2023–24). This is not competing in a crowded content space.

Revenue:
  Ad revenue: modest ($100–400/month at 100K views; Mexico CPM $1–4)
  Sponsorships: cultural orgs, universities, NGOs, language-learning platforms pay $200–2,000/video
  Total at 100K+ followers with 2–3 sponsorships/month: $500–$3,000/month into the cooperative

Revenue is held at the school/cooperative entity level and distributed as student stipends. Video upload requires broadband at Huejutla; recording is offline.

""", None),

("VENTURE BUILDER — SEPARATE ENTITY", "H1"),
("""
Many businesses the PE fund would want to invest in the Huasteca do not yet exist or are not investment-ready. The venture builder arm incubates them. Venture builder and PE fund are separate legal entities with a defined equity handoff mechanism. This separation is essential for LP confidence, regulatory clarity, and founder trust.

""", None),

("Recommended Structure: Blended Finance Tranche", "H3"),
("""
Builder phase funded by concessional capital (IDB Lab, Ford Foundation Mexico, GIZ Mexico, Christensen Fund). Fund deploys commercial capital once a portfolio company hits agreed investability criteria (revenue threshold, unit economics, team composition). This cleanly separates concessional and commercial risk — the key structural innovation that makes the model work for impact LPs and commercial LPs simultaneously.

Precedent: IDB Lab (Inter-American Development Bank's innovation lab) and FOMIN have financed several LatAm venture builders using exactly this structure.

Key structural safeguards:
  Separate investment committees for builder and fund (avoid GP conflict of interest)
  Builder equity stake: 15–25% for co-founding; 10–15% for service-only support
  Fund right of first refusal (ROFR) at a valuation cap of 3–5x builder's entry valuation
  Founder equity floor: must not fall below 51% post-builder stake (maintains entrepreneurial control; avoids cooperative misclassification under Mexican law)

""", None),

("Priority Sectors for Huasteca Venture Building", "H3"),
("""
High-readiness (proven models exist, adaptation needed):
  Specialty food processing — Veracruz is a vanilla and chili-producing zone. Value-add processing cooperatives with direct export channels are fundable. Model: Root Capital / Café Mujer (Oaxaca indigenous coffee cooperatives).
  Eco- and cultural tourism — turismo comunitario with Nahuatl-language cultural experiences (cooking, temazcal, textile). Premium international pricing. Model: Pueblos Mancomunados (Oaxaca).
  Artisan e-commerce — aggregating Huastec embroidery artisans into export cooperatives with digital storefronts. Model: Taller Maya (Yucatan), Novica/National Geographic partnership.

Medium-readiness (18–36 month incubation):
  Agritech for smallholders — soil monitoring, weather alerts, input financing via mobile. Model: Agromovilidad (Mexico).
  Nahuatl/language tech — Nahuatl keyboard, educational app, translation services for compliance. Small market but high strategic value for community trust and grant eligibility.
  Rural fintech / tanda digitization — digitizing rotating savings (tanda) for indigenous communities. Model: Kichink / Tanda app (Mexico).

Longer-term (3–5 year incubation):
  Healthcare logistics, mini-grid renewable energy, construction materials from local inputs.

""", None),

("Entrepreneur-in-Residence Sourcing", "H3"),
("""
For remote indigenous contexts, diaspora EIRs outperform external hires on community legitimacy. Target: Huasteca diaspora in Mexico City, Monterrey, Houston, Chicago — people who want to return. Provide a 12–18 month salary bridge (~MXN 20–30K/month) and pair with a local community co-founder who holds the community relationship. The external EIR brings capital access, digital skills, and networks; the local co-founder brings trust and knowledge.

Cost structure (lean builder, 3–5 portfolio companies):
  Annual operating budget: $1–2M
  Core team (4–6 FTEs — MD, sector leads, CFO, community liaison): $400–700K/year
  Per-company direct support: $150–300K/company/year
  Overhead (travel, tech, office): $100–200K/year
  Incubation period to fund investability: 18–36 months (longer than urban builders due to trust-building)

Grant sources for builder phase: IDB Lab, GIZ Mexico, Ford Foundation Mexico City office, SEFOPI (successor to INADEM), Christensen Fund, NSF/National Endowment for the Humanities (cultural/language programs).

""", None),

("TALENT RECRUITMENT PIPELINE", "H1"),
("""
Three tracks: short-term volunteers, paid fellows, diaspora returnees and EIRs.

""", None),

("Track 1 — Short-Term Volunteers (2–3 months)", "H3"),
("""
  AIESEC en México: Fastest to activate. No cost to academy. Places 18–30-year-old international volunteers in teaching, tech coaching, and entrepreneurship mentoring roles. Standard MOU process. Website: aiesec.org.mx
  ISF México (Ingenieros Sin Fronteras): Engineering volunteer teams for technical projects. Chapter-based; Hidalgo chapter active. Skills: water, energy, civil. Website: isf.org.mx
  UN Volunteers Online: Remote specialists (curriculum design, data analysis, research) if academy achieves UN partner status through UNDP Mexico. Free with UN affiliation. Website: onlinevolunteering.org
  Catchafire: Remote pro-bono specialists for bounded projects (financial model, curriculum framework, website). Subscription ~USD 2,500–5,000/year for unlimited project posts. Website: catchafire.org

""", None),

("Track 2 — Paid Fellows (1–2 Years)", "H3"),
("""
  Enseña por México (Teach For All affiliate): Two-year teaching fellowship. Stipend ~MXN 5,000–8,000/month plus social security. Has placed fellows in Veracruz and Hidalgo. Formal MOU partnership agreement required but standard process. Website: ensenapormexico.org
  Codeando México: Civic-tech fellowship. Paid (~MXN 10,000–15,000/month). Has worked in indigenous data-sovereignty contexts. Approach via project proposal. Website: codeandomexico.org
  Acumen Fellows (Latin America cohort): Develops your own existing mid-career staff (5–15 years experience). Acumen covers program costs; academy pays the fellow's salary. Nomination-based. Website: acumenacademy.org

""", None),

("Track 3 — Diaspora EIRs and Mentors", "H3"),
("""
  Red de Talentos Mexicanos: Free directory of Mexican professionals abroad managed by Secretaría de Relaciones Exteriores. Low-barrier posting for EIR or mentor roles.
  MATT Foundation (Mexicans & Americans Thinking Together): Small org specifically connecting Mexican diaspora with Mexico-based social projects. Direct contact. Website: mattfoundation.org
  LinkedIn targeted outreach: Most effective channel for EIR recruiting. Target Mexican professionals in Texas, California, and Illinois with Nahuatl/Huasteca family ties.
  Sistema B México entrepreneur network: B Corp-certified social enterprises. Source of mission-aligned EIRs who may relocate for an equity opportunity.

Note: WorkAbroad.ph is a Philippines-based overseas worker job board for construction/hospitality roles. Not relevant to this context.

""", None),

("FROM MOZAMBIQUE TO HUASTECA — AZLERA LESSONS", "H1"),
("""
AZLera (Project Ocean, Ilha de Moçambique, 2010–2016+) was a community education project serving ~17,000 people on a small island off the Mozambique coast, founded and led by the same founder. It is the operational proof-of-concept for Tlamachiyotl. The following lessons transfer directly.

""", None),

("What Worked — Direct Transfers", "H3"),
("""
Local manager model (Saide Coman): Empowering a mature, committed local project manager reduced operational burden dramatically and increased community trust. The strategy doc explicitly identifies this as the key operational unlock for AZLera's sustainability. Transfer: Identify and develop a Nahuatl-speaking local manager from within the Huejutla/Chicontepec community as the primary operational lead. Compensate well. Train annually at an external institution (AZLera brought Coman to Brazil for training at TCP/Plug). Budget for this from Day 1.

Volunteer flow: AZLera received 1–2 unsolicited volunteer inquiries per week without active recruitment. Structuring a 2–3 month short-term volunteer track (with lodging coordination, no financial guarantee) creates a renewable workforce at near-zero recruiting cost. Transfer: Tlamachiyotl should build the same structured short-term volunteer program from Year 1. A small volunteer contribution ($150–300/month toward housing and materials) is reasonable — AZLera explored this and found it viable at $100–200/month.

Community anchor: On the island, Project Ocean had strong core attendance and was actively sought by children and adults. It was the only alternative for 17,000 people. Transfer: Design Tlamachiyotl for the Chicontepec zone where no comparable program exists — not as a competitor to established programs but as the only option of its kind.

Revenue ideas that transfer: AZLera considered an Etsy shop for Mozambican products. The artisan e-commerce track in the venture builder pipeline is the scaled, institutional version of the same idea.

""", None),

("What to Avoid — Direct Warnings", "H3"),
("""
Bolsista program complexity: AZLera's scholarship-student (bolsista) program created financial strain — it amplified cash needs, made budgets unpredictable, and raised selection quality questions. The "Mozambique family incentive" dynamic the founder referenced was essentially this bolsista mechanism: it worked in principle but was expensive and operationally difficult to manage. Do NOT replicate the bolsista model directly. The student digital income pipeline (Nahuatl voice corpus, AI labeling cooperative) achieves the same family-incentive goal through private-sector digital income rather than scholarship transfers — more scalable, more sustainable, and no government dependency.

Operational centralization: AZLera was too dependent on the founding team's time for operational decisions. Transfer warning: Tlamachiyotl's operating structure must be local-first from Day 1. The local manager leads; the founder is board-level, not operational.

Underfunded local compensation: AZLera's strategy doc explicitly identified the need to increase Coman's salary and hire additional support staff. Transfer: Budget competitive local compensation from the outset, not as an afterthought.

""", None),

("Narrative Connection", "H3"),
("""
AZLera is the founder's 15-year proof-of-concept for community education in a resource-constrained indigenous/remote setting. Tlamachiyotl is the scaled, institutionalized version with a financial sustainability model that AZLera lacked. The PE fund and venture builder provide the missing commercial infrastructure. This arc — from volunteer-driven NGO (AZLera) to institutional ecosystem (Tlamachiyotl + fund + builder) — is the founder's story and the fund's investment thesis in one narrative.

""", None),

("EARLY CHILDHOOD ANCHOR — TALKLET CONNECTION", "H1"),
("""
Talklet (co-founded by Wilbert Sanchez and Lulu Dubin, circa 2016–2018) was a cloud-connected children's wearable device that recorded and analyzed parent-child speech in the 0–5 age window, providing quality and quantity metrics to parents. Tagline: "The Fitbit for Words."

Scientific foundation of Talklet — directly relevant to Tlamachiyotl:
  90% of brain development occurs by age 5
  Quantity and quality of speech heard in the 0–5 window profoundly impacts IQ, school performance, self-esteem, and life success
  The "30 million word gap" between high- and low-income households is the strongest predictor of school readiness
  Bilingual/indigenous families face a compounded gap: parents shifting to Spanish may provide fewer Nahuatl utterances AND lower-quality Spanish input as non-native speakers

""", None),

("How Talklet Fills Narrative Gaps in Tlamachiyotl", "H3"),
("""
1. The missing 0–5 chapter: Talklet addresses the developmental window before Tlamachiyotl begins. The complete educational arc becomes: Talklet-type early childhood speech support (ages 0–5) → Nahuatl-medium academy (ages 5–18) → digital economy pipeline (ages 18+). This arc fills a gap in the brainstorm document, which begins at school age but does not address the earlier developmental period that determines school readiness.

2. The Nahuatl speech double-gap: In Huasteca households shifting to Spanish, children lose Nahuatl input in the critical 0–5 window AND receive lower-quality Spanish from non-native-speaking parents. This double gap is the root-cause problem the academy addresses. Talklet's evidence base (published research on the word gap, bilingual households, brain development timelines) documents and quantifies this gap — providing the academic foundation for the "why now, why here" section of the fund pitch.

3. Practical early childhood intervention: A simplified Nahuatl speech-tracking program — even paper-based word counting guides for parents — could be added as a community feeder intervention, identifying high-need children before academy age and establishing the academy's relationship with families 2–3 years before enrollment.

4. Research opportunity: Talklet's core methodology (measuring speech quality/quantity longitudinally) applied to Nahuatl-speaking households generates original data on the indigenous language word gap. This is precisely the type of "original research the academy can generate" identified in the brainstorm's Open Research Gaps section. A UVI (Universidad Veracruzana Intercultural) partnership that places this research question at the center of a joint program opens the second, research-based funding track.

5. Founder credibility signal: Talklet demonstrates the founder's EdTech startup experience, speech analytics domain knowledge, and early childhood research literacy. For the PE fund LP pitch — particularly to education-focused foundations (Kellogg, Ford) and impact family offices — this is a differentiating credential.

""", None),

("APPENDIX C: PE FUND — LP CAPITAL LANDSCAPE", "H1"),
("""
""", None),

("Market Position: White Space in LatAm", "H3"),
("""
No indigenous-focused private equity or venture fund exists in Latin America as of 2025. This is a genuine first-mover opportunity. Globally, the only structural comparable is Raven Indigenous Capital Partners (Canada): indigenous-led, ~CAD $25M Fund I, closed 2021, LP base of foundations and family offices, 12–15% net IRR target, VC/growth equity strategy.

Closest Mexico comparable: Adobe Capital — impact PE, base-of-pyramid thesis, ~$30M Fund II, LP base of Mexican family offices and IFC. Net IRR target 15–18%. Adobe Capital is the fund to benchmark against for return expectations and LP outreach.

""", None),

("Recommended Fund Parameters", "H3"),
("""
  First close target:         $10–15M
  Final close target:         $25–35M
  Timeline to final close:    18–24 months
  Management fee:             1.5%
  Carried interest:           15% (with optional impact hurdle: 12% base, 18% if impact KPIs met)
  Return target (net IRR):    10–15% for impact/foundation LPs; 15–18% for commercial tranche
  Fund life:                  10 years
  Domicile:                   Cayman Islands LP (primary) + parallel CKD/FIBRA E for Mexican institutional LPs

Note: A blended finance share structure — concessional tranche from foundations (PRI/MRI, accepting sub-10% returns) + commercial tranche from family offices (targeting 15%+) — allows different return expectations across LP classes. This is the structural innovation that makes a $25–35M first fund viable.

""", None),

("LP Universe — By Probability of Commitment", "H3"),
("""
Anchor LP candidates (highest probability — move first):

  W.K. Kellogg Foundation: Deepest Mexico + indigenous mandate of any US foundation. Program-related investments (PRIs) do not require market returns. Ticket: $2–5M. Approach via Mexico program officers, not the investment team. The Kellogg Foundation's history in Mexico (40+ years of grantmaking) makes it the single most likely anchor.

  Ford Foundation: BUILD program funds indigenous rights organizations; Mexico office is active. PRI structure. Ticket: $1–3M. Approach via Ford Foundation Mexico City office.

  Christensen Fund: Explicit biocultural diversity and indigenous landscape mandate globally. Fast decision-making. Ticket: $500K–2M. Strong strategic alignment.

  Builders Vision (Lukas Walton family office): Explicit indigenous and regenerative portfolio. Ticket: $1–3M. Relationship-driven.

  Ceniarth: Family office that explicitly anchors first-time impact GPs in Latin America. Has made checks as small as $500K. Best early-stage family office anchor.

Medium probability LPs:

  IDB Invest: Explicit indigenous and Afro-descendant inclusion strategy, LatAm mandate, precedent of LP commitments to Mexico-focused impact funds (IGNIA Fund). Ticket: $5–10M. Semi-governmental — note per brief.

  IFC (World Bank): LP'd in IGNIA Fund (Mexico). Indigenous Peoples Performance Standard PS7 creates alignment. Ticket: $5–15M. Fully governmental — note per brief.

  ImpactAssets Emerging Fund Manager program: DAF capital ($250K–2M) to first-time impact GPs + marketplace visibility to donor-advised fund holders and HNWIs. Key first-time GP accelerator.

  MATT Foundation / Mexican diaspora family offices (Texas, California, Illinois): $250K–1M tickets. Relationship-driven. Diaspora capital with homeland investment motivation.

  Toniic T100 network: Impact investor network whose members actively seek emerging market funds. Membership unlocks warm introductions to aligned family offices globally.

""", None),

("Regulatory and Legal Structure", "H3"),
("""
Domicile: Cayman Islands Limited Partnership is the standard structure for US, European, and foundation LPs. Optimal for this fund.

Parallel vehicle: A CKD (Certificado de Capital de Desarrollo) or FIBRA E structure for Mexican institutional LPs. Note: AFORE (pension fund) capital is semi-governmental — exclude per brief. Target Mexican family offices and high-net-worth individuals through the parallel vehicle.

US LP access: Regulation D 506(b) or 506(c) exemption. No SEC registration required for accredited investors only. Limit to under 250 non-US investors for Regulation S.

CNBV: GP entity in Mexico may require CNBV authorization if marketing to Mexican retail investors. Avoid by limiting to sophisticated/institutional Mexican LPs only.

FATCA: Required for Mexican LPs investing into a Cayman vehicle. Manageable with US tax counsel.

""", None),

("Path to First Close", "H3"),
("""
  Months 1–6:   Kellogg Foundation or Ford Foundation PRI commitment as anchor ($2–4M)
  Months 6–12:  2–3 mission-aligned family offices (Ceniarth, Builders Vision, diaspora FO): $3–6M
  Months 12–18: IDB Invest or DFC tranche: $5–10M (semi-governmental; include if LP constraints allow)
  First close:  ~$10–15M
  Final close:  ~$25–35M over 24 months

Emerging manager programs to engage in parallel with LP outreach:
  ImpactAssets Emerging Fund Manager Program
  GIIN membership + IRIS+ impact framework adoption (credibility signal, accelerates LP due diligence)
  Toniic T100 (HNWI warm intros)
  Sistema B México (mission-aligned deal flow and co-investor network)

""", None),

("The Ecosystem Thesis — What Makes This Fund Different", "H3"),
("""
The PE fund is not a standalone investment vehicle. It is the commercial layer of a self-reinforcing ecosystem:

  Academy (Tlamachiyotl): Develops the human capital pipeline — digitally literate, bilingual Nahuatl-Spanish graduates who become the workforce and eventually the founders of fund portfolio companies.
  Data Cooperative (student digital income): Generates community cash flow and early digital literacy, demonstrating market viability of indigenous digital labor to AI companies and investors.
  Venture Builder: Incubates the businesses that the fund will eventually invest in, using AZLera-proven community trust-building techniques and diaspora EIR talent.
  PE Fund: Provides growth capital to builder graduates; generates financial returns that recycle into the academy and cooperative endowment.

The fund pitch to LPs is not "invest in indigenous Mexico." It is "invest in a 20-year institution-building program with a private equity return structure and a self-reinforcing flywheel that no single-fund thesis has."

(Sources: All research from training data cutoff August 2025. Live verification recommended for fund databases via PitchBook, GIIN ImpactBase, IDB Invest published portfolio, and Kellogg/Ford/Christensen foundation annual reports.)
""", None),
]

# ── Build full text and record heading positions ────────────────────────────
full_text = "\n\n"  # separator before first section
position_offset = len(full_text)  # chars already in prefix

heading_ranges = []  # (start_offset, end_offset, style)

for (text, style) in ENTRIES:
    start = position_offset
    end = start + len(text)
    if style in ('H1', 'H3'):
        heading_ranges.append((start, end, style))
    full_text += text
    position_offset += len(text)

print(f"Total text length: {len(full_text)} chars")
print(f"Insert position (doc end_index): {end_index}")
print(f"Headings to format: {len(heading_ranges)}")

# ── Insert all text in one request ─────────────────────────────────────────
insert_requests = [
    {
        'insertText': {
            'location': {'index': end_index},
            'text': full_text
        }
    }
]

result = service.documents().batchUpdate(
    documentId=DOC_ID,
    body={'requests': insert_requests}
).execute()
print("Text inserted successfully.")

# ── Apply heading styles ────────────────────────────────────────────────────
# After insertion, doc positions shift: inserted text starts at end_index
# Heading at offset X in full_text → doc position end_index + X
style_map = {
    'H1': 'HEADING_1',
    'H3': 'HEADING_3',
}
# Navy color for H1, Teal for H3
color_map = {
    'HEADING_1': {'red': 0.1, 'green': 0.2, 'blue': 0.4},
    'HEADING_3': {'red': 0.0, 'green': 0.5, 'blue': 0.5},
}

fmt_requests = []
for (start_off, end_off, style_key) in heading_ranges:
    doc_start = end_index + start_off
    doc_end = end_index + end_off
    named_style = style_map[style_key]
    fmt_requests.append({
        'updateParagraphStyle': {
            'range': {'startIndex': doc_start, 'endIndex': doc_end},
            'paragraphStyle': {'namedStyleType': named_style},
            'fields': 'namedStyleType'
        }
    })
    # Apply color
    col = color_map[named_style]
    fmt_requests.append({
        'updateTextStyle': {
            'range': {'startIndex': doc_start, 'endIndex': doc_end},
            'textStyle': {
                'foregroundColor': {'color': {'rgbColor': col}},
                'bold': True,
                'fontSize': {'magnitude': 14 if style_key == 'H1' else 12, 'unit': 'PT'}
            },
            'fields': 'foregroundColor,bold,fontSize'
        }
    })

# Batch in chunks of 50
chunk_size = 50
for i in range(0, len(fmt_requests), chunk_size):
    chunk = fmt_requests[i:i+chunk_size]
    service.documents().batchUpdate(
        documentId=DOC_ID,
        body={'requests': chunk}
    ).execute()
    print(f"Formatted requests {i+1}–{i+len(chunk)} of {len(fmt_requests)}")

print("All done.")
