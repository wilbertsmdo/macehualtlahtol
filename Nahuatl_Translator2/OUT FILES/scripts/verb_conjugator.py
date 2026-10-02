"""
verb_conjugator.py — English verb → Nahuatl conjugation system.
Detects English verb tense, finds infinitive, looks up Nahuatl root,
and conjugates using Nahuatl subject prefixes.

Based on IDIEZ Huasteca Nahuatl grammar (N1 unidades 5-6, p.67).
"""

import re

# ============================================================
# 1. ENGLISH VERB → INFINITIVE + TENSE DETECTION
# ============================================================

VERB_FORMS = {
    # (conjugated_form, infinitive, tense)
    # --- be ---
    "am": ("be", "present"), "is": ("be", "present"), "are": ("be", "present"),
    "was": ("be", "past"), "were": ("be", "past"),
    "been": ("be", "past_participle"), "being": ("be", "present_participle"),
    # --- have ---
    "has": ("have", "present"), "had": ("have", "past"),
    "having": ("have", "present_participle"),
    # --- do ---
    "does": ("do", "present"), "did": ("do", "past"),
    "doing": ("do", "present_participle"),
    # --- go ---
    "goes": ("go", "present"), "went": ("go", "past"),
    "gone": ("go", "past_participle"), "going": ("go", "present_participle"),
    # --- come ---
    "comes": ("come", "present"), "came": ("come", "past"),
    "coming": ("come", "present_participle"),
    # --- see ---
    "sees": ("see", "present"), "saw": ("see", "past"),
    "seen": ("see", "past_participle"), "seeing": ("see", "present_participle"),
    # --- know ---
    "knows": ("know", "present"), "knew": ("know", "past"),
    "known": ("know", "past_participle"), "knowing": ("know", "present_participle"),
    # --- think ---
    "thinks": ("think", "present"), "thought": ("think", "past"),
    "thinking": ("think", "present_participle"),
    # --- say ---
    "says": ("say", "present"), "said": ("say", "past"),
    "saying": ("say", "present_participle"),
    # --- tell ---
    "tells": ("tell", "present"), "told": ("tell", "past"),
    "telling": ("tell", "present_participle"),
    # --- speak ---
    "speaks": ("speak", "present"), "spoke": ("speak", "past"),
    "spoken": ("speak", "past_participle"), "speaking": ("speak", "present_participle"),
    # --- talk ---
    "talks": ("talk", "present"), "talked": ("talk", "past"),
    "talking": ("talk", "present_participle"),
    # --- ask ---
    "asks": ("ask", "present"), "asked": ("ask", "past"),
    "asking": ("ask", "present_participle"),
    # --- give ---
    "gives": ("give", "present"), "gave": ("give", "past"),
    "given": ("give", "past_participle"), "giving": ("give", "present_participle"),
    # --- take ---
    "takes": ("take", "present"), "took": ("take", "past"),
    "taken": ("take", "past_participle"), "taking": ("take", "present_participle"),
    # --- make ---
    "makes": ("make", "present"), "made": ("make", "past"),
    "making": ("make", "present_participle"),
    # --- get ---
    "gets": ("get", "present"), "got": ("get", "past"),
    "gotten": ("get", "past_participle"), "getting": ("get", "present_participle"),
    # --- find ---
    "finds": ("find", "present"), "found": ("find", "past"),
    "finding": ("find", "present_participle"),
    # --- want ---
    "wants": ("want", "present"), "wanted": ("want", "past"),
    "wanting": ("want", "present_participle"),
    # --- use ---
    "uses": ("use", "present"), "used": ("use", "past"),
    "using": ("use", "present_participle"),
    # --- try ---
    "tries": ("try", "present"), "tried": ("try", "past"),
    "trying": ("try", "present_participle"),
    # --- call ---
    "calls": ("call", "present"), "called": ("call", "past"),
    "calling": ("call", "present_participle"),
    # --- work ---
    "works": ("work", "present"), "worked": ("work", "past"),
    "working": ("work", "present_participle"),
    # --- seem ---
    "seems": ("seem", "present"), "seemed": ("seem", "past"),
    "seeming": ("seem", "present_participle"),
    # --- feel ---
    "feels": ("feel", "present"), "felt": ("feel", "past"),
    "feeling": ("feel", "present_participle"),
    # --- put ---
    "puts": ("put", "present"), "putting": ("put", "present_participle"),
    # --- set ---
    "sets": ("set", "present"), "setting": ("set", "present_participle"),
    # --- let ---
    "lets": ("let", "present"), "letting": ("let", "present_participle"),
    # --- keep ---
    "keeps": ("keep", "present"), "kept": ("keep", "past"),
    "keeping": ("keep", "present_participle"),
    # --- hold ---
    "holds": ("hold", "present"), "held": ("hold", "past"),
    "holding": ("hold", "present_participle"),
    # --- bring ---
    "brings": ("bring", "present"), "brought": ("bring", "past"),
    "bringing": ("bring", "present_participle"),
    # --- show ---
    "shows": ("show", "present"), "showed": ("show", "past"),
    "shown": ("show", "past_participle"), "showing": ("show", "present_participle"),
    # --- hear ---
    "hears": ("hear", "present"), "heard": ("hear", "past"),
    "hearing": ("hear", "present_participle"),
    # --- run ---
    "runs": ("run", "present"), "ran": ("run", "past"),
    "running": ("run", "present_participle"),
    # --- move ---
    "moves": ("move", "present"), "moved": ("move", "past"),
    "moving": ("move", "present_participle"),
    # --- live ---
    "lives": ("live", "present"), "lived": ("live", "past"),
    "living": ("live", "present_participle"),
    # --- believe ---
    "believes": ("believe", "present"), "believed": ("believe", "past"),
    "believing": ("believe", "present_participle"),
    # --- happen ---
    "happens": ("happen", "present"), "happened": ("happen", "past"),
    "happening": ("happen", "present_participle"),
    # --- write ---
    "writes": ("write", "present"), "wrote": ("write", "past"),
    "written": ("write", "past_participle"), "writing": ("write", "present_participle"),
    # --- read ---
    "reads": ("read", "present"), "reading": ("read", "present_participle"),
    # --- learn ---
    "learns": ("learn", "present"), "learned": ("learn", "past"),
    "learning": ("learn", "present_participle"),
    # --- teach ---
    "teaches": ("teach", "present"), "taught": ("teach", "past"),
    "teaching": ("teach", "present_participle"),
    # --- understand ---
    "understands": ("understand", "present"), "understood": ("understand", "past"),
    "understanding": ("understand", "present_participle"),
    # --- begin ---
    "begins": ("begin", "present"), "began": ("begin", "past"),
    "begun": ("begin", "past_participle"), "beginning": ("begin", "present_participle"),
    # --- grow ---
    "grows": ("grow", "present"), "grew": ("grow", "past"),
    "grown": ("grow", "past_participle"), "growing": ("grow", "present_participle"),
    # --- stand ---
    "stands": ("stand", "present"), "stood": ("stand", "past"),
    "standing": ("stand", "present_participle"),
    # --- fall ---
    "falls": ("fall", "present"), "fell": ("fall", "past"),
    "fallen": ("fall", "past_participle"), "falling": ("fall", "present_participle"),
    # --- lose ---
    "loses": ("lose", "present"), "lost": ("lose", "past"),
    "losing": ("lose", "present_participle"),
    # --- pay ---
    "pays": ("pay", "present"), "paid": ("pay", "past"),
    "paying": ("pay", "present_participle"),
    # --- meet ---
    "meets": ("meet", "present"), "met": ("meet", "past"),
    "meeting": ("meet", "present_participle"),
    # --- sit ---
    "sits": ("sit", "present"), "sat": ("sit", "past"),
    "sitting": ("sit", "present_participle"),
    # --- lead ---
    "leads": ("lead", "present"), "led": ("lead", "past"),
    "leading": ("lead", "present_participle"),
    # --- mean ---
    "means": ("mean", "present"), "meant": ("mean", "past"),
    "meaning": ("mean", "present_participle"),
    # --- build ---
    "builds": ("build", "present"), "built": ("build", "past"),
    "building": ("build", "present_participle"),
    # --- buy ---
    "buys": ("buy", "present"), "bought": ("buy", "past"),
    "buying": ("buy", "present_participle"),
    # --- sell ---
    "sells": ("sell", "present"), "sold": ("sell", "past"),
    "selling": ("sell", "present_participle"),
    # --- send ---
    "sends": ("send", "present"), "sent": ("send", "past"),
    "sending": ("send", "present_participle"),
    # --- spend ---
    "spends": ("spend", "present"), "spent": ("spend", "past"),
    "spending": ("spend", "present_participle"),
    # --- leave ---
    "leaves": ("leave", "present"), "left": ("leave", "past"),
    "leaving": ("leave", "present_participle"),
    # --- sleep ---
    "sleeps": ("sleep", "present"), "slept": ("sleep", "past"),
    "sleeping": ("sleep", "present_participle"),
    # --- lay ---
    "lays": ("lay", "present"), "laid": ("lay", "past"),
    "laying": ("lay", "present_participle"),
    # --- catch ---
    "catches": ("catch", "present"), "caught": ("catch", "past"),
    "catching": ("catch", "present_participle"),
    # --- fight ---
    "fights": ("fight", "present"), "fought": ("fight", "past"),
    "fighting": ("fight", "present_participle"),
    # --- seek ---
    "seeks": ("seek", "present"), "sought": ("seek", "past"),
    "seeking": ("seek", "present_participle"),
    # --- strike ---
    "strikes": ("strike", "present"), "struck": ("strike", "past"),
    "striking": ("strike", "present_participle"),
    # --- win ---
    "wins": ("win", "present"), "won": ("win", "past"),
    "winning": ("win", "present_participle"),
    # --- bind ---
    "binds": ("bind", "present"), "bound": ("bind", "past"),
    "binding": ("bind", "present_participle"),
    # --- dig ---
    "digs": ("dig", "present"), "dug": ("dig", "past"),
    "digging": ("dig", "present_participle"),
    # --- hang ---
    "hangs": ("hang", "present"), "hung": ("hang", "past"),
    "hanging": ("hang", "present_participle"),
    # --- stick ---
    "sticks": ("stick", "present"), "stuck": ("stick", "past"),
    "sticking": ("stick", "present_participle"),
    # --- sting ---
    "stings": ("sting", "present"), "stung": ("sting", "past"),
    "stinging": ("sting", "present_participle"),
    # --- swing ---
    "swings": ("swing", "present"), "swung": ("swing", "past"),
    "swinging": ("swing", "present_participle"),
    # --- spin ---
    "spins": ("spin", "present"), "spun": ("spin", "past"),
    "spinning": ("spin", "present_participle"),
    # --- slide ---
    "slides": ("slide", "present"), "slid": ("slide", "past"),
    "sliding": ("slide", "present_participle"),
    # --- spit ---
    "spits": ("spit", "present"), "spat": ("spit", "past"),
    "spitting": ("spit", "present_participle"),
    # --- split ---
    "splits": ("split", "present"), "splitting": ("split", "present_participle"),
    # --- spread ---
    "spreads": ("spread", "present"), "spreading": ("spread", "present_participle"),
    # --- shed ---
    "sheds": ("shed", "present"), "shedding": ("shed", "present_participle"),
    # --- bet ---
    "bets": ("bet", "present"), "betting": ("bet", "present_participle"),
    # --- cut ---
    "cuts": ("cut", "present"), "cutting": ("cut", "present_participle"),
    # --- hit ---
    "hits": ("hit", "present"), "hitting": ("hit", "present_participle"),
    # --- hurt ---
    "hurts": ("hurt", "present"), "hurting": ("hurt", "present_participle"),
    # --- cost ---
    "costs": ("cost", "present"), "costing": ("cost", "present_participle"),
    # --- cast ---
    "casts": ("cast", "present"), "casting": ("cast", "present_participle"),
    # --- thrust ---
    "thrusts": ("thrust", "present"), "thrusting": ("thrust", "present_participle"),
    # --- quit ---
    "quits": ("quit", "present"), "quitting": ("quit", "present_participle"),
    # --- shut ---
    "shuts": ("shut", "present"), "shutting": ("shut", "present_participle"),
    # --- rid ---
    "rids": ("rid", "present"), "ridding": ("rid", "present_participle"),
    # --- bleed ---
    "bleeds": ("bleed", "present"), "bled": ("bleed", "past"),
    "bleeding": ("bleed", "present_participle"),
    # --- breed ---
    "breeds": ("breed", "present"), "bred": ("breed", "past"),
    "breeding": ("breed", "present_participle"),
    # --- feed ---
    "feeds": ("feed", "present"), "fed": ("feed", "past"),
    "feeding": ("feed", "present_participle"),
    # --- speed ---
    "speeds": ("speed", "present"), "sped": ("speed", "past"),
    "speeding": ("speed", "present_participle"),
    # --- light ---
    "lights": ("light", "present"), "lit": ("light", "past"),
    "lighting": ("light", "present_participle"),
    # --- string ---
    "strings": ("string", "present"), "strung": ("string", "past"),
    "stringing": ("string", "present_participle"),
    # --- cling ---
    "clings": ("cling", "present"), "clung": ("cling", "past"),
    "clinging": ("cling", "present_participle"),
    # --- fling ---
    "flings": ("fling", "present"), "flung": ("fling", "past"),
    "flinging": ("fling", "present_participle"),
    # --- sling ---
    "slings": ("sling", "present"), "slung": ("sling", "past"),
    "slinging": ("sling", "present_participle"),
    # --- wring ---
    "wrings": ("wring", "present"), "wrung": ("wring", "past"),
    "wringing": ("wring", "present_participle"),
    # --- grind ---
    "grinds": ("grind", "present"), "ground": ("grind", "past"),
    "grinding": ("grind", "present_participle"),
    # --- wind ---
    "winds": ("wind", "present"), "wound": ("wind", "past"),
    "winding": ("wind", "present_participle"),
    # --- eat ---
    "eats": ("eat", "present"), "ate": ("eat", "past"),
    "eaten": ("eat", "past_participle"), "eating": ("eat", "present_participle"),
    # --- drink ---
    "drinks": ("drink", "present"), "drank": ("drink", "past"),
    "drunk": ("drink", "past_participle"), "drinking": ("drink", "present_participle"),
    # --- fly ---
    "flies": ("fly", "present"), "flew": ("fly", "past"),
    "flown": ("fly", "past_participle"), "flying": ("fly", "present_participle"),
    # --- swim ---
    "swims": ("swim", "present"), "swam": ("swim", "past"),
    "swum": ("swim", "past_participle"), "swimming": ("swim", "present_participle"),
    # --- drive ---
    "drives": ("drive", "present"), "drove": ("drive", "past"),
    "driven": ("drive", "past_participle"), "driving": ("drive", "present_participle"),
    # --- ride ---
    "rides": ("ride", "present"), "rode": ("ride", "past"),
    "ridden": ("ride", "past_participle"), "riding": ("ride", "present_participle"),
    # --- sing ---
    "sings": ("sing", "present"), "sang": ("sing", "past"),
    "sung": ("sing", "past_participle"), "singing": ("sing", "present_participle"),
    # --- draw ---
    "draws": ("draw", "present"), "drew": ("draw", "past"),
    "drawn": ("draw", "past_participle"), "drawing": ("draw", "present_participle"),
    # --- throw ---
    "throws": ("throw", "present"), "threw": ("throw", "past"),
    "thrown": ("throw", "past_participle"), "throwing": ("throw", "present_participle"),
    # --- blow ---
    "blows": ("blow", "present"), "blew": ("blow", "past"),
    "blown": ("blow", "past_participle"), "blowing": ("blow", "present_participle"),
    # --- break ---
    "breaks": ("break", "present"), "broke": ("break", "past"),
    "broken": ("break", "past_participle"), "breaking": ("break", "present_participle"),
    # --- choose ---
    "chooses": ("choose", "present"), "chose": ("choose", "past"),
    "chosen": ("choose", "past_participle"), "choosing": ("choose", "present_participle"),
    # --- freeze ---
    "freezes": ("freeze", "present"), "froze": ("freeze", "past"),
    "frozen": ("freeze", "past_participle"), "freezing": ("freeze", "present_participle"),
    # --- wake ---
    "wakes": ("wake", "present"), "woke": ("wake", "past"),
    "woken": ("wake", "past_participle"), "waking": ("wake", "present_participle"),
    # --- wear ---
    "wears": ("wear", "present"), "wore": ("wear", "past"),
    "worn": ("wear", "past_participle"), "wearing": ("wear", "present_participle"),
    # --- become ---
    "becomes": ("become", "present"), "became": ("become", "past"),
    "becoming": ("become", "present_participle"),
    # --- rise ---
    "rises": ("rise", "present"), "rose": ("rise", "past"),
    "risen": ("rise", "past_participle"), "rising": ("rise", "present_participle"),
    # --- shake ---
    "shakes": ("shake", "present"), "shook": ("shake", "past"),
    "shaken": ("shake", "past_participle"), "shaking": ("shake", "present_participle"),
    # --- steal ---
    "steals": ("steal", "present"), "stole": ("steal", "past"),
    "stolen": ("steal", "past_participle"), "stealing": ("steal", "present_participle"),
    # --- forget ---
    "forgets": ("forget", "present"), "forgot": ("forget", "past"),
    "forgotten": ("forget", "past_participle"), "forgetting": ("forget", "present_participle"),
    # --- forgive ---
    "forgives": ("forgive", "present"), "forgave": ("forgive", "past"),
    "forgiven": ("forgive", "past_participle"), "forgiving": ("forgive", "present_participle"),
    # --- hide ---
    "hides": ("hide", "present"), "hid": ("hide", "past"),
    "hidden": ("hide", "past_participle"), "hiding": ("hide", "present_participle"),
    # --- bite ---
    "bites": ("bite", "present"), "bit": ("bite", "past"),
    "bitten": ("bite", "past_participle"), "biting": ("bite", "present_participle"),
    # --- shine ---
    "shines": ("shine", "present"), "shone": ("shine", "past"),
    "shining": ("shine", "present_participle"),
    # --- sink ---
    "sinks": ("sink", "present"), "sank": ("sink", "past"),
    "sunk": ("sink", "past_participle"), "sinking": ("sink", "present_participle"),
    # --- creep ---
    "creeps": ("creep", "present"), "crept": ("creep", "past"),
    "creeping": ("creep", "present_participle"),
    # --- sweep ---
    "sweeps": ("sweep", "present"), "swept": ("sweep", "past"),
    "sweeping": ("sweep", "present_participle"),
    # --- weep ---
    "weeps": ("weep", "present"), "wept": ("weep", "past"),
    "weeping": ("weep", "present_participle"),
    # --- flee ---
    "flees": ("flee", "present"), "fled": ("flee", "past"),
    "fleeing": ("flee", "present_participle"),
    # --- lend ---
    "lends": ("lend", "present"), "lent": ("lend", "past"),
    "lending": ("lend", "present_participle"),
    # --- deal ---
    "deals": ("deal", "present"), "dealt": ("deal", "past"),
    "dealing": ("deal", "present_participle"),
    # --- bend ---
    "bends": ("bend", "present"), "bent": ("bend", "past"),
    "bending": ("bend", "present_participle"),
    # --- prove ---
    "proves": ("prove", "present"), "proved": ("prove", "past"),
    "proven": ("prove", "past_participle"), "proving": ("prove", "present_participle"),
    # --- mistake ---
    "mistakes": ("mistake", "present"), "mistook": ("mistake", "past"),
    "mistaken": ("mistake", "past_participle"), "mistaking": ("mistake", "present_participle"),
    # --- undertake ---
    "undertakes": ("undertake", "present"), "undertook": ("undertake", "past"),
    "undertaken": ("undertake", "past_participle"), "undertaking": ("undertake", "present_participle"),
    # --- withstand ---
    "withstands": ("withstand", "present"), "withstood": ("withstand", "past"),
    "withstanding": ("withstand", "present_participle"),
    # --- upset ---
    "upsets": ("upset", "present"), "upsetting": ("upset", "present_participle"),
    # --- broadcast ---
    "broadcasts": ("broadcast", "present"), "broadcasting": ("broadcast", "present_participle"),
    # --- mislead ---
    "misleads": ("mislead", "present"), "misled": ("mislead", "past"),
    "misleading": ("mislead", "present_participle"),
    # --- overtake ---
    "overtakes": ("overtake", "present"), "overtook": ("overtake", "past"),
    "overtaken": ("overtake", "past_participle"), "overtaking": ("overtake", "present_participle"),
    # --- burst ---
    "bursts": ("burst", "present"), "bursting": ("burst", "present_participle"),
    # --- forbid ---
    "forbids": ("forbid", "present"), "forbade": ("forbid", "past"),
    "forbidden": ("forbid", "past_participle"), "forbidding": ("forbid", "present_participle"),
    # --- lie ---
    "lies": ("lie", "present"), "lay": ("lie", "past"),
    "lain": ("lie", "past_participle"), "lying": ("lie", "present_participle"),
    # --- provide ---
    "provides": ("provide", "present"), "provided": ("provide", "past"),
    "providing": ("provide", "present_participle"),
    # --- require ---
    "requires": ("require", "present"), "required": ("require", "past"),
    "requiring": ("require", "present_participle"),
    # --- suppose ---
    "supposes": ("suppose", "present"), "supposed": ("suppose", "past"),
    "supposing": ("suppose", "present_participle"),
    # --- answer ---
    "answers": ("answer", "present"), "answered": ("answer", "past"),
    "answering": ("answer", "present_participle"),
    # --- die ---
    "dies": ("die", "present"), "died": ("die", "past"),
    "dying": ("die", "present_participle"),
    # --- kill ---
    "kills": ("kill", "present"), "killed": ("kill", "past"),
    "killing": ("kill", "present_participle"),
    # --- love ---
    "loves": ("love", "present"), "loved": ("love", "past"),
    "loving": ("love", "present_participle"),
    # --- hate ---
    "hates": ("hate", "present"), "hated": ("hate", "past"),
    "hating": ("hate", "present_participle"),
    # --- help ---
    "helps": ("help", "present"), "helped": ("help", "past"),
    "helping": ("help", "present_participle"),
    # --- hope ---
    "hopes": ("hope", "present"), "hoped": ("hope", "past"),
    "hoping": ("hope", "present_participle"),
    # --- fear ---
    "fears": ("fear", "present"), "feared": ("fear", "past"),
    "fearing": ("fear", "present_participle"),
    # --- cry ---
    "cries": ("cry", "present"), "cried": ("cry", "past"),
    "crying": ("cry", "present_participle"),
    # --- laugh ---
    "laughs": ("laugh", "present"), "laughed": ("laugh", "past"),
    "laughing": ("laugh", "present_participle"),
    # --- smile ---
    "smiles": ("smile", "present"), "smiled": ("smile", "past"),
    "smiling": ("smile", "present_participle"),
    # --- shout ---
    "shouts": ("shout", "present"), "shouted": ("shout", "past"),
    "shouting": ("shout", "present_participle"),
    # --- whisper ---
    "whispers": ("whisper", "present"), "whispered": ("whisper", "past"),
    "whispering": ("whisper", "present_participle"),
    # --- promise ---
    "promises": ("promise", "present"), "promised": ("promise", "past"),
    "promising": ("promise", "present_participle"),
    # --- agree ---
    "agrees": ("agree", "present"), "agreed": ("agree", "past"),
    "agreeing": ("agree", "present_participle"),
    # --- refuse ---
    "refuses": ("refuse", "present"), "refused": ("refuse", "past"),
    "refusing": ("refuse", "present_participle"),
    # --- allow ---
    "allows": ("allow", "present"), "allowed": ("allow", "past"),
    "allowing": ("allow", "present_participle"),
    # --- order ---
    "orders": ("order", "present"), "ordered": ("order", "past"),
    "ordering": ("order", "present_participle"),
    # --- beg ---
    "begs": ("beg", "present"), "begged": ("beg", "past"),
    "begging": ("beg", "present_participle"),
    # --- warn ---
    "warns": ("warn", "present"), "warned": ("warn", "past"),
    "warning": ("warn", "present_participle"),
    # --- advise ---
    "advises": ("advise", "present"), "advised": ("advise", "past"),
    "advising": ("advise", "present_participle"),
    # --- suggest ---
    "suggests": ("suggest", "present"), "suggested": ("suggest", "past"),
    "suggesting": ("suggest", "present_participle"),
    # --- explain ---
    "explains": ("explain", "present"), "explained": ("explain", "past"),
    "explaining": ("explain", "present_participle"),
    # --- describe ---
    "describes": ("describe", "present"), "described": ("describe", "past"),
    "describing": ("describe", "present_participle"),
    # --- count ---
    "counts": ("count", "present"), "counted": ("count", "past"),
    "counting": ("count", "present_participle"),
    # --- measure ---
    "measures": ("measure", "present"), "measured": ("measure", "past"),
    "measuring": ("measure", "present_participle"),
    # --- mix ---
    "mixes": ("mix", "present"), "mixed": ("mix", "past"),
    "mixing": ("mix", "present_participle"),
    # --- cook ---
    "cooks": ("cook", "present"), "cooked": ("cook", "past"),
    "cooking": ("cook", "present_participle"),
    # --- bake ---
    "bakes": ("bake", "present"), "baked": ("bake", "past"),
    "baking": ("bake", "present_participle"),
    # --- boil ---
    "boils": ("boil", "present"), "boiled": ("boil", "past"),
    "boiling": ("boil", "present_participle"),
    # --- fry ---
    "fries": ("fry", "present"), "fried": ("fry", "past"),
    "frying": ("fry", "present_participle"),
    # --- wash ---
    "washes": ("wash", "present"), "washed": ("wash", "past"),
    "washing": ("wash", "present_participle"),
    # --- clean ---
    "cleans": ("clean", "present"), "cleaned": ("clean", "past"),
    "cleaning": ("clean", "present_participle"),
    # --- dry ---
    "dries": ("dry", "present"), "dried": ("dry", "past"),
    "drying": ("dry", "present_participle"),
    # --- burn ---
    "burns": ("burn", "present"), "burned": ("burn", "past"),
    "burnt": ("burn", "past"), "burning": ("burn", "present_participle"),
    # --- melt ---
    "melts": ("melt", "present"), "melted": ("melt", "past"),
    "melting": ("melt", "present_participle"),
    # --- flow ---
    "flows": ("flow", "present"), "flowed": ("flow", "past"),
    "flowing": ("flow", "present_participle"),
    # --- pour ---
    "pours": ("pour", "present"), "poured": ("pour", "past"),
    "pouring": ("pour", "present_participle"),
    # --- fill ---
    "fills": ("fill", "present"), "filled": ("fill", "past"),
    "filling": ("fill", "present_participle"),
    # --- empty ---
    "empties": ("empty", "present"), "emptied": ("empty", "past"),
    "emptying": ("empty", "present_participle"),
    # --- tie ---
    "ties": ("tie", "present"), "tied": ("tie", "past"),
    "tying": ("tie", "present_participle"),
    # --- loose ---
    "looses": ("loose", "present"), "loosed": ("loose", "past"),
    "loosing": ("loose", "present_participle"),
    # --- free ---
    "frees": ("free", "present"), "freed": ("free", "past"),
    "freeing": ("free", "present_participle"),
    # --- hunt ---
    "hunts": ("hunt", "present"), "hunted": ("hunt", "past"),
    "hunting": ("hunt", "present_participle"),
    # --- plant ---
    "plants": ("plant", "present"), "planted": ("plant", "past"),
    "planting": ("plant", "present_participle"),
    # --- harvest ---
    "harvests": ("harvest", "present"), "harvested": ("harvest", "past"),
    "harvesting": ("harvest", "present_participle"),
    # --- bury ---
    "buries": ("bury", "present"), "buried": ("bury", "past"),
    "burying": ("bury", "present_participle"),
    # --- cover ---
    "covers": ("cover", "present"), "covered": ("cover", "past"),
    "covering": ("cover", "present_participle"),
    # --- wrap ---
    "wraps": ("wrap", "present"), "wrapped": ("wrap", "past"),
    "wrapping": ("wrap", "present_participle"),
    # --- fold ---
    "folds": ("fold", "present"), "folded": ("fold", "past"),
    "folding": ("fold", "present_participle"),
    # --- bend ---
    "bends": ("bend", "present"), "bent": ("bend", "past"),
    "bending": ("bend", "present_participle"),
    # --- stretch ---
    "stretches": ("stretch", "present"), "stretched": ("stretch", "past"),
    "stretching": ("stretch", "present_participle"),
    # --- reach ---
    "reaches": ("reach", "present"), "reached": ("reach", "past"),
    "reaching": ("reach", "present_participle"),
    # --- touch ---
    "touches": ("touch", "present"), "touched": ("touch", "past"),
    "touching": ("touch", "present_participle"),
    # --- press ---
    "presses": ("press", "present"), "pressed": ("press", "past"),
    "pressing": ("press", "present_participle"),
    # --- crush ---
    "crushes": ("crush", "present"), "crushed": ("crush", "past"),
    "crushing": ("crush", "present_participle"),
    # --- tremble ---
    "trembles": ("tremble", "present"), "trembled": ("tremble", "past"),
    "trembling": ("tremble", "present_participle"),
    # --- glow ---
    "glows": ("glow", "present"), "glowed": ("glow", "past"),
    "glowing": ("glow", "present_participle"),
    # --- darken ---
    "darkens": ("darken", "present"), "darkened": ("darken", "past"),
    "darkening": ("darken", "present_participle"),
    # --- brighten ---
    "brightens": ("brighten", "present"), "brightened": ("brighten", "past"),
    "brightening": ("brighten", "present_participle"),
    # --- clear ---
    "clears": ("clear", "present"), "cleared": ("clear", "past"),
    "clearing": ("clear", "present_participle"),
    # --- rain ---
    "rains": ("rain", "present"), "rained": ("rain", "past"),
    "raining": ("rain", "present_participle"),
    # --- snow ---
    "snows": ("snow", "present"), "snowed": ("snow", "past"),
    "snowing": ("snow", "present_participle"),
    # --- thunder ---
    "thunders": ("thunder", "present"), "thundered": ("thunder", "past"),
    "thundering": ("thunder", "present_participle"),
}

