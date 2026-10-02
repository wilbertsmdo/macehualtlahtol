"""
unknown_words.py — Track and manage unknown words from translation.

Workflow:
  1. Load known translations from unknown_words.json
  2. Use them during translation
  3. Save new unknown words after translation (filtering out proper names)
  4. User edits the JSON file to add Nahuatl translations
  5. Next run picks them up automatically
"""

import json
import os
import re

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unknown_words.json")

# Common proper name patterns to filter out
PROPER_NAME_PATTERNS = [
    # Common first names
    'samuel', 'john', 'jane', 'mary', 'james', 'robert', 'william', 'david',
    'richard', 'joseph', 'thomas', 'charles', 'christopher', 'daniel', 'michael',
    'mark', 'donald', 'george', 'kenneth', 'steven', 'edward', 'brian', 'ronald',
    'anthony', 'kevin', 'jason', 'matthew', 'gary', 'timothy', 'jose', 'larry',
    'jeffrey', 'frank', 'scott', 'eric', 'stephen', 'andrew', 'raymond', 'gregory',
    'joshua', 'jerry', 'dennis', 'walter', 'patrick', 'peter', 'harold', 'douglas',
    'henry', 'carl', 'arthur', 'ryan', 'roger', 'joe', 'juan', 'jack', 'albert',
    'jonathan', 'justin', 'terry', 'gerald', 'keith', 'samuel', 'willie', 'ralph',
    'lawrence', 'nicholas', 'roy', 'benjamin', 'bruce', 'brandon', 'adam', 'harry',
    'fred', 'wayne', 'billy', 'steve', 'louis', 'jeremy', 'aaron', 'randy',
    'eugene', 'carlos', 'russell', 'bobby', 'victor', 'martin', 'ernest', 'phillip',
    'todd', 'jesse', 'craig', 'alan', 'shawn', 'clarence', 'sean', 'philip',
    'chris', 'johnny', 'earl', 'jimmy', 'antonio', 'danny', 'bryan', 'tony',
    'luis', 'mike', 'stanley', 'leonard', 'nathan', 'dale', 'manuel', 'rodney',
    'curtis', 'norman', 'allen', 'marvin', 'vincent', 'glenn', 'jeffery', 'travis',
    'jeff', 'chad', 'jacob', 'melvin', 'alfred', 'kyle', 'francis', 'bradley',
    'jesus', 'herbert', 'frederick', 'ray', 'joel', 'edwin', 'don', 'eddie',
    'ricky', 'troy', 'randall', 'barry', 'alexander', 'bernard', 'mario', 'leroy',
    'francisco', 'marcus', 'micheal', 'theodore', 'clifford', 'miguel', 'oscar',
    'jay', 'jim', 'tom', 'calvin', 'alex', 'jon', 'ronnie', 'bill', 'lloyd',
    'tommy', 'leon', 'derek', 'darrell', 'jerome', 'floyd', 'dean', 'greg',
    'jorge', 'dustin', 'pedro', 'derrick', 'dan', 'zachary', 'corey', 'herman',
    'maurice', 'vernon', 'roberto', 'clyde', 'glen', 'hector', 'shane', 'ricardo',
    'sam', 'rick', 'lester', 'brent', 'ramon', 'charlie', 'tyler', 'gilbert',
    'gene', 'marc', 'reginald', 'ruben', 'brett', 'angel', 'nathaniel', 'rafael',
    'leslie', 'edgar', 'milton', 'raul', 'ben', 'chester', 'cecil', 'duane',
    'franklin', 'andre', 'elmer', 'brad', 'gabriel', 'ron', 'roland', 'arnold',
    'harvey', 'jared', 'adrian', 'karl', 'cory', 'claude', 'erik', 'darryl',
    'jamie', 'neil', 'jessie', 'christian', 'javier', 'fernando', 'clinton', 'ted',
    'mathew', 'tyrone', 'darren', 'lonnie', 'lance', 'cody', 'julio', 'kurt',
    'allan', 'nelson', 'guy', 'clayton', 'hugh', 'max', 'dwayne', 'dwight',
    'armando', 'felix', 'jimmie', 'everett', 'jordan', 'ian', 'wallace', 'ken',
    'bob', 'jaime', 'casey', 'alfredo', 'alberto', 'dave', 'ivan', 'johnnie',
    'sidney', 'byron', 'julian', 'isaac', 'clifton', 'willard', 'daryl', 'virgil',
    'andy', 'salvador', 'kirk', 'sergio', 'seth', 'kent', 'terrance', 'rene',
    'eduardo', 'terrence', 'enrique', 'freddie', 'stuart', 'fredrick', 'arturo',
    'alejandro', 'joey', 'nick', 'luther', 'wendell', 'jeremiah', 'evan', 'julius',
    'donnie', 'otis', 'shannon', 'trevor', 'luke', 'homer', 'gerard', 'doug',
    'kenny', 'hubert', 'angelo', 'shaun', 'lyle', 'matt', 'alfonso', 'orlando',
    'rex', 'carlton', 'ernesto', 'cameron', 'neal', 'pablo', 'lorenzo', 'omar',
    'wilbur', 'blake', 'grant', 'horace', 'roderick', 'kerry', 'abraham', 'rickey',
    'ira', 'andres', 'cesar', 'johnathan', 'malcolm', 'rudolph', 'damon', 'kelvin',
    'rudy', 'preston', 'alton', 'archie', 'marco', 'wm', 'pete', 'randolph',
    'garry', 'geoffrey', 'jonathon', 'felipe', 'bennie', 'gerardo', 'ed', 'dominic',
    'loren', 'delbert', 'colin', 'guillermo', 'earnest', 'lucas', 'benny', 'noel',
    'spencer', 'rodolfo', 'myron', 'edmund', 'salvatore', 'cedric', 'lowell', 'gregg',
    'sherman', 'wilson', 'devin', 'sylvester', 'kim', 'roosevelt', 'israel', 'jermaine',
    'forrest', 'wilbert', 'leland', 'simon', 'guadalupe', 'clark', 'irving', 'carroll',
    'bryant', 'owen', 'rufus', 'woodrow', 'sammy', 'kristopher', 'levi', 'marcos',
    'gustavo', 'jake', 'lionel', 'marty', 'ellis', 'dallas', 'gilberto', 'clint',
    'nicolas', 'laurence', 'ismael', 'orville', 'drew', 'ervin', 'dewey', 'al',
    'wilfred', 'josh', 'hugo', 'ignacio', 'caleb', 'tomas', 'sheldon', 'erick',
    'frankie', 'stewart', 'doyle', 'darrel', 'rogelio', 'terence', 'alonzo', 'elias',
    'bert', 'elbert', 'ramiro', 'conrad', 'pat', 'noah', 'grady', 'phil',
    'cornelius', 'lamar', 'rolando', 'clay', 'percy', 'bradford', 'merle', 'darin',
    'amos', 'terrell', 'moses', 'irvin', 'saul', 'roman', 'darnell', 'randal',
    'tommie', 'timmy', 'darrin', 'brendan', 'toby', 'van', 'abel', 'dominick',
    'emilio', 'elijah', 'cary', 'domingo', 'santos', 'aubrey', 'emmett', 'marlon',
    'emanuel', 'jerald', 'edmond',
    # Common last names
    'smith', 'johnson', 'williams', 'jones', 'brown', 'davis', 'miller', 'wilson',
    'moore', 'taylor', 'anderson', 'thomas', 'jackson', 'white', 'harris', 'martin',
    'thompson', 'garcia', 'martinez', 'robinson', 'clark', 'rodriguez', 'lewis', 'lee',
    'walker', 'hall', 'allen', 'young', 'hernandez', 'king', 'wright', 'lopez',
    'hill', 'scott', 'green', 'adams', 'baker', 'gonzalez', 'nelson', 'carter',
    'mitchell', 'perez', 'roberts', 'turner', 'phillips', 'campbell', 'parker', 'evans',
    'edwards', 'collins', 'stewart', 'sanchez', 'morris', 'rogers', 'reed', 'cook',
    'morgan', 'bell', 'murphy', 'bailey', 'rivera', 'cooper', 'richardson', 'cox',
    'howard', 'ward', 'torres', 'peterson', 'gray', 'ramirez', 'james', 'watson',
    'brooks', 'kelly', 'sanders', 'price', 'bennett', 'wood', 'barnes', 'ross',
    'henderson', 'coleman', 'jenkins', 'perry', 'powell', 'long', 'patterson', 'hughes',
    'flores', 'washington', 'butler', 'simmons', 'foster', 'gonzales', 'bryant', 'alexander',
    'russell', 'griffin', 'diaz', 'hayes', 'myers', 'ford', 'hamilton', 'graham',
    'sullivan', 'wallace', 'woods', 'cole', 'west', 'jordan', 'owens', 'reynolds',
    'fisher', 'ellis', 'harrison', 'gibson', 'mcdonald', 'cruz', 'marshall', 'ortiz',
    'gomez', 'murray', 'freeman', 'wells', 'webb', 'simpson', 'stevens', 'tucker',
    'porter', 'hicks', 'crawford', 'boyd', 'mason', 'morales', 'kennedy', 'warren',
    'dixon', 'ramos', 'reyes', 'burns', 'gordon', 'shaw', 'holmes', 'rice',
    'robertson', 'hunt', 'black', 'daniels', 'palmer', 'mills', 'nichols', 'grant',
    'knight', 'ferguson', 'rose', 'stone', 'hawkins', 'dunn', 'perkins', 'hudson',
    'spencer', 'gardner', 'stephens', 'payne', 'pierce', 'berry', 'matthews', 'arnold',
    'wagner', 'willis', 'ray', 'watkins', 'olson', 'carroll', 'duncan', 'snyder',
    'hart', 'cunningham', 'lane', 'andrews', 'ruiz', 'harper', 'fox', 'riley',
    'armstrong', 'carpenter', 'weaver', 'greene', 'elliott', 'chavez', 'sims', 'peters',
    'kelley', 'franklin', 'lawson', 'fields', 'gutierrez', 'schmidt', 'carr', 'vasquez',
    'castillo', 'wheeler', 'chapman', 'montgomery', 'richards', 'williamson', 'johnston', 'banks',
    'meyer', 'bishop', 'mccoy', 'howell', 'alvarez', 'morrison', 'hansen', 'fernandez',
    'garza', 'burton', 'nguyen', 'jacobs', 'reid', 'fuller', 'lynch', 'garrett',
    'romero', 'welch', 'larson', 'frazier', 'burke', 'hanson', 'mendoza', 'moreno',
    'bowman', 'medina', 'fowler', 'brewer', 'hoffman', 'carlson', 'silva', 'pearson',
    'holland', 'fleming', 'jensen', 'vargas', 'byrd', 'davidson', 'hopkins', 'herrera',
    'wade', 'soto', 'walters', 'neal', 'caldwell', 'lowe', 'jennings', 'barnett',
    'graves', 'jimenez', 'horton', 'shelton', 'barrett', 'obrien', 'castro', 'sutton',
    'mckinney', 'lucas', 'miles', 'rodriquez', 'chambers', 'holt', 'lambert', 'fletcher',
    'watts', 'bates', 'hale', 'rhodes', 'pena', 'beck', 'newman', 'haynes',
    'mcdaniel', 'mendez', 'bush', 'vaughn', 'parks', 'dawson', 'santiago', 'norris',
    'hardy', 'steele', 'curry', 'powers', 'schultz', 'barker', 'guzman', 'page',
    'munoz', 'ball', 'keller', 'chandler', 'weber', 'walsh', 'lyons', 'ramsey',
    'wolfe', 'schneider', 'mullins', 'benson', 'sharp', 'bowen', 'barber', 'cummings',
    'hines', 'baldwin', 'griffith', 'valdez', 'hubbard', 'salazar', 'reeves', 'warner',
    'stevenson', 'burgess', 'santos', 'tate', 'cross', 'garner', 'mann', 'mack',
    'moss', 'thornton', 'mcgee', 'farmer', 'delgado', 'aguilar', 'vega', 'glover',
    'manning', 'cohen', 'harmon', 'rodgers', 'robbins', 'newton', 'blair', 'higgins',
    'ingram', 'reese', 'cannon', 'strickland', 'townsend', 'potter', 'goodwin', 'walton',
    'rowe', 'hampton', 'ortega', 'patton', 'swanson', 'goodman', 'maldonado', 'yates',
    'becker', 'erickson', 'hodges', 'rios', 'conner', 'adkins', 'webster', 'malone',
    'hammond', 'flowers', 'cobb', 'moody', 'quinn', 'pope', 'osborne', 'mccarthy',
    # Common place names / organizations
    'philadelphia', 'washington', 'virginia', 'federalist', 'society', 'march',
    'america', 'english', 'spanish', 'french', 'german', 'italian', 'chinese',
    'japanese', 'mexican', 'canadian', 'european', 'african', 'asian',
    'london', 'paris', 'berlin', 'rome', 'madrid', 'tokyo', 'beijing',
    'moscow', 'cairo', 'delhi', 'mumbai', 'bangkok', 'seoul', 'sydney',
    'toronto', 'vancouver', 'montreal', 'boston', 'chicago', 'detroit', 'houston',
    'dallas', 'phoenix', 'san', 'francisco', 'los', 'angeles', 'new', 'york',
    'miami', 'atlanta', 'denver', 'seattle', 'portland', 'austin', 'nashville',
    'memphis', 'cleveland', 'pittsburgh', 'cincinnati', 'kansas', 'minneapolis',
    'tampa', 'orlando', 'charlotte', 'indianapolis', 'columbus', 'milwaukee',
    'oklahoma', 'louisville', 'baltimore', 'albuquerque', 'tucson', 'fresno',
    'sacramento', 'mesa', 'omaha', 'tulsa', 'honolulu', 'anaheim', 'santa',
    'arlington', 'corpus', 'christi', 'lexington', 'stockton', 'anchorage',
    'st', 'paul', 'rivera', 'plaza', 'avenue', 'street', 'boulevard',
    'university', 'college', 'institute', 'foundation', 'corporation', 'company',
    'incorporated', 'association', 'organization', 'department', 'agency', 'bureau',
    'commission', 'authority', 'board', 'council', 'committee', 'conference',
    'congress', 'senate', 'parliament', 'assembly', 'court', 'tribunal',
    'supreme', 'federal', 'state', 'national', 'international', 'global',
    'american', 'british', 'canadian', 'australian', 'indian', 'russian',
    'english', 'spanish', 'french', 'german', 'italian', 'portuguese',
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
    'january', 'february', 'march', 'april', 'may', 'june', 'july',
    'august', 'september', 'october', 'november', 'december',
]

