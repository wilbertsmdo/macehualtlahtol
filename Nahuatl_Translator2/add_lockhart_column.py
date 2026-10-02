#!/usr/bin/env /data/data/com.termux/files/usr/bin/python3
"""
Add Lockhart 2001 delta notes as column L to the Morpheme Mapping sheet,
and create a 'Missing Morphemes' tab for morphemes absent from the 35 rows.
"""
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SA_PATH  = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json'
SHEET_ID = '1TYw3gvcSGmCTQEKchEKlNDUm1BOL-i66jfhsNA1og-k'
SCOPES   = ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']

creds      = Credentials.from_service_account_file(SA_PATH, scopes=SCOPES)
gc         = gspread.authorize(creds)
sheets_svc = build('sheets', 'v4', credentials=creds)
sh         = gc.open_by_key(SHEET_ID)
ws         = sh.get_worksheet(0)

# ── Column L data — keyed by row # (1-indexed matching column A) ──────────────
# Format: delta type tag + concise finding from Lockhart 2001
LOCKHART_NOTES = {
    1:  ("NEW_EXAMPLES | PRODUCTIVITY_NOTE — "
         "Lockhart (L9 p.12) distinguishes 3 agentive patterns: "
         "(1) -ni [fully productive]; "
         "(2) -qui/-c [older/frozen past-habit]: iztanamacac (salt-seller), tlaxcalchiuhqui (tortilla-maker); "
         "(3) -cauh [possessed agentive = 'my X-er']: notlatocauh (my ruler), notemaquixticauh (my savior), + reverential -catzin: notlatocatzin. "
         "Also: alcaldetia → agentive confirms denominal -tia → -ni chain."),

    2:  ("NEW_EXAMPLES — "
         "Lockhart (L15 p.23) provides full -oni paradigm: teconi (cutter), qualoni (edible), chihualoni (doable/possible), "
         "tlamachtiloni (teaching-instrument), tetlacuitlahuiltiloni (caring-instrument). "
         "Key sentence contrasts plain -oni vs. tepoz- + -oni: 'in quahuitl ca huel teconi yece oiçoliuh in tepoztlateconi' "
         "(the stick is good to cut with, but the iron cutter has rusted). "
         "Confirms te- object prefix works INSIDE the nominalized form."),

    3:  ("NEW_EXAMPLES — "
         "Lockhart (L5 pp.7–8) confirms tla- + verb + -(l)li = generic patientive. "
         "Paradigm: tlacohualli (purchased thing), tlatlatilli (burned/ashes), tlapololli (confusion/disorder), "
         "tlacuilolli (written document), tlaitlantli (demand/petition), tlachihualli (made thing/product), "
         "tlanamactli (merchandise/sale). "
         "The tla- unspecified-object prefix before the verb is the standard pattern — not explicit in our table."),

    4:  ("DISCREPANCY — MISSING LOCATIVE TYPE: "
         "Lockhart (L13 pp.18–19) documents -can as a 3rd locative suffix alongside -yan and -loyan. "
         "-can = where a quality/state is situated: cacchiuhcan (sandal-making place), qualcan (good place), acan (nowhere), nican (here), oncan (there). "
         "3-way distinction: -can (where quality IS) vs. -yan (where agent DOES action) vs. -loyan (where impersonal action OCCURS). "
         "Our table currently only documents -yan and -loyan."),

    5:  ("NEW_EXAMPLES — "
         "Lockhart (L5 pp.7–8) attests ne- prefix creating mutual/reciprocal -liztli nominals: "
         "nenamictiliztli (mutual marrying/marriage), nepohualiztli (self-counting/pride), "
         "netecuitlahuiliztli (mutual caretaking), netlacuitlahuiliztli. "
         "RULE: ne- + verb + -liztli = institutionalized/impersonal mutual process noun. "
         "Distinction from mo-: mo- is the verbal reflexive/reciprocal; ne- is the NOMINALIZED impersonal form. "
         "Critical for abstract/institutional neologisms."),

    6:  ("DISCREPANCY — ALLOMORPH RULE: "
         "Lockhart (L12 pp.17–18) shows -otl (not -yotl) after vowel-final stems: "
         "quallotl (goodness, not *kuali-yotl), oquichotl (maleness). "
         "RULE: vowel-final stem → -otl; consonant-final stem → -yotl. "
         "Paradigm: pillotl (nobility), teucyotl (lordship), tlatocayotl (sovereignty-system), "
         "nanyotl (motherhood), yaoyotl (war-quality), coneyotl (childhood), teoyotl (divinity), "
         "toltecayotl (artisanal excellence), acayotl (reed-ness), chichihualayotl (breast milk)."),

    7:  ("NEW_EXAMPLES — "
         "Lockhart (L9 p.12) confirms -tzitzintin as the reverential animate plural collective: "
         "pipiltzitzintin (honored noble children collectively), macehualtzitzintin (honored commoners collectively). "
         "This is MISSING from our table. "
         "Pattern: noun + -tzitzin (reverential sg.) → noun + -tzitzintin (reverential pl. collective). "
         "Distinct from plain -meh plural; carries institutional/honorific weight for group references."),

    8:  ("NEW_EXAMPLES | MISSING FORM: "
         "Lockhart (L1–L9) attests reverential diminutives on non-person nouns: "
         "cactzintli (dear sandal), caltzintli (dear house), atzintli (dear water). "
         "MISSING FORM: -tepiton as alternate smallish-modifier: caltepiton (little house, pp.4,11,23), tlaltepiton. "
         "Also: achitzin (reverential of achi = 'just a tiny bit'), nopiltzitzinhuan (my dear children - double reverential). "
         "-tepiton encodes 'smallish-X' without the affective/reverential tone of -tsintli."),

    9:  ("NEW_EXAMPLES | PRODUCTIVITY_NOTE — "
         "Lockhart (throughout) confirms huey- as fully productive augmentative. "
         "Attested: huei tlahtohuani (great-speaker = emperor/paramount ruler), "
         "huei apantli (great canal/river = major waterway), huey otli (highway = great road). "
         "KEY EXTENSION: huey- also functions as degree intensifier on ADJECTIVES: "
         "huei oquichtli (very manly/very masculine, L12 p.17) — not just scale for nouns. "
         "Our table should extend rule to: huey + adjective = degree superlative."),

    10: ("DISCREPANCY — SEMANTIC CORRECTION: "
         "Lockhart (L12 pp.17–18) shows -yoh/-e is primarily a POSSESSIVE 'one who HAS X' suffix, "
         "not a 'pertaining to' relational. "
         "Paradigm: tlale (land-owner/having land), mile (field-owner), pilhua (child-having/parent), "
         "axcahua (possessions-owner), topile (staff-owner/constable), quaquauhe (horn-having/bovine). "
         "For qualities: teuhyo (dusty = having dust), çoquiyo (muddy = having mud). "
         "CORRECTION: tepoz-yoh would mean 'one who has metal/iron' not 'pertaining to metal.' "
         "For 'pertaining to' readings, prefer noun-noun compounding over -yoh."),

    11: ("NEW_EXAMPLES — "
         "Lockhart (L14 p.21; L12 p.18) confirms a- privative. "
         "Also attests temporal-privative compounds: "
         "ayamo (not yet = a- + yamo), aoc (no longer = a- + oc), "
         "aocmo (no more/never again). "
         "In possession context: atlatquihua (without possessions), amo taxcahua (non-owner). "
         "DISTINCTION: derivational a- (prefix on nouns/adjectives) vs. ahmo/amo (verbal negation particle) "
         "— Lockhart treats them in same lesson but they are formally distinct."),

    12: ("NEW_EXAMPLES | PRODUCTIVITY_NOTE — "
         "Lockhart (L3 pp.3–5; L15 p.23) provides causative paradigm: "
         "nicchihualtia, nicchololtia (chase off), nicnemitia (sustain/support), "
         "nicmachtia (teach = make-know), niccahualtia (hold back). "
         "KEY EXTENSION: DENOMINAL causative (noun + -tia = 'act as X / behave as X'): "
         "alcaldetia (act as alcalde), jueztia (act as judge), niccaltia (build/make house). "
         "Our table only describes adjective→causative; the noun→causative pattern is equally productive. "
         "Also: ninonamictia (marry = 'cause oneself to be matched')."),

    13: ("NEW_EXAMPLES | PRODUCTIVITY_NOTE — "
         "Lockhart (L2–L3; L15) confirms mo- reflexive. "
         "KEY NOTE: mo- with PLURAL subject = RECIPROCAL (not just reflexive): "
         "monamicti (they marry EACH OTHER), omonamicti (they got married to each other). "
         "Also: mo- in possessed nominals: monemiliz (your life-way/lifestyle), "
         "motetlachihuililiz (your duty-to-people). "
         "Distinction: mo- (verbal 3rd/reflexive) vs. ne- (impersonal nominalized mutual) — "
         "ne-namictiliztli = marriage-as-institution; mo-namictiliztli = his/her marrying."),

    14: ("DISCREPANCY — MISSING ALLOMORPH: "
         "Lockhart (L13 pp.18–20) documents -hua as an alternate passive allomorph alongside -lo-: "
         "nemoa/nemohua (people live/is lived), yolihua (people live/is lived), "
         "chocohua (people weep), huiloa/huilohua (people travel to). "
         "-hua allomorph occurs with certain verb classes in Classical Nahuatl. "
         "Also confirms passive of applicative: maco (is given to someone), tetlamacoc (food was distributed). "
         "For MHN, -lo- is dominant; -hua is Classical alternant to note but not use as primary generator rule."),

    15: ("NEW_EXAMPLES — "
         "Lockhart (throughout) confirms cenca as primary degree intensifier. "
         "Attested patterns: cenca notech monequi (very much needed), cenca miec (very many), "
         "cenca etic (very heavy), cenca mahuiztic (very impressive/marvelous), "
         "cenca ohuican (very dangerous place), cenca tetolinia (oppresses greatly). "
         "Formula confirmed: cenca + adjective OR cenca + verb phrase. "
         "No prefix-based intensifier found — cenca is invariably pre-position (adverb, not prefix)."),

    16: ("NEW_EXAMPLES — "
         "Lockhart (L14 p.22; L16 p.28) confirms achi as degree-diminisher. "
         "Attested: cuix ye achi tiquelehuia in atzintli (do you somewhat want the water?), "
         "cuix oc achi ticmomacehuiz (would you like a little more?). "
         "NEW FORMS: achitzin (just a little = reverential/polite diminutive of achi, pp.22,28); "
         "oc achi (a little more = oc [repetitive] + achi) = 'incrementally more/slightly further.' "
         "The achitzin form is useful for polite/formal register diminishment."),

    17: ("NEW_EXAMPLES | MISSING FORM: "
         "Lockhart (L8 pp.11–12) provides full number system. "
         "MISSING SUFFIX: -pa multiplicative = 'X times': "
         "ceppa (once), oppa (twice), expa (three times), nappa (four times), macuilpa (five times). "
         "This -pa suffix is MISSING from our table and is the Classical way to say 'X-fold.' "
         "Also missing: -tetl counting classifier for inanimate round objects: "
         "centetl, ontetl, yetetl (one, two, three [inanimates]). "
         "Also: ordinal inic + number: inic centetl (the first), inic caxtoltetl omei (the eighteenth)."),

    18: ("NEW_EXAMPLES — "
         "Lockhart (L11 p.16; appendices) confirms oc ceppa as standard repetitive. "
         "Attested: ma oc ceppa mahuiltitiecan (let them play again), "
         "oc ceppa niquitoa (I say again / let me restate). "
         "NEW CONTRAST: yeppa (formerly/habitually/previously = prior habitual) "
         "contrasts with oc ceppa (will do again = future repetition). "
         "Pair frames temporal axis: yeppa (was formerly) ↔ oc ceppa (do/will do again)."),

    19: ("DISCREPANCY — NOT ATTESTED CLASSICALLY: "
         "Lockhart (2001) does NOT attest seyotl/seyolia as a morpheme for 'inter-/co-.' "
         "Classical Nahuatl expresses mutual/reciprocal via: "
         "(1) mo- reflexive with plural subject: monamicti = they marry each other; "
         "(2) ne- prefix in nominals: nenamictiliztli = mutual marrying (L5). "
         "The ne- pattern is likely the better Classical model for mutual/inter- institutional nominals. "
         "Recommendation: prefer ne- + verb + -liztli over seyolia for formal mutual-process neologisms. "
         "seyotl may be a more specifically modern/Huastecan innovation."),

    20: ("NEW_EXAMPLES — "
         "Lockhart (L14 p.22; L3 p.4) confirms achtopa and çatepan in real documents: "
         "'achtopa oncan oniya teopantzinco çatepan ompa onitlacouh' "
         "(first I went to church, afterward I bought there). "
         "FULL TEMPORAL SEQUENCE (missing from our table): "
         "yalhua (yesterday), moztla (tomorrow), huiptla (day after tomorrow), "
         "imoztlayoc (day before yesterday), ye huecauh (long ago), oc huecauh (still far future). "
         "These temporal anchors flesh out the full before/after axis."),

    21: ("NEW_EXAMPLES — "
         "Lockhart (L4 pp.5–7; L5 p.8) provides full relational noun system: "
         "icpac (on top of), itzintlan (at the base of), inahuac (near/alongside), "
         "ixpan/ixco (before/in front of), itic (inside/within), icampa (behind), "
         "ihuicpa (toward/in the direction of — FULL form of -huic). "
         "Attested in docs: itzintlan tepetl mani (land lies at mountain base). "
         "NOTE: ihuicpa (not just -huic) is the postpositional form used in documents."),

    22: ("NEW_EXAMPLES | PRODUCTIVITY_NOTE — "
         "Lockhart (L4 pp.5–7; throughout) confirms ipan as multifunction relational. "
         "Extended figurative uses: "
         "ipan Moteucçoma ninemi (I live under/within the era of Moteucçoma — temporal/under), "
         "ipan tlatoa in tamalchihualiztli (speaks about tamale-making — THEMATIC 'about'), "
         "atle ipan nimitzmati (I regard you as nothing — STATUS 'counted-as'). "
         "Our table covers spatial 'within'; these thematic/temporal/status readings are not addressed. "
         "Road-compound for trans- confirmed: 'in notlal itech acitiuh in Tollocan otli' (path reaching land)."),

    23: ("NEW_EXAMPLES — "
         "Lockhart (appendices) confirms a- privative as main anti-/counter-/non- marker. "
         "No dedicated counter-action morpheme beyond a-. "
         "The pattern a- + [concept] + -yotl = 'quality of without-X / anti-X orientation' is natural Classical usage. "
         "Complex negation examples from real documents: "
         "'amo iuh tlamani in Xochimilco in iuh nican tlamani' (it is not arranged there as here). "
         "Note: ayao/aocmo (no longer/against-further continuation) as compound temporal-privative adverbs."),
}
# Rows 24-35: no deltas from Lockhart (pre-modern texts, not applicable)
for r in range(24, 36):
    LOCKHART_NOTES[r] = (
        "NOT ADDRESSED — Lockhart (2001) pre-dates modern neologistic strategy. "
        "Section 5 calque strategies are post-Classical inventions not found in colonial documents. "
        "However, the base verbs used in these rules ARE confirmed etymologically in Lockhart: "
        "iximati (know deeply, L9), tlazohtla (love/cherish, L5), mauhtia (fear, L9), "
        "tlahtoa (speak/govern, throughout) — all attested in classical usage."
    )

