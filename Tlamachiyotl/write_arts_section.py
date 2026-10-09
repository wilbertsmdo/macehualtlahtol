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

ARTS_TEXT = """\

ARTS & MUSIC — CURRICULUM AREA

Why arts and music belong in the academy

Arts education is not enrichment — it is infrastructure. The research case for including arts and music as a core curriculum track is strong across four independent domains.

Cognitive transfer. Arts training produces measurable gains in the skills the academy's other tracks require. Music training strengthens phonological awareness (Bolduc, 2009), spatial-temporal reasoning linked to mathematics (Hetland & Winner, 2004), and working memory. Visual arts develop pattern recognition and precision — directly applicable to coding and data work. A meta-analysis of arts-integrated schools (Catterall, Chaparro & Iwanaga, 2012 — Champions of Change) found lower dropout rates and higher academic engagement among disadvantaged youth, even controlling for socioeconomic status.

Language development. Singing in one's native language is one of the most effective phonological anchors for endangered-language learners. The melody, prosody, and tonal patterns of a language are encoded through song in ways rote vocabulary lists cannot replicate. Huapango huasteco — the traditional son huasteco genre — is performed in Nahuatl and preserves vocabulary, metaphor, and oral history in living form. Teaching it is Nahuatl-language instruction delivered through music.

Cultural identity and retention. UNESCO's Seoul Agenda on Arts Education (2010) documents the link between traditional arts practice and community attachment, which in turn predicts reduced migration pressure and higher rates of young people staying in or returning to their home community — directly relevant to the academy's long-term mission of developing community-embedded talent rather than extracting it.

Revenue pathway. Traditional Huasteca crafts (bordado huasteco, amate painting) already sell internationally. Digital art and music production are emerging income tracks with low infrastructure requirements. The arts curriculum provides the production skills that the artisan cooperative revenue model (see Appendix E) requires to function.

Nahuatl arts heritage of the Huasteca region

The academy sits in one of the richest surviving indigenous arts zones in Mexico. This heritage is not merely background context — it is curriculum content.

Huapango huasteco (son huasteco): The signature music of the Huasteca. Performed on three instruments — violin, jarana huasteca, and quinta huapanguera. Distinctive falsetto singing (canto de falsete) and zapateado footwork. Sung in Nahuatl and Spanish. A living tradition with active practitioners in Huejutla, Chicontepec, and Tantoyuca. Declared Intangible Cultural Heritage of Mexico by INAH (2017). UNESCO intangible heritage nomination in process (jointly with son jarocho and son calentano under "sones de México").

Bordado huasteco: The colorful hand embroidery of Nahua women — blouses (quechquémitl and huipil), tablecloths, and wall hangings featuring florals, birds, and animals in vivid colour on black or white fabric. Sold at artisan markets in Mexico City, internationally via Novica and Etsy, and directly to collectors. A quality quechquémitl sells for MXN 800–4,000 locally; international buyers pay 3–5× via direct channels. A direct revenue-generating skill the artisan cooperative can formalise and digitalise.

Amate bark paper art: Pre-Columbian tradition of bark-paper painting, rooted in Nahua ritual (the amate tree, Ficus insipida, was used for codex pages). Contemporary amate art from Guerrero and Puebla Nahuas is internationally collected by galleries in the US and Europe. Huasteca students have roots in the same tradition — a medium that connects pre-Hispanic, colonial, and contemporary Nahua identity.

Danza de Moros y Cristianos and ritual dances: Syncretic ceremonial performance still practiced in Huasteca communities during patron saint festivals, combining pre-Hispanic choreography and colonial-era narrative. Costume design, choreography, music composition — all teachable. Drama and performance are also documented tools for language immersion.

Décima and oral poetry: The huapango tradition includes improvised verse (the huapango arribeño variant, practiced in the Sierra Gorda, is famous for poetic duels — topadas). Composing and performing décimas in Nahuatl is an advanced language and rhetoric exercise that also connects students to a living competitive art form.

Cross-pollination with other academy areas

Arts × Nahuatl language: Huapango is performed in Nahuatl. Transcribing traditional songs creates reading and writing exercises in Nahuatl. Analysing verse structure teaches grammar and metaphor in the target language. Composing original décimas develops advanced Nahuatl register. Music is the most natural Nahuatl-medium class after formal language instruction itself.

Arts × STEM and coding: Music production (DAW software: GarageBand, LMMS, Audacity) introduces acoustic signal processing, mathematics of rhythm and tuning, and basic programming (p5.js for generative visuals, Sonic Pi for code-generated music). Visual arts connects to graphic design (Figma, Inkscape), which is a direct digital income skill. Creative coding projects — generative art, interactive Nahuatl vocabulary games — make strong portfolio pieces.

Arts × Finance module: The artisan cooperative in Appendix E requires the production skills that the arts curriculum develops. The finance module provides cost, pricing, margin, and cooperative governance skills. Together they form a vertically integrated student income track: arts curriculum → artisan cooperative → finance module → digital sales channel.

Arts × Digital income (Appendix E): Digital art sales (Tier 2) require Figma/Inkscape proficiency. Music recordings in Nahuatl are genuinely rare — a Nahuatl music archive commands interest from Common Voice, Spotify curators of indigenous music playlists, language preservation foundations, and documentary filmmakers. Student-recorded traditional songs are a unique, low-competition revenue and grant-attracting asset.

Arts × Sports: Ceremonial music and dance at sports events — traditional dances before games, student performances at community tournaments — create a public-facing showcase. The Clontarf Foundation uses sport as a community gateway; arts plays the same role for families who are skeptical of a tech-focused academy. A joint arts-sports opening ceremony is an immediate community trust-building tool.

Arts × Mandarin: Music is the lowest-barrier cross-cultural exchange medium. Pentatonic scales appear prominently in both Nahuatl/Mesoamerican and Chinese musical traditions — an accessible point of connection for early student cohorts learning Mandarin. A joint Nahuatl-Mandarin music session (traditional instruments from both traditions, simple pentatonic improvisation) requires no shared language and creates memorable cross-cultural contact.

Arts × Nutrition and wellbeing: Arts therapy is well-documented as a wellbeing intervention for adolescents in high-stress or marginalised communities. Community mural projects, expressive music sessions, and collaborative textile work build the social cohesion and psychological safety that the academy's learning environment depends on. This is not a separate track — it is ambient in a well-designed arts curriculum.

Curriculum — what to teach

Foundation track (all students, Year 1):
  Music literacy: rhythm, pitch, basic notation — taught through huapango rhythms, which are familiar to students and culturally grounded. A jarabe tapatío or son huasteco rhythm is more motivating than a textbook exercise and just as rigorous.
  Traditional instrument introduction: jarana huasteca or violin, depending on available teacher. Even one semester of structured instrument exposure builds the cognitive-transfer effects documented in the literature.
  Visual arts: drawing, colour theory, composition — taught through bordado design and amate motifs as entry points. Students see their own cultural forms as the starting material, not imitations of a distant art-world canon.
  Digital creation: Canva, Inkscape, GarageBand/LMMS — the bridge between traditional production skills and digital income. A student who can design her own quechquémitl pattern can also design a logo or a social media graphic.

Concentration track (optional, Year 2+):
  Music production: multitrack recording, MIDI arrangement, mixing. Capstone: students produce and release a Nahuatl music EP under a Creative Commons licence, with full credits and a streaming presence.
  Graphic design: professional Figma workflow — wireframing, brand identity, print layout. Connects to the cooperative's marketing and digital artisan shop.
  Textile and artisan production: advanced bordado, pattern scaling, quality control for export market. Pairs with cooperative finance training.
  Performance and oral tradition: décima composition, huapango ensemble performance, community event coordination. Produces the public face of the academy.

Potential partners — local

Casa de la Cultura, Huejutla de Reyes: Every Mexican municipality operates a Casa de la Cultura. The Huejutla branch offers music, visual arts, and dance classes. Likely underutilised and open to collaboration agreements — shared space, co-teaching, student referrals. The most immediate and frictionless arts partner available.

INAH — Delegación Hidalgo / Veracruz: Instituto Nacional de Antropología e Historia has field staff in the Huasteca focused on cultural preservation. Natural partner for documenting and archiving Nahuatl huapango recordings. INAH grants and in-kind support are available for approved cultural documentation projects.

Secretaría de Cultura de Hidalgo: State arts funding body — runs artist residency and community arts programs with annual application cycles. The academy's artisan track qualifies directly for community cultural development funding.

Secretaría de Cultura de Veracruz: Runs a strong huapango huasteco promotion program. Active interest in partnering with schools that document and teach traditional Veracruz regional music.

FONCA — Fondo Nacional para la Cultura y las Artes: Federal grants body (now under Secretaría de Cultura). The FONCA Comunidades grant (community-rooted cultural projects) awards MXN 100–500K. Application once per year — a Nahuatl arts academy is a strong candidate.

UAEH (Universidad Autónoma del Estado de Hidalgo) and UV (Universidad Veracruzana): Both universities have arts and music faculties. UV has a well-regarded ethnomusicology program with documented interest in Huasteca regional music. Faculty collaborations can provide visiting instructors, student-teacher practicum placements, and research supervision for the academy's cultural documentation work.

Grupo Mono Blanco and Huapango Arribeño ensembles: Active son huasteco and son arribeño ensembles working in the region. Precedent exists for partnering traditional artists with educational institutions (artist-in-residence, master class formats). Contact via Secretaría de Cultura de Veracruz or directly through regional music festivals (Festival Huasteco).

Potential partners — international

El Sistema México / Fundación El Sistema: The Venezuelan Sistema model — instrument-based social development for disadvantaged youth — has a Mexican chapter. Provides instruments, teacher training methodology, and network access. The most directly applicable international music-education model for this context. Contact: fundacionelsistema.mx.

Latin Grammy Cultural Foundation: Funds music education programs focused on Latin music communities. Awards scholarships and school-level grants. A Nahuatl music program is genuinely underrepresented in Latin music education — strong differentiation as an applicant. Contact: latingrammy.com/en/cultural-foundation.

Berklee College of Music — Global Initiatives: Berklee has international community partnerships, subsidised online courses, and documented work with indigenous musical traditions. The Berklee Online platform offers free or low-cost music production courses applicable to the concentration track. Contact: berklee.edu/about/community.

Silkroad (Yo-Yo Ma initiative): The Silkroad Ensemble works with underrepresented musical traditions globally and has an education and documentation arm. Strong fit for a Nahuatl music documentation and cross-cultural performance project. Contact: silkroad.org/education.

UNESCO — Culture Sector / Intangible Cultural Heritage: UNESCO's 2003 Convention for Safeguarding Intangible Cultural Heritage is directly applicable to huapango huasteco. Engaging UNESCO on a documentation and transmission project creates international credibility and opens a separate grant track from education funding. Contact via Mexico's National UNESCO Commission (CONALMEX, SEP).

British Council — Arts and Creative Economy: Funds arts-in-education projects in Mexico with an international collaboration component. Most relevant if a UK conservatory or university (e.g. Royal College of Music, Guildhall) joins as a co-partner for instrument-based or music-production programming. Contact: britishcouncil.org.mx/programas/artes.

Fundación BBVA México — Arte y Cultura: One of the largest private arts funders in Mexico. Funds community arts education with a heritage preservation angle. Documented interest in indigenous cultural projects. Contact: fundacion.bbva.com/es/mexico.

Common Voice / Mozilla Foundation: Mozilla's Common Voice project collects voice recordings for open-source speech datasets. A Nahuatl music + speech archive aligns directly — Mozilla has funded indigenous language recording projects and the data produced has downstream value for AI language tools. Contact: commonvoice.mozilla.org/sentence-collectors.

Revenue — arts-specific

Artisan cooperative (Appendix E, Tier 1): Bordado, amate, and craft production formalised through the school cooperative. Revenue flows to students. MXN 800–4,000/piece for quality bordado locally; 3–5× via direct international sales channels (Novica, Etsy, gallery consignment). The arts curriculum develops the skill base; the cooperative is the sales structure.

Digital art sales (Tier 2): Students trained in Figma and Inkscape produce art prints, merchandise designs, brand identity work, and digital downloads. Global market via Redbubble, Society6, or direct Gumroad stores. Low production cost, passive revenue once set up.

Nahuatl music archive — licensing: Record traditional huapango songs with elder practitioners and student ensembles. License recordings to documentary filmmakers, streaming playlists, language apps, and academic institutions. This content is rare — there is no well-catalogued, high-quality Nahuatl music archive with permissive licensing. Being first to build one is a durable competitive position.

Student music releases: Students record and release original Nahuatl music via DistroKid or TuneCore (Spotify, Apple Music, YouTube Music). Streaming revenue is modest per track but builds cultural presence, portfolio evidence, and grant eligibility.

Paid performances and cultural tourism: Once the academy has a student ensemble, paid performances at cultural festivals (Día de Muertos, Feria de Huejutla, Carnaval Huasteco), school visits, and cultural tourism circuits generate community revenue and local visibility. Connects to the eco-tourism venture builder track.

Arts grants — stackable with education funding: FONCA Comunidades, Secretaría de Cultura federal grants, NEA (US National Endowment for the Arts — international programs exist), British Council arts grants, UNESCO emergency safeguarding funds. These are awarded to cultural projects, not schools — they are a separate and stackable funding track alongside education grants.

Research gaps — the academy can answer these

  What is the effect of huapango-integrated Nahuatl instruction on vocabulary retention versus standard literacy methods? A controlled comparison across two cohorts is feasible within Year 2.
  Does participation in the arts concentration correlate with lower out-migration rates among alumni? A 3-year longitudinal survey design is achievable within the academy's own tracking.
  Can a student-run artisan cooperative reach financial sustainability within three years without external subsidy? The academy is the natural site for this data.
  Is there a latent international market for licensed Nahuatl music and craft content that a pilot archive and shop can quantify? A 6-month pilot with Common Voice audio and an Etsy shop generates real market data.

"""

