from google.oauth2.service_account import Credentials as SACredentials
from googleapiclient.discovery import build

SA_KEY = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
DOC_ID = '15wEbCHRmjW09T5KgMLhHiGjyp4YcCRrNpBunnAiQURs'
SA_SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive',
]

sa_creds = SACredentials.from_service_account_file(SA_KEY, scopes=SA_SCOPES)
docs = build('docs', 'v1', credentials=sa_creds)

NEW_SECTION = 'NEOLOGISM GENERATOR RESEARCH'

SECTION_TEXT = """\
NEOLOGISM GENERATOR RESEARCH

Research summary: building a Nahuatl neologism generator for technical vocabulary not currently present in Nahuatl — terms found in sources such as the Financial Times or New York Times. Focus: applying Chinese calque and Greek/Latin compounding strategies to Modern Huasteca Nahuatl.

Strategies in the Literature

1. Native Compounding (Nahuatl's own tradition)

The most documented approach. Nahuatl morphology is transparent and agglutinative; new words built from existing morphemes are immediately parseable to speakers. This has been happening organically for decades:

  tepoztototl ("airplane") = tepoztli (metal) + tototl (bird)
  tepozcoatl ("metro/subway") = tepoztli + coatl (serpent)
  tepozyoyolli ("car") = tepoztli + yoyolli (moving/heart-thing)

tepoztli functions like a combining form in the same way Greek tele- or bio- does in English scientific vocabulary. Key sources: Mexicolore "How Nahuatl uses compound words to adapt to an ever-changing world" and the ScienceDirect paper "Lexical creativity in modern Nahuatl" (2023), which documents that word-formation patterns have not degraded despite endangerment.

IDIEZ example from monolingual grammar writing: no word existed for "vocal folds," so they coined totozcaamayo = tozquitl (voice) + amatl (paper/sheet) + -yo (bodypart suffix). Pure internal derivation, no borrowing.

2. The Chinese Model (semantic calque)

The closest analog to the proposed generator approach. Chinese systematically calques foreign technical concepts into native morphemes:
  dianao (electric brain) = computer
  shouji (hand machine) = mobile phone
  hulianwang (mutually-linked net) = internet
  yinhang (silver row/firm) = bank

Strategy: decompose the foreign concept into semantic components, find morphemes carrying those semantics in the target language, compound them. Result: semantically transparent, no foreign phonology borrowed. Nahuatl is equally well-suited because its morphological transparency is comparable. Gap in the literature: no one has formally applied this model to Nahuatl neologism generation as a systematic methodology — an open space.

3. The Greek/Latin Neoclassical Compound Model

How modern scientific English works: telephone, microscope, algorithm, cryptocurrency. The key is maintaining an inventory of semantic primitives (roots with defined meanings) and combining them productively under consistent rules. The insight for Nahuatl: define a stable root inventory — analogous to Greek tele-/micro-/bio- — drawn from Classical Nahuatl roots that modern Huasteca speakers still recognize. This is the prescriptive version of what IDIEZ does informally.

4. Committee-Based Institutional Models (Hawaiian, Hebrew, Welsh)

Hebrew (Ben Yehuda, 1890s onward): Language Committee coined words from Semitic roots systematically — glida (ice cream), ofanayim (bicycle), milon (dictionary). Key: formal committee with approval authority + dissemination via newspapers Ben Yehuda owned. ~150,000 modern Hebrew words result.

Hawaiian Lexicon Committee: most directly applicable indigenous-language precedent. A 2025 ACL paper ("A Web Platform for Facilitating Hawaiian Word Neologism") describes Kuene, a platform supporting the committee workflow: propose, vote in committee, ratify, publish. The 2003 paper "Indigenous New Words Creation Perspectives from Alaska and Hawaii" (NAU) documents how the Hawaiian model was exported to Alutiiq communities.

Welsh: Canolfan Bedwyr (Bangor University) produces Welsh technical terminology for computing, legal, and medical domains via formal terminology panels.

Key Considerations for a Nahuatl Neologism Generator

Morphological basis: Use existing Nahuatl roots — compounding is natural and already productive in the language.
Transparency principle: Prefer semantically transparent coinages (Chinese calque model) over phonological borrowing from Spanish or English.
Root inventory: Requires a curated list of productive semantic primitives — the IDIEZ dictionary is the primary source.
Validation: The Hawaiian model shows community/committee approval is needed for adoption; a generator alone is insufficient.
Register target: FT/NYT terms concentrate in finance, geopolitics, technology, and climate — the top 200-300 missing concepts should be the initial target set.
Pioneer gap: No formal neologism body exists for any Nahuatl variety today — this generator would be the first systematic effort.

Conclusion

A Chinese calque + Nahuatl native compounding hybrid is the most defensible and linguistically clean approach. Greek/Latin etymology is less directly applicable (Nahuatl shares no historical etymological tradition with them), but the meta-strategy — define a stable root inventory, apply productive compounding rules — is exactly right.

Sources

Lexical creativity in modern Nahuatl — ScienceDirect (2023): https://www.sciencedirect.com/science/article/abs/pii/S0024384123000128
How Nahuatl uses compound words to adapt — Mexicolore: https://www.mexicolore.co.uk/aztecs/language/how-nahuatl-adapts-to-changing-world
A Web Platform for Facilitating Hawaiian Word Neologism — ACL (2025): https://aclanthology.org/2025.computel-main.21.pdf
Indigenous New Words Creation Perspectives from Alaska and Hawaii — NAU (2003): https://jan.ucc.nau.edu/~jar/ILR/ILR-10.pdf
Continuity and Change in Modern Nahuatl Word Formation — ResearchGate: https://www.researchgate.net/publication/365690985_Continuity_and_Change_in_Modern_Nahuatl_Word_Formation
Revival of the Hebrew language — Wikipedia: https://en.wikipedia.org/wiki/Revival_of_the_Hebrew_language
Ben-Yehuda's Hebrew Revival — the-brain.blog: https://the-brain.blog/ben-yehuda-hebrew-revival-lessons-languages-37597/
Toward a Comprehensive Model for Nahuatl Language Research — eScholarship: https://escholarship.org/uc/item/7g88w6nn
Neoclassical compound — Wikipedia: https://en.wikipedia.org/wiki/Neoclassical_compound
"""