# Build column L values (header + 35 data rows)
col_header = "Lockhart 2001 Notes (NAW Examples)"
col_values = [[col_header]]
for i in range(1, 36):
    note = LOCKHART_NOTES.get(i, "")
    col_values.append([note])

# Write column L
ws.update(values=col_values, range_name='L1', value_input_option='RAW')
print(f"Column L written: {len(col_values)} rows")

# ── Format column L ───────────────────────────────────────────────────────────
sid = ws.id
requests = [
    # Header cell L1
    {'repeatCell': {
        'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1,
                  'startColumnIndex': 11, 'endColumnIndex': 12},
        'cell': {'userEnteredFormat': {
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'fontSize': 10},
            'backgroundColor': {'red': 0.55, 'green': 0.25, 'blue': 0.10},
            'horizontalAlignment': 'CENTER',
        }},
        'fields': 'userEnteredFormat(textFormat,backgroundColor,horizontalAlignment)',
    }},
    # Data cells wrap + top-align
    {'repeatCell': {
        'range': {'sheetId': sid, 'startRowIndex': 1,
                  'startColumnIndex': 11, 'endColumnIndex': 12},
        'cell': {'userEnteredFormat': {
            'wrapStrategy': 'WRAP',
            'verticalAlignment': 'TOP',
            'textFormat': {'fontSize': 8},
        }},
        'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment,textFormat)',
    }},
    # Column L width
    {'updateDimensionProperties': {
        'range': {'sheetId': sid, 'dimension': 'COLUMNS',
                  'startIndex': 11, 'endIndex': 12},
        'properties': {'pixelSize': 380},
        'fields': 'pixelSize',
    }},
]
sheets_svc.spreadsheets().batchUpdate(
    spreadsheetId=SHEET_ID,
    body={'requests': requests}
).execute()
print("Column L formatted.")