# ============================================================
# 2. REGULAR VERB PATTERN DETECTION
#    For verbs not in the explicit list above.
# ============================================================

def detect_regular_verb(word):
    """Detect if word is a regular English verb form.
    Returns (infinitive, tense) or (None, None)."""
    w = word.lower()

    # -ing form
    if w.endswith("ing") and len(w) > 5:
        root = w[:-3]
        # Handle doubled consonant: running -> run
        if len(root) >= 2 and root[-1] == root[-2]:
            root = root[:-1]
        # Handle -ie → -y: dying → die
        if root.endswith("i"):
            root = root[:-1] + "e"
        return root, "present_participle"

    # -ed form (past/past_participle)
    if w.endswith("ed") and len(w) > 4:
        root = w[:-2]
        if root.endswith("e"):
            root = root[:-1]
        return root, "past"

    # -s form (3rd person present)
    if w.endswith("ies") and len(w) > 5:
        root = w[:-3] + "y"
        return root, "present"
    if w.endswith("es") and len(w) > 4:
        root = w[:-2]
        return root, "present"
    if w.endswith("s") and len(w) > 3 and not w.endswith("ss"):
        root = w[:-1]
        return root, "present"

    return None, None

# ============================================================
# 3. NAHUATL CONJUGATION
#    Subject prefixes + verb root + tense markers
#    Based on IDIEZ Huasteca Nahuatl (N1 unidades 5-6, p.67)
# ============================================================

