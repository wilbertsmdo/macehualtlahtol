import sys, time
sys.path.insert(0, '/data/data/com.termux/files/usr/lib/python3.13/site-packages')
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

DOC_ID = '1VB9eKJhOUtligj2oiBiFcqVkWrWS-ghBjW66qzsokZ4'
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(
    '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json',
    scopes=SCOPES
)
service = build('docs', 'v1', credentials=creds)

doc = service.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])

# Map: display text → URL
# Order matters: longer/more specific strings first to avoid partial matches
LINK_MAP = [
    # Connectivity
    ('starlink.com/mx',         'https://www.starlink.com/mx'),
    ('telcel.com',              'https://www.telcel.com'),
    ('Starlink',                'https://www.starlink.com/mx'),
    # Income / data platforms
    ('Karya',                   'https://karya.in'),
    ('Remotasks',               'https://www.remotasks.com'),
    ('TELUS AI',                'https://www.telusinternational.com/solutions/ai-data'),
    ('Outlier AI',              'https://outlier.ai'),
    ('Outlier',                 'https://outlier.ai'),
    ('Appen',                   'https://www.appen.com'),
    ('iMerit',                  'https://imerit.net'),
    # Talent / recruitment
    ('Enseña por México',       'https://www.ensenapormexico.org'),
    ('Codeando México',         'https://codeandomexico.org'),
    ('Catchafire',              'https://www.catchafire.org'),
    ('AIESEC',                  'https://aiesec.org'),
    ('Idealist',                'https://www.idealist.org'),
    ('UN Volunteers Online',    'https://www.onlinevolunteering.org'),
    ('GoOverseas',              'https://www.gooverseas.com'),
    # Academy / curriculum models
    ('IDIEZ',                   'https://www.idiez.org.mx'),
    ('CESDER',                  'https://www.cesder-prodes.org'),
    ('Clontarf Foundation',     'https://www.clontarffoundation.org.au'),
    ('École 42',                'https://42.fr'),
    # Mandarin
    ('HelloChinese',            'https://www.hellochinese.com'),
    ('Taiwan TECRO',            'https://www.tecro.org.tw'),
    ('TECRO',                   'https://www.tecro.org.tw'),
    ('CI-UAEH',                 'https://www.uaeh.edu.mx/campus/icsa/instituto_confucio/'),
    ('CI-UV',                   'https://www.uv.mx/confucio/'),
    # Social entrepreneur platforms
    ('Ashoka México',           'https://www.ashoka.org/en-MX/country/mexico'),
    ('Ashoka',                  'https://www.ashoka.org'),
    ('Sistema B México',        'https://www.sistemab.org/mexico/'),
    ('Sistema B',               'https://www.sistemab.org'),
    ('Endeavor México',         'https://endeavor.org.mx'),
    ('Endeavor',                'https://endeavor.org'),
    # Funders / philanthropy
    ('Google.org',              'https://www.google.org/our-work/'),
    ('Microsoft Philanthropies','https://www.microsoft.com/en-us/corporate-responsibility/philanthropies'),
    ('Amazon Future Engineer',  'https://www.amazonfutureengineer.com'),
    ('Cisco Networking Academy','https://www.netacad.com'),
    ('Salesforce.org',          'https://www.salesforce.org/grants/'),
    ('W.K. Kellogg Foundation', 'https://www.wkkf.org'),
    ('Kellogg Foundation',      'https://www.wkkf.org'),
    ('Ford Foundation',         'https://www.fordfoundation.org'),
    ('Christensen Fund',        'https://christensenfund.org'),
    ('Builders Vision',         'https://buildersvision.com'),
    ('IDB Invest',              'https://www.idbinvest.org'),
    ('IDB Lab',                 'https://bidlab.org'),
    ('Raven Indigenous Capital','https://www.ravenindigenouscapital.com'),
    ('Adobe Capital',           'https://www.adobecapital.org'),
    ('Ceniarth',                'https://ceniarth.com'),
    ('Village Capital',         'https://vilcap.com'),
    # Tech philanthropy
    ('aka.ms/teals',            'https://aka.ms/teals'),
    ('netacad.com',             'https://www.netacad.com'),
    # Research / orgs
    ('Common Voice',            'https://commonvoice.mozilla.org'),
    ('Masakhane',               'https://www.masakhane.io'),
    ('UNESCO',                  'https://www.unesco.org'),
    ('UAEH',                    'https://www.uaeh.edu.mx'),
    ('UV Xalapa',               'https://www.uv.mx'),
]

# Build lookup: for each paragraph, scan for link targets and record (si_in_doc, ei_in_doc, url)
link_requests = []
seen_ranges = []  # avoid overlapping link ranges

def overlaps(s1, e1, s2, e2):
    return not (e1 <= s2 or e2 <= s1)

matched_count = 0
for elem in body:
    if 'paragraph' not in elem:
        continue
    para_si = elem.get('startIndex', 0)
    para_ei = elem.get('endIndex', 0)
    runs = elem['paragraph'].get('elements', [])

    # Build char-offset → doc-index mapping
    # Each run has startIndex, endIndex in doc coordinates
    for run in runs:
        if 'textRun' not in run:
            continue
        run_si = run.get('startIndex', 0)
        run_ei = run.get('endIndex', 0)
        run_text = run['textRun'].get('content', '')

        # Check if run already has a link
        existing_link = run['textRun'].get('textStyle', {}).get('link')
        if existing_link:
            continue  # already linked

        for phrase, url in LINK_MAP:
            pos = 0
            while True:
                idx = run_text.find(phrase, pos)
                if idx == -1:
                    break
                # Doc coordinates
                doc_start = run_si + idx
                doc_end = run_si + idx + len(phrase)
                # Check bounds
                if doc_end > run_ei:
                    break
                # Check overlap with already-added ranges
                overlap = any(overlaps(doc_start, doc_end, s, e) for s, e in seen_ranges)
                if not overlap:
                    link_requests.append({'updateTextStyle': {
                        'range': {'startIndex': doc_start, 'endIndex': doc_end},
                        'textStyle': {'link': {'url': url}},
                        'fields': 'link'
                    }})
                    seen_ranges.append((doc_start, doc_end))
                    matched_count += 1
                    # Only link first occurrence per run per phrase to avoid flooding
                    break
                pos = idx + 1

print(f"Total link requests: {len(link_requests)} (matched {matched_count} occurrences)")

# Execute in batches of 50
sent = 0
for i in range(0, len(link_requests), 50):
    chunk = link_requests[i:i+50]
    service.documents().batchUpdate(documentId=DOC_ID, body={'requests': chunk}).execute()
    sent += len(chunk)
    print(f"  Applied {sent}/{len(link_requests)}")
    time.sleep(0.3)

print("Done.")