# Set for fast lookup
PROPER_NAMES = set(PROPER_NAME_PATTERNS)


def is_proper_name(word):
    """Check if a word is likely a proper name."""
    w = word.lower().strip()

    # Check against known proper names
    if w in PROPER_NAMES:
        return True

    # Check for common name patterns
    # Words ending with common name suffixes
    if w.endswith(('ville', 'burg', 'ton', 'ham', 'shire', 'ford', 'worth')):
        return True

    # Words that look like dates/numbers
    if re.match(r'^\d+$', w):
        return True

    # Single letter words (except 'a' and 'i')
    if len(w) == 1 and w not in ('a', 'i'):
        return True

    return False


def filter_unknown_words(unknown_words, context_map=None):
    """Filter out proper names from unknown words.
    
    Returns:
        (filtered_unknown, filtered_context)
    """
    filtered = set()
    filtered_context = {}

    for word in unknown_words:
        if not is_proper_name(word):
            filtered.add(word)
            if context_map and word in context_map:
                filtered_context[word] = context_map[word]

    return filtered, filtered_context


def load_known_words(path=None):
    """Load previously translated unknown words.
    
    Returns a dict: {word_lower: nahuatl_translation}
    """
    path = path or DEFAULT_PATH
    if not os.path.exists(path):
        return {}

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    known = {}
    for entry in data:
        if entry.get("status") == "done" and entry.get("nahuatl"):
            known[entry["word"].lower()] = entry["nahuatl"]

    return known