# Sub-headings to style as HEADING_3 within the new section
H3_EXACT = {
    'Strategies in the Literature',
    'Key Considerations for a Nahuatl Neologism Generator',
    'Conclusion',
    'Sources',
}
H3_STARTSWITH = (
    '1. Native Compounding',
    '2. The Chinese Model',
    '3. The Greek/Latin Neoclassical',
    '4. Committee-Based Institutional',
)

LAST_TOC_ENTRY = 'OPEN QUESTIONS / NEXT STEPS'
BLUE = {'red': 0.07, 'green': 0.33, 'blue': 0.80}


def para_text(element):
    para = element.get('paragraph', {})
    return ''.join(
        r.get('textRun', {}).get('content', '')
        for r in para.get('elements', [])
    ).strip()


def batch(reqs):
    if reqs:
        docs.documents().batchUpdate(
            documentId=DOC_ID, body={'requests': reqs}
        ).execute()


# ── Phase 1: read doc, find positions ─────────────────────────────────────────
doc = docs.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])
end_index = body[-1].get('endIndex', 1)

toc_entry_end = None
seen = set()
for el in body:
    text = para_text(el)
    named = el.get('paragraph', {}).get('paragraphStyle', {}).get('namedStyleType', '')
    if text == LAST_TOC_ENTRY and named == 'HEADING_2' and text not in seen:
        toc_entry_end = el.get('endIndex')
        seen.add(text)
        break

print(f'Doc end index: {end_index}')
print(f'Insert TOC entry after index: {toc_entry_end}')
if toc_entry_end is None:
    raise RuntimeError(f'Could not find TOC entry for "{LAST_TOC_ENTRY}"')

# ── Phase 2: insert text — section at end first (higher index), TOC entry second ─
# Processing higher-index insert first in a single batchUpdate ensures the lower-index
# TOC insert position is unaffected by the larger insertion.
batch([
    {'insertText': {
        'location': {'index': end_index - 1},
        'text': '\n' + SECTION_TEXT,
    }},
    {'insertText': {
        'location': {'index': toc_entry_end},
        'text': NEW_SECTION + '\n',
    }},
])
print('Phase 2: text inserted')

# ── Phase 3: apply HEADING_2 to both occurrences of NEW_SECTION ────────────────
doc = docs.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])
style_reqs = []
for el in body:
    text = para_text(el)
    start, end = el.get('startIndex', 0), el.get('endIndex', 0)
    if text == NEW_SECTION:
        style_reqs.append({'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': 'HEADING_2'},
            'fields': 'namedStyleType',
        }})
batch(style_reqs)
print(f'Phase 3: HEADING_2 applied to {len(style_reqs)} paragraph(s)')

# ── Phase 4: find section heading, apply pageBreakBefore + HEADING_3 sub-heads ─
# After HEADING_2 is applied, both occurrences get headingIds. Iterate in doc order:
# first occurrence = TOC entry, second = actual section heading.
doc = docs.documents().get(documentId=DOC_ID).execute()
body = doc.get('body', {}).get('content', [])

seen4 = set()
toc_entry_range = None
section_heading_id = None
section_start = None
reqs4 = []

for el in body:
    text = para_text(el)
    start, end = el.get('startIndex', 0), el.get('endIndex', 0)
    para = el.get('paragraph', {})
    named = para.get('paragraphStyle', {}).get('namedStyleType', '')
    hid   = para.get('paragraphStyle', {}).get('headingId')

    if text == NEW_SECTION and named == 'HEADING_2':
        if text not in seen4:
            toc_entry_range = (start, end)
            seen4.add(text)
        else:
            section_start = start
            section_heading_id = hid
            reqs4.append({'updateParagraphStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'paragraphStyle': {'pageBreakBefore': True},
                'fields': 'pageBreakBefore',
            }})

    # Apply HEADING_3 to sub-headings inside the new section only
    if section_start and start > section_start:
        if text in H3_EXACT or any(text.startswith(p) for p in H3_STARTSWITH):
            reqs4.append({'updateParagraphStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'paragraphStyle': {'namedStyleType': 'HEADING_3'},
                'fields': 'namedStyleType',
            }})

batch(reqs4)
print(f'Phase 4: pageBreakBefore + {len(reqs4) - 1} HEADING_3 styles applied')
print(f'         section headingId: {section_heading_id}')

# ── Phase 5: apply hyperlink to TOC entry ─────────────────────────────────────
if not (toc_entry_range and section_heading_id):
    print(f'WARNING: toc_entry_range={toc_entry_range}, headingId={section_heading_id}')
else:
    start, end = toc_entry_range
    batch([{'updateTextStyle': {
        'range': {'startIndex': start, 'endIndex': end - 1},
        'textStyle': {
            'link': {'headingId': section_heading_id},
            'underline': True,
            'foregroundColor': {'color': {'rgbColor': BLUE}},
        },
        'fields': 'link,underline,foregroundColor',
    }}])
    print('Phase 5: TOC hyperlink applied')

print(f'\nDone — https://docs.google.com/document/d/{DOC_ID}/edit')