# ── Get current doc end index ────────────────────────────────────────────────
doc = service.documents().get(documentId=DOC_ID).execute()
body_content = doc.get('body', {}).get('content', [])
insert_idx = body_content[-1].get('endIndex', 1) - 1
print(f"Appending {len(ARTS_TEXT)} chars at index {insert_idx}...")

service.documents().batchUpdate(
    documentId=DOC_ID,
    body={'requests': [{'insertText': {
        'location': {'index': insert_idx},
        'text': ARTS_TEXT
    }}]}
).execute()
print("Inserted. Re-reading for formatting...")

# ── Re-read and format headings ──────────────────────────────────────────────
doc2 = service.documents().get(documentId=DOC_ID).execute()
body2 = doc2.get('body', {}).get('content', [])

H2_HEADINGS = {
    'ARTS & MUSIC — CURRICULUM AREA',
}

H3_TEAL = {
    'Why arts and music belong in the academy',
    'Nahuatl arts heritage of the Huasteca region',
    'Cross-pollination with other academy areas',
    'Curriculum — what to teach',
    'Potential partners — local',
    'Potential partners — international',
    'Revenue — arts-specific',
    'Research gaps — the academy can answer these',
}

# Bold orange labels within body text
ORANGE_LABELS = ['Cognitive transfer.', 'Language development.', 'Cultural identity', 'Revenue pathway.']
TEAL_LABELS = ['Arts ×']

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

    for h3 in H3_TEAL:
        if text.startswith(h3[:35]):
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
            break
    else:
        # Bold + orange for "Cognitive transfer." etc
        for label in ORANGE_LABELS:
            if text.startswith(label):
                end_idx = min(si + len(label), ei - 1)
                fmt.append({'updateTextStyle': {
                    'range': {'startIndex': si, 'endIndex': end_idx},
                    'textStyle': {'bold': True, 'foregroundColor': rgb(ORANGE)},
                    'fields': 'bold,foregroundColor'
                }})
                break
        # Bold + teal for "Arts × ..." cross-pollination lines
        for label in TEAL_LABELS:
            if text.startswith(label):
                colon = text.find(':')
                end_idx = min(si + colon + 1, ei - 1) if colon != -1 else min(si + 30, ei - 1)
                fmt.append({'updateTextStyle': {
                    'range': {'startIndex': si, 'endIndex': end_idx},
                    'textStyle': {'bold': True, 'foregroundColor': rgb(TEAL)},
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