def save_unknown_words(unknown_words, context_map=None, path=None):
    """Save unknown words to JSON file.
    
    Args:
        unknown_words: set of unknown word strings
        context_map: dict of {word: [list of sentences where it appeared]}
        path: output file path
    """
    path = path or DEFAULT_PATH

    # Filter out proper names
    filtered_unknown, filtered_context = filter_unknown_words(unknown_words, context_map)

    if not filtered_unknown:
        print("\n📝 No new unknown words (all were proper names)")
        return []

    # Load existing data to preserve user edits
    existing = []
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            existing = json.load(f)

    # Build lookup of existing words
    existing_words = {e["word"].lower() for e in existing}

    # Add new unknown words
    new_entries = []
    for word in sorted(filtered_unknown):
        if word.lower() not in existing_words:
            contexts = filtered_context.get(word.lower(), []) if filtered_context else []
            new_entries.append({
                "word": word.lower(),
                "context": contexts[:3] if contexts else [],
                "status": "pending",
                "nahuatl": "",
                "notes": ""
            })

    # Merge: keep existing entries, add new ones
    all_entries = existing + new_entries

    # Sort by status (pending first) then alphabetically
    all_entries.sort(key=lambda e: (0 if e["status"] == "pending" else 1, e["word"].lower()))

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print(f"\n📝 Unknown words saved to: {path}")
    print(f"   New words: {len(new_entries)} (filtered out {len(unknown_words) - len(filtered_unknown)} proper names)")
    print(f"   Total words: {len(all_entries)}")
    print(f"   Pending: {sum(1 for e in all_entries if e['status'] == 'pending')}")
    print(f"   Done: {sum(1 for e in all_entries if e['status'] == 'done')}")

    return all_entries


def print_unknown_summary(path=None):
    """Print a summary of unknown words status."""
    path = path or DEFAULT_PATH
    if not os.path.exists(path):
        print("No unknown words file found.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pending = [e for e in data if e["status"] == "pending"]
    done = [e for e in data if e["status"] == "done"]

    print(f"\n📊 Unknown Words Summary:")
    print(f"   Total: {len(data)}")
    print(f"   Pending: {len(pending)}")
    print(f"   Translated: {len(done)}")

    if pending:
        print(f"\n⏳ Pending words:")
        for e in pending[:20]:
            ctx = e.get("context", [])
            ctx_str = f" (e.g. '{ctx[0][:50]}...')" if ctx else ""
            print(f"   • {e['word']}{ctx_str}")
        if len(pending) > 20:
            print(f"   ... and {len(pending) - 20} more")
