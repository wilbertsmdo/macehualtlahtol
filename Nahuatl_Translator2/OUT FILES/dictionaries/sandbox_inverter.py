#!/usr/bin/env python3
import json

# Data extracted from your enriched_idiez.json
target_words = {
  "zoquitl": {
    "cat": "tlat", # Noun
    "definitions": [{"en": "mud.", "analysis": {"roots": ["mud"], "lemmas": ["mud"]}}]
  },
  "zozoquitic": {
    "cat": "quen", # Adjective
    "definitions": [{"en": "person, animal or thing covered with mud.", "analysis": {"roots": ["person"], "lemmas": ["cover", "mud"]}}]
  },
  "ahalaxhuiliā": {
    "cat": "tlach3", # Verb
    "definitions": [
      {"en": "to caress an animal.", "analysis": {"roots": ["caress"], "lemmas": ["animal"]}},
      {"en": "to apply mud to a wall.", "analysis": {"roots": ["apply"], "lemmas": ["mud", "wall"]}}
    ]
  }
}

def sandbox_invert(data):
    inverted = {}
    
    for nah, info in data.items():
        cat = info["cat"]
        for d in info["definitions"]:
            en_def = d["en"]
            roots = d["analysis"]["roots"]
            lemmas = d["analysis"]["lemmas"]
            
            # Combine all possible keys for this definition
            possible_keys = set(roots + lemmas)
            # Add the full phrase if it's short
            if len(en_def.split()) <= 5:
                possible_keys.add(en_def.lower().rstrip('.'))

            for key in possible_keys:
                if key not in inverted: inverted[key] = []
                
                # Calculate a "Match Score"
                score = 0
                if key in roots: score += 10 # Root is high priority
                if key in en_def.lower(): score += 5 # Literal match
                
                # Grammatical Bonus
                if cat == "tlat" and key == "mud": score += 20 # Noun matches Noun
                if cat == "tlach3" and key == "apply": score += 20 # Verb matches Verb
                
                inverted[key].append({
                    "nah": nah,
                    "cat": cat,
                    "score": score,
                    "def": en_def
                })
    
    # Sort results by score
    for key in inverted:
        inverted[key] = sorted(inverted[key], key=lambda x: x['score'], reverse=True)
        
    return inverted

# Run Sandbox
result = sandbox_invert(target_words)

# Display specific interesting keys
print("--- SANDBOX OUTPUT ---")
for word in ["mud", "apply", "cover", "person", "apply mud"]:
    if word in result:
        print(f"\nKey: '{word}'")
        for match in result[word]:
            print(f"  -> [{match['score']}] {match['nah']} ({match['cat']}) - '{match['def']}'")
