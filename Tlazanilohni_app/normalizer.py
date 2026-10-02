import re

REPLACEMENTS = [
    # em-dash and en-dash (dialogue markers) -> strip to prevent TTS hallucinations
    ("—|–", " "),
    # hyphen -> space (spoken as "menos" in Spanish TTS otherwise)
    ("-", " "),
    # other punctuation that causes TTS artifacts
    ('["""\\u00ab\\u00bb():;]', ""),

    # cc -> cj  (geminate k: "nocca" -> "nocja", soft aspirated /kx/ not plain /k/)
    ("cc", "cj"),

    # vowel + uh -> vowel + h  (silent u: queniuhqui->quenihqui, nouhquiya->nohquiya)
    (r"([aeiou])uh", r"\1h"),

    # hu + vowel -> w  (must run before x->sh and h->j)
    (r"hu([aeiou])", r"w\1"),
    # x -> sh
    ("x", "sh"),
    # h -> j  (lookbehind: skip h in "sh" and "ch")
    # "sh" = our x substitution; "ch" = Nahuatl /tsh/ (same as Spanish ch)
    # Spanish j = /x/ -- audible aspiration, closest to Nahuatl /h/
    (r"(?<!s)(?<!c)h", "j"),
    # tz -> ts
    ("tz", "ts"),
    # tl: leave as-is (Mexican Spanish TTS approximates the lateral affricate)
    # qu before e/i -> k
    (r"qu([ei])", r"k\1"),
    # cu before vowels -> kw
    (r"cu([aeiou])", r"kw\1"),
    # saltillo variants -> drop
    ("[ʼʻ‘’]", ""),
    # ll -> l
    ("ll", "l"),
]

def normalize(text: str) -> str:
    # collapse all whitespace (including newlines from book text) to single space
    text = re.sub(r"\s+", " ", text).strip()
    text = text.lower()

    for pattern, replacement in REPLACEMENTS:
        text = re.sub(pattern, replacement, text)

    # strip trailing period -- XTTS-v2 produces a small artifact on end-of-input period
    text = re.sub(r"\.\s*$", "", text).strip()

    # add Spanish inverted openers for correct interrogative/exclamatory intonation
    if text.endswith("?") and not text.startswith("¿"):
        text = "¿" + text
    if text.endswith("!") and not text.startswith("¡"):
        text = "¡" + text

    return text

if __name__ == "__main__":
    tests = [
        "Nimitztlazohtla",
        "Xochitl",
        "Tlazohcamati",
        "Tlahtolli",
        "Niquintlazcamatilia notatahuan",
        "Huehca motlahpaloa",
    ]
    print("--- core rules ---")
    for t in tests:
        print(f"{t:42s} -> {normalize(t)}")

    print("\n--- punctuation / iuh / dash / cc ---")
    edge_cases = [
        "Nimitztlazohtla.",
        "Tlen  ticcaqui,  Pedro?",
        "nocca",
        "Huacca nopa rohuenteh",
        "queniuhqui",
        "Nouhquiya quinhuica conemeh",
        "Iuhquinon quiihtoah macehualmeh",
        "—Huacca nopa rohuenteh tlen ticpantih, tateh",
        "—Axnicmati, cuah, ma nimoxixqui.",
    ]
    for t in edge_cases:
        print(f"{t!r:52s} -> {normalize(t)!r}")
