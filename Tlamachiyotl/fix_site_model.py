import sys
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

NAVY = {'red': 0.11, 'green': 0.20, 'blue': 0.42}
TEAL = {'red': 0.00, 'green': 0.47, 'blue': 0.47}
def rgb(c): return {'color': {'rgbColor': c}}

# Re-read fresh to get current indices
doc = service.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])

# Find heading "Recommended Alternative: Mobile Unit" and the two paragraphs after it
heading_si = heading_ei = None
paras_to_delete_ei = None

for i, elem in enumerate(body):
    if 'paragraph' not in elem:
        continue
    si = elem.get('startIndex', 0)
    ei = elem.get('endIndex', 0)
    text = ''.join(r.get('textRun', {}).get('content', '') for r in elem['paragraph'].get('elements', [])).strip()
    if 'Recommended Alternative: Mobile Unit' in text:
        heading_si = si
        heading_ei = ei
        print(f"Heading found: si={si} ei={ei}")
        # Collect the next two non-empty paragraphs (van costs + CESDER)
        count = 0
        for j in range(i + 1, min(i + 10, len(body))):
            nelem = body[j]
            if 'paragraph' not in nelem:
                continue
            ntext = ''.join(r.get('textRun', {}).get('content', '') for r in nelem['paragraph'].get('elements', [])).strip()
            nsi = nelem.get('startIndex', 0)
            nei = nelem.get('endIndex', 0)
            print(f"  Next para si={nsi} ei={nei}: {ntext[:80]}")
            if ntext:
                count += 1
                paras_to_delete_ei = nei
                if count == 2:  # delete heading + 2 body paragraphs
                    break
        break

if heading_si is None:
    print("ERROR: heading not found")
    sys.exit(1)

print(f"\nWill delete range si={heading_si} to ei={paras_to_delete_ei}")

NEW_CONTENT = (
    "Phase 0–1 Site: Fixed Rented Premises in Huejutla\n"
    "Huejutla de Reyes is the confirmed Phase 0–1 HQ. The site is a fixed, rented professional space — "
    "a proper building that signals aspiration and permanence to students and families: "
    "a converted classroom block, a cultural centre, or a rented commercial premises. "
    "The founder will be on-site. Facility requirements: 1–2 classrooms or open-plan workspace, "
    "reliable electrical supply, roof access for Starlink mount, secure equipment storage. "
    "Estimated monthly rental in Huejutla: MXN 3,000–8,000/month.\n"
    "Why fixed, not mobile. A van works for outreach but cannot be the primary learning environment — "
    "it sends the wrong signal about the academy’s ambition and permanence. "
    "The founding site must feel like a place students are proud to attend. "
    "Professional premises also simplify safeguarding (defined entry/exit points, parental sign-in) "
    "and grant compliance (fixed address for AC registration).\n"
    "Chicontepec access — Phase 2 model. In Phase 0–1, Chicontepec-cabecera students commute to Huejutla "
    "for the after-school program (~45 min by colectivo). Phase 2 introduces a periodic Chicontepec outreach: "
    "the founder or a teaching fellow travels to Chicontepec 1–2 days per week, "
    "renting classroom space at the local telebachillerato or comunitario. "
    "CESDER (Centro de Estudios para el Desarrollo Rural, Puebla Sierra Norte) ran exactly this "
    "mobile extension model for rural outreach — applicable to Phase 2, not Phase 0–1.\n"
)

requests = [
    # Step 1: delete the old heading + 2 body paragraphs
    {'deleteContentRange': {
        'range': {'startIndex': heading_si, 'endIndex': paras_to_delete_ei}
    }},
    # Step 2: insert new content at the same position
    {'insertText': {
        'location': {'index': heading_si},
        'text': NEW_CONTENT
    }},
]

service.documents().batchUpdate(documentId=DOC_ID, body={'requests': requests}).execute()
print("Text replaced. Re-reading to format headings...")

# Re-read to format new headings
doc2 = service.documents().get(documentId=DOC_ID).execute()
body2 = doc2.get('body', {}).get('content', [])

fmt = []
targets = {
    'Phase 0–1 Site: Fixed Rented Premises': ('HEADING_3', NAVY),
    'Why fixed, not mobile.': ('HEADING_3', TEAL),
    'Chicontepec access — Phase 2 model.': ('HEADING_3', TEAL),
}

for elem in body2:
    if 'paragraph' not in elem:
        continue
    si = elem.get('startIndex', 0)
    ei = elem.get('endIndex', 0)
    text = ''.join(r.get('textRun', {}).get('content', '') for r in elem['paragraph'].get('elements', [])).strip()
    for key, (style, col) in targets.items():
        if text.startswith(key[:30]):
            fmt.append({'updateParagraphStyle': {
                'range': {'startIndex': si, 'endIndex': ei},
                'paragraphStyle': {'namedStyleType': style},
                'fields': 'namedStyleType'
            }})
            fmt.append({'updateTextStyle': {
                'range': {'startIndex': si, 'endIndex': ei - 1},
                'textStyle': {
                    'foregroundColor': rgb(col),
                    'bold': True,
                    'fontSize': {'magnitude': 11, 'unit': 'PT'},
                },
                'fields': 'foregroundColor,bold,fontSize'
            }})
            print(f"  Formatted: '{text[:60]}'")
            break

if fmt:
    service.documents().batchUpdate(documentId=DOC_ID, body={'requests': fmt}).execute()
print("Done.")