# ── Create 'Missing Morphemes' tab ────────────────────────────────────────────
# Check if tab already exists
existing_titles = [ws2.title for ws2 in sh.worksheets()]
if 'Missing Morphemes' not in existing_titles:
    sh.add_worksheet(title='Missing Morphemes', rows=30, cols=5)
    print("Tab 'Missing Morphemes' created.")
ws2 = sh.worksheet('Missing Morphemes')
ws2_id = ws2.id

MISSING = [
    ['#', 'Morpheme(s)', 'Meaning / Function', 'Key Examples (Lockhart 2001)', 'Priority for Generator'],

    ['M1', 'Applicative: -lia / -ilia / -illia',
     'Adds beneficiary/recipient argument to verb (= do X FOR/TO someone)',
     'niquitzomilia (sew for s/o), nicpixquilia (harvest for s/o), niccuilia (take FROM s/o), '
     'nimitznomaquilia (I give to you — reverential). '
     'Passive of applicative: maco (is given to s/o), tetlamacoc (people were given food)',
     'HIGH — most productive missing morpheme; needed for benefactive neologisms'],

    ['M2', 'Instrumental/manner: -tica (bound) / -ica (free postposition)',
     '-tica bound to noun = "by means of / with [noun]"; -ica relational = "by/with/by means of"',
     'cuchillotica (with a knife), mitica (with an arrow), tlamahuiçoltica (miraculously), '
     'nocamatica (with my mouth); '
     'ica atl quipaca (washes with water), ica in itlaçoezçotzin (by his precious blood)',
     'HIGH — essential for expressing means/manner in sentences; distinct from tepoz- compounds'],

    ['M3', 'ne- reciprocal/impersonal prefix (nominal)',
     'Impersonal reflexive/reciprocal prefix on nominalizations: ne- + verb + -liztli = mutual/institutional process noun',
     'nenamictiliztli (mutual marrying / marriage-as-institution), '
     'nepohualiztli (self-counting / pride), '
     'netecuitlahuiliztli (mutual caretaking), netlacuitlahuiliztli. '
     'Distinction: mo- is VERBAL reflexive; ne- is NOMINALIZED impersonal/mutual form',
     'HIGH — critical for institutional/mutual process neologisms (compare Row 5, 13, 35)'],

    ['M4', 'Locative suffix: -can',
     '3rd locative type (alongside -yan and -loyan): where a quality/state IS situated',
     'cacchiuhcan (sandal-making place), qualcan (good place / place of goodness), '
     'acan (nowhere), nican (here/this place), oncan (there/that place), '
     'mieccan (many places). '
     'Distinction from -yan (where agent DOES) and -loyan (where impersonal action OCCURS)',
     'HIGH — currently missing from Row 4; changes locative neologism strategy'],

    ['M5', '-pa multiplicative suffix',
     'Creates "X-fold / X times" from numerals',
     'ceppa (once), oppa (twice), expa (three times), nappa (four times), macuilpa (five times). '
     'Relevant for: "twofold growth" = ome-pa tlahueyiliztli; "tenfold" = matlacpa',
     'MEDIUM — useful for economic/statistical neologisms'],

    ['M6', '-cauh / -catzin possessed agentive',
     '"My X-er / the one who does X to/for me" — social role pattern with possessive prefix',
     'notemaquixticauh (my savior), notlatocauh (my ruler), toteopixcauh (our priest), '
     'nocihuauh (my wife); reverential: notemaquixticatzin, notlatocatzin. '
     'Pattern: no- + [verb stem] + -cauh = "the one who does X for me"',
     'MEDIUM — relevant for social role neologisms (my teacher, my healer, my counselor)'],

    ['M7', 'Directional prefixes: on- (away) / hual- (toward)',
     'on- = motion away/outward or completive; hual- = motion toward/hither. '
     'Together: onhual- / hualon- for complex directional compounds',
     'nonaci (I arrive) vs. nichualaci (I arrive here); '
     'on- also completive marker in some uses; '
     'Lesson 7 shows combinations with motion compound verbs',
     'MEDIUM — important for motion-based process verbs'],

    ['M8', 'Compound verb motion suffixes: -tiuh, -to, -co, -tinemi, -tica',
     '-tiuh/-tihui (go to do X), -to (went to do X, purposive past), '
     '-co (came here to do X), -tinemi (go around doing habitually), '
     '-tica (be doing X — progressive / stative-active)',
     'titlaxtlauhtiuh (you go to pay), nicchihuato (I went to make), '
     'nicchihuaco (I came to make), quichiuhtinemi (goes around doing), '
     'nicchixtica (I am waiting), nitemotica (I am descending)',
     'MEDIUM — needed for ongoing/purposive process verbs in neologisms'],

    ['M9', 'Relational noun: -pan (on/at/in/about/under/regarding)',
     'Most multifunctional relational in Nahuatl: spatial, temporal, thematic, status/regard senses',
     'tlalpan (on the ground), ipan xihuitl (in the year), '
     'ipan tlatoa in tamalchihualiztli (speaks ABOUT tamale-making), '
     'ipan Moteucçoma ninemi (lives UNDER/IN era of M.), '
     'atle ipan nimitzmati (regard you as nothing = counts-as-zero)',
     'MEDIUM — its thematic "about/regarding" sense is useful for discourse neologisms'],

    ['M10', 'Relational noun: -tlan (near/alongside/place-of)',
     'Encodes proximity/adjacency; different from -pan (on/in)',
     'Domingo itlan nemi (lives near/alongside Domingo), '
     'itzintlan tepetl mani (lies at the base of the mountain), '
     'tlatzintlan (at the base of things). '
     'Also in place names: Mazatlan, Tenochtitlan (tlan = place-of/alongside)',
     'MEDIUM — complement to -yan/-loyan for place-of neologisms'],

    ['M11', 'Absolutive suffixes: -tl, -tli, -li, -in',
     'Free-noun endings that DROP in possession and compounds — essential for compound formation',
     '-tl after vowels: atl, metl, tetl; '
     '-tli after consonants: tlacatl, patli; '
     '-li in certain classes: petlatl; '
     '-in for some animates: tochtli/tochin, michin. '
     'Possessed nouns drop absolutive: nocaltzin (not *no-caltzin-tli). '
     'In compounds: tepoz- + tl → tepoz- (drop absolutive)',
     'HIGH (technical) — generator must know when to drop -tl/-tli in compound formation'],

    ['M12', 'Comitative: -huan / ihuan (with/together-with)',
     'Marks companion/accompaniment; different from -tica (instrumental "by means of")',
     'niquinhuica Fabian ihuan ipiltzin (I take Fabian along with his child), '
     'inhuan quichihua (does it with them), '
     'nohuan yoli (lives with me/alongside me). '
     'Possessed: nohuan (my companion), mohuan, ihuan',
     'MEDIUM — for "co-/jointly-with" constructions distinct from -tica (manner) and mo- (self)'],

    ['M13', 'Plural morphemes: -tin, -meh, -htin + reduplication',
     'Full animate plural system; reduplication as noun-plural marker',
     '-tin animate pl: macehualtin, teopixcatzintli → teopixcatzitzintin; '
     '-meh alternate: totome (turkeys), pitzome (pigs); '
     '-htin for agent/role nouns: teteuctin (lords = te-teuc-tin), tlatlacotin; '
     '-tzitzin reverential pl: pipiltzitzintin, macehualtzitzintin. '
     'Reduplication: te-teuctin (lords) = CV- reduplication of stem',
     'LOW (grammatical, not derivational) — but generator must select correct plural allomorph'],

    ['M14', 'inic subordinator (purpose / manner / causal / extent)',
     'Multi-function subordinating conjunction for purpose, manner, cause, and standard-of-comparison clauses',
     'Purpose: inic tamechpalehuizque (so that we help you); '
     'Manner: inic hueyac (as for its length / in terms of how long); '
     'Causal: inic oticmocniuhti (because you befriended); '
     'Extent: inic cempohualli (to the extent of twenty / meaning twenty of them)',
     'MEDIUM — essential for formal/legal Nahuatl document language; relevant for governance neologisms'],

    ['M15', 'yeppa (formerly / habitually / previously)',
     'Temporal adverb marking prior habitual or former state; contrasts with oc ceppa (again/future repetition)',
     'yeppa + verb = formerly/habitually did X (past habitual not covered by simple past). '
     'Contrasts: yeppa (was formerly) vs. oc ceppa (will do again) frames temporal axis of repetition. '
     'Also: ye huecauh (long ago), imoztlayoc (day before yesterday), huiptla (day after tomorrow)',
     'LOW — useful for historical/temporal neologisms but not core generator rule'],
]