# Subject prefixes for regular verbs
SUBJECT_PREFIX = {
    "i": "ni",
    "you": "ti",
    "he": "",
    "she": "",
    "it": "",
    "we": "ti",
    "they": "",
}

# Plural suffixes
PLURAL_SUFFIX = {
    "we": "h",
    "they": "h",
}

# Tense markers for regular verbs
TENSE_MARKER = {
    "present": "",
    "past": "c",       # -c for past (perfective)
    "future": "z",     # -z for future
    "present_participle": "a",  # -a for progressive
    "past_participle": "c",     # -c for perfect
}

def conjugate_nahuatl(verb_root, subject, tense):
    """Conjugate a Nahuatl verb.
    
    Pattern: subject_prefix + verb_root + tense_marker + plural_suffix
    
    Nahuatl verb roots often end in -a, -i, -oa, -ia, -hua, etc.
    Tense markers interact with these endings:
      - Present: root as-is (or -a → -a)
      - Past: -a → -ac, -i → -ic, -oa → -oc, -ia → -iac
      - Future: -a → -az, -i → -iz, -oa → -oz, -ia → -iaz
      - Present participle: -a → -a (same), often needs context
      - Past participle: same as past
    
    Examples:
        ni + tequiti + Ø = nitequiti (I work)
        ti + tequiti + h = titequitih (we work)
        ni + tequiti + c = nitequitic (I worked)
        ni + tequiti + z = nitequitiz (I will work)
    """
    prefix = SUBJECT_PREFIX.get(subject, "")
    plural = PLURAL_SUFFIX.get(subject, "") if subject in ("we", "they") else ""

    # Clean the root
    root = verb_root.strip().rstrip('.')

    # Apply tense marker based on root ending
    if tense == "past" or tense == "past_participle":
        if root.endswith('a'):
            root = root + 'c'
        elif root.endswith('i'):
            root = root + 'c'
        elif root.endswith('oa'):
            root = root[:-1] + 'c'  # -oa → -oc
        elif root.endswith('ia'):
            root = root + 'c'  # -ia → -iac
        elif root.endswith('hua'):
            root = root[:-1] + 'c'  # -hua → -huc
        elif root.endswith('e'):
            root = root + 'c'
        elif root.endswith('o'):
            root = root + 'c'
        elif root.endswith('y'):
            root = root + 'c'
        else:
            root = root + 'c'
    elif tense == "future":
        if root.endswith('a'):
            root = root[:-1] + 'z'  # -a → -z
        elif root.endswith('i'):
            root = root[:-1] + 'z'  # -i → -z
        elif root.endswith('oa'):
            root = root[:-1] + 'z'  # -oa → -oz
        elif root.endswith('ia'):
            root = root[:-1] + 'z'  # -ia → -iaz
        elif root.endswith('hua'):
            root = root[:-1] + 'z'  # -hua → -huz
        elif root.endswith('e'):
            root = root[:-1] + 'z'
        elif root.endswith('o'):
            root = root[:-1] + 'z'
        elif root.endswith('y'):
            root = root[:-1] + 'z'
        else:
            root = root + 'z'
    elif tense == "present_participle":
        # Progressive often uses -a ending or -tia → -tia
        # For simplicity, keep root as-is for progressive
        pass

    # Build the conjugated form
    result = prefix + root + plural
    return result

