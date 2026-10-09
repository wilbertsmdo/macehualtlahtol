import sys
sys.path.insert(0, '/data/data/com.termux/files/usr/lib/python3.13/site-packages')
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

DOC_ID = '1VB9eKJhOUtligj2oiBiFcqVkWrWS-ghBjW66qzsokZ4'
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive',
]
creds = Credentials.from_service_account_file(
    '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json',
    scopes=SCOPES
)
drive = build('drive', 'v3', credentials=creds)

# 14 open comments with specific reply text
REPLIES = [
    ('AAACIDONxCU',
     '✅ DONE — Appendix E (Revenue Streams) added. All project revenue types listed in Tier 1/2/3/Zero-income format: voice corpus ($50–150/student/month), translated texts (MXN 0.50–2/word), digital art, YouTube/podcast, coded apps, Common Voice/Wikipedia.'),
    ('AAACIDONw_k',
     '✅ DONE — Teacher training Step 0 added to Tlamachiyotl_Project_Plan.md under Next Steps: "Step 0 (before cohort launch): recruit and train 1 Nahuatl-fluent teacher-in-residence; partner with IDIEZ or UV Intercultural for training methodology."'),
    ('AAACIDONw_c',
     '✅ DONE — "LANGUAGES — SPANISH: POSITIONING" section added at end of doc. Covers three-point position (Nahuatl primary, Spanish as second language, Mandarin as third), Cummins Threshold Hypothesis rationale, and enrollment communication script in Spanish.'),
    ('AAACIDONw-o',
     '✅ DONE — "ONLINE CURRICULA & BOOTCAMP RESOURCES" section added with full links: CS50x (Harvard), freeCodeCamp, The Odin Project, Laboratoria (github.com/Laboratoria/curriculum), Kaggle Learn, CONAFE Robótica, and CONALEP dual-enrollment pathway.'),
    ('AAACIDONw-g',
     '✅ DONE — "FINANCE MODULE 6 — CRYPTO REMITTANCE RAILS" section added. Covers Bitso (CNBV-registered, $1B+/month), MoneyGram+Stellar (rural cash-out agents), Strike (Lightning Network), Mexico Fintech Law 2018 regulation note, and a hands-on class exercise design.'),
    ('AAACIDONw-Y',
     '✅ ALREADY IN DOC — 135 hyperlinks were embedded inline in the previous session via add_links.py. All key organisations, platforms, and funders are linked (Starlink, Telcel, Karya, Enseña por México, IDIEZ, CESDER, Clontarf, Kellogg Foundation, IDB Invest, etc.).'),
    ('AAACIDONw-Q',
     '✅ DONE — Appendix E (Revenue Streams) covers all student project ideas by revenue tier: Tier 1 (voice corpus, translated texts — highest $/hour), Tier 2 (digital art, YouTube/podcast — medium), Tier 3 (coded apps — high ceiling, longer runway), Zero-income (Common Voice, Wikipedia — community/CV building).'),
    ('AAACIDONw-M',
     '✅ DONE — CONAFE Robótica (with direct link to conafe.edu.mx) and CONALEP dual-enrollment pathway added to the "ONLINE CURRICULA & BOOTCAMP RESOURCES" section. CONALEP note includes the technician certificate pathway and that no tuition is charged.'),
    ('AAACIDONw9I',
     '✅ DONE — "THE 4-WEEK BOOTCAMP — TLAMACHIYOTL PISCINE" section added. Week 1: Scratch + Nahuatl vocab game. Week 2: HTML/CSS personal page in Nahuatl. Week 3: Python + Nahuatl word-lookup CLI app. Week 4: GitHub portfolio + peer presentations. Modelled on École 42 Piscine.'),
    ('AAACIDONw9E',
     '✅ ALREADY IN DOC — XP clarification added inline in the gamification paragraph: "Levels / XP (Experience Points: students advance by completing and having peers validate projects, not by exams)." Appears in the Curriculum / Pedagogy section.'),
    ('AAACIDONw88',
     '✅ DONE — Appendix F (Site Comparison) added with detailed Huejutla vs Chicontepec comparison: population table (122,905 vs 50,129; 51% vs 70% Nahuatl speakers), infrastructure comparison (internet, transport, marginalization index), and phase recommendations.'),
    ('AAACIDONwzw',
     '✅ ALREADY IN DOC — "Connectivity stack — research findings" section added in the previous session. Contains Starlink Mexico pricing (MXN 799–1,399/month), CFE Telecomunicaciones coverage note, Telcel 700 MHz rural coverage, and recommended monthly cost stack (MXN 1,100–3,500/month).'),
    ('AAACIDONwxw',
     '✅ ALREADY IN DOC — "Co-partner and ground-person sourcing — platforms and approaches" section added in the previous session. Lists: Ashoka México, Sistema B, Endeavor, LinkedIn search terms (Huasteca/educación indígena), Enseña por México alumni, UAEH/UV faculty, and AZLera network.'),
    ('AAACIDONwxs',
     '✅ ALREADY IN DOC — "What this question actually asks" clarification section added in the previous session. Explains the Spanish literacy baseline (students from SEP schools have Spanish literacy but limited formal Nahuatl literacy), and the enrollment assessment decision (oral Nahuatl proficiency by community elder, no minimum Spanish requirement).'),
]

print(f"Posting {len(REPLIES)} replies...")
for cid, text in REPLIES:
    try:
        drive.replies().create(
            fileId=DOC_ID,
            commentId=cid,
            fields='id,content',
            body={'content': text, 'action': 'resolve'}
        ).execute()
        print(f"  ✓ {cid[:12]}… — resolved")
    except Exception as e:
        print(f"  ✗ {cid[:12]}… — ERROR: {e}")

print("\nAll done.")