ws2.update(values=MISSING, range_name='A1', value_input_option='RAW')
print(f"Missing Morphemes tab: {len(MISSING)-1} rows written.")

# Format the missing tab
req2 = [
    # Header row
    {'repeatCell': {
        'range': {'sheetId': ws2_id, 'startRowIndex': 0, 'endRowIndex': 1},
        'cell': {'userEnteredFormat': {
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'fontSize': 10},
            'backgroundColor': {'red': 0.55, 'green': 0.25, 'blue': 0.10},
            'horizontalAlignment': 'CENTER',
        }},
        'fields': 'userEnteredFormat(textFormat,backgroundColor,horizontalAlignment)',
    }},
    # Freeze row 1
    {'updateSheetProperties': {
        'properties': {'sheetId': ws2_id, 'gridProperties': {'frozenRowCount': 1}},
        'fields': 'gridProperties.frozenRowCount',
    }},
    # Data rows: wrap + top align
    {'repeatCell': {
        'range': {'sheetId': ws2_id, 'startRowIndex': 1},
        'cell': {'userEnteredFormat': {
            'wrapStrategy': 'WRAP', 'verticalAlignment': 'TOP',
            'textFormat': {'fontSize': 9},
        }},
        'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment,textFormat)',
    }},
    # Priority column colour coding
]
# HIGH priority rows (M1-M4, M11) → light red
HIGH_ROWS = [1, 2, 3, 4, 11]  # 1-indexed data rows
for r in HIGH_ROWS:
    req2.append({'repeatCell': {
        'range': {'sheetId': ws2_id, 'startRowIndex': r, 'endRowIndex': r+1},
        'cell': {'userEnteredFormat': {'backgroundColor': {'red': 0.99, 'green': 0.87, 'blue': 0.87}}},
        'fields': 'userEnteredFormat.backgroundColor',
    }})