# ============================================================
# 4. MAIN API
# ============================================================

def find_verb_info(word):
    """Find the infinitive and tense of an English verb.
    Returns (infinitive, tense) or (None, None)."""
    w = word.lower()

    # Check explicit forms first
    if w in VERB_FORMS:
        return VERB_FORMS[w]

    # Try regular verb patterns
    infinitive, tense = detect_regular_verb(w)
    if infinitive:
        return infinitive, tense

    return None, None


def translate_and_conjugate(word, subject, dictionary):
    """Translate an English verb to Nahuatl with proper conjugation.
    
    Args:
        word: English verb (any form)
        subject: Subject pronoun ("i", "you", "he", "she", "we", "they")
        dictionary: English→Nahuatl dictionary
    
    Returns:
        Conjugated Nahuatl verb, or None if not found.
    """
    infinitive, tense = find_verb_info(word)
    if not infinitive:
        return None

    def _get_nah(entry):
        """Extract Nahuatl word from dictionary entry (string or dict)."""
        if isinstance(entry, dict):
            return entry.get("nah", "")
        return entry

    # Look up the infinitive in the dictionary
    nah_root = _get_nah(dictionary.get(infinitive.lower()))
    if not nah_root:
        # Try synonyms
        from synonyms import SYNONYMS
        if infinitive.lower() in SYNONYMS:
            for syn in SYNONYMS[infinitive.lower()]:
                if syn in dictionary:
                    nah_root = _get_nah(dictionary[syn])
                    break

    if not nah_root:
        return None

    # Clean up the Nahuatl root (remove absolutive suffix if present)
    # Nahuatl verbs often end in -a, -i, -oa, -ia
    nah_root = nah_root.strip()

    # Conjugate
    result = conjugate_nahuatl(nah_root, subject, tense)
    return result