# MEDIUM priority rows → light yellow
for r in [5, 6, 7, 8, 9, 10, 12, 13]:
    req2.append({'repeatCell': {
        'range': {'sheetId': ws2_id, 'startRowIndex': r, 'endRowIndex': r+1},
        'cell': {'userEnteredFormat': {'backgroundColor': {'red': 0.99, 'green': 0.97, 'blue': 0.85}}},
        'fields': 'userEnteredFormat.backgroundColor',
    }})
# LOW priority → light grey
for r in [14, 15]:
    req2.append({'repeatCell': {
        'range': {'sheetId': ws2_id, 'startRowIndex': r, 'endRowIndex': r+1},
        'cell': {'userEnteredFormat': {'backgroundColor': {'red': 0.94, 'green': 0.94, 'blue': 0.94}}},
        'fields': 'userEnteredFormat.backgroundColor',
    }})
# Column widths
for col_i, px in [(0,40),(1,180),(2,200),(3,350),(4,160)]:
    req2.append({'updateDimensionProperties': {
        'range': {'sheetId': ws2_id, 'dimension': 'COLUMNS',
                  'startIndex': col_i, 'endIndex': col_i+1},
        'properties': {'pixelSize': px},
        'fields': 'pixelSize',
    }})

sheets_svc.spreadsheets().batchUpdate(
    spreadsheetId=SHEET_ID,
    body={'requests': req2}
).execute()
print("Missing Morphemes tab formatted.")

print(f"\nDone!")
print(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
