"""
tokenizer_compare.py — Tiyat (tachiwin/tokenizer_64k) vs NLLB-200 tokenizer
on Huasteca Nahuatl text from our training corpus.

Run: /usr/bin/python3 tokenizer_compare.py
"""
from transformers import AutoTokenizer
import json, statistics

TRAINING_DATA = "/storage/self/primary/PY_Projects/Macehualtlahtol/Nahuatl_Translator2/training_data/nah_es_pairs.json"

# Morphologically rich words with known IDIEZ decompositions
TEST_WORDS = [
    ("nitlatequitiz",        "ni-tla-tequiti-z"),
    ("niquintalazcamatilia",  "ni-quin-tlazcamati-lia"),
    ("timochihuazqueh",      "ti-mo-chihua-z-queh"),
    ("niquimittaz",          "ni-qui-mitta-z"),
    ("tlatequipanoa",        "tla-tequipano-a"),
    ("mochihuaz",            "mo-chihua-z"),
    ("quinamiqui",           "qui-namiqui"),
    ("nicnequi",             "nic-nequi"),
    ("tlahtoa",              "tlahtoa"),
    ("tihuallahqueh",        "ti-hual-lahqueh"),
    ("nimitztlazohtla",      "ni-mitz-tlazohtla"),
    ("xinechtlapohpolhui",   "xi-nech-tlapohpolhui"),
    ("tictlazohcamati",      "tic-tlazohtla-mati"),
    ("cualtzin",             "cual-tzin"),
    ("moxtin",               "mox-tin"),
]

# ── Load tokenizers ──────────────────────────────────────────────────────────
print("Loading Tiyat tokenizer (tachiwin/tokenizer_64k)...")
tok_tiyat = AutoTokenizer.from_pretrained("tachiwin/tokenizer_64k", trust_remote_code=True)
print(f"  Vocab size: {tok_tiyat.vocab_size:,}")

print("Loading NLLB-200 tokenizer...")
tok_nllb = AutoTokenizer.from_pretrained(
    "facebook/nllb-200-distilled-600M", src_lang="nah_Latn"
)
print(f"  Vocab size: {tok_nllb.vocab_size:,}")

# ── Load test corpus ─────────────────────────────────────────────────────────
with open(TRAINING_DATA) as f:
    pairs = json.load(f)

sentences = [p["nahuatl"] for p in pairs if p.get("nahuatl") and len(p["nahuatl"].split()) >= 3][:300]
print(f"\nTest corpus: {len(sentences)} Nahuatl sentences from nah_es_pairs.json\n")

# ── Metric functions ─────────────────────────────────────────────────────────
def tokenize_safe(tok, text):
    try:
        return tok.tokenize(text)
    except Exception:
        return []

def fertility(tok, texts):
    total_t, total_w = 0, 0
    for t in texts:
        tokens = tokenize_safe(tok, t)
        words  = t.split()
        total_t += len(tokens)
        total_w += len(words)
    return total_t / total_w if total_w else 0

def per_sentence_fertility(tok, texts):
    vals = []
    for t in texts:
        tokens = tokenize_safe(tok, t)
        words  = t.split()
        if words:
            vals.append(len(tokens) / len(words))
    return vals

def single_token_rate(tok, words):
    singles = sum(1 for w in words if len(tokenize_safe(tok, w)) == 1)
    return singles / len(words) if words else 0

def unk_rate(tok, texts):
    unk_id = getattr(tok, "unk_token_id", None)
    if unk_id is None:
        return None
    total, unk = 0, 0
    for t in texts:
        try:
            ids = tok.encode(t)
        except Exception:
            continue
        total += len(ids)
        unk   += ids.count(unk_id)
    return unk / total if total else 0

def avg_tokens_per_word(tok, words):
    counts = [len(tokenize_safe(tok, w)) for w in words if w]
    return statistics.mean(counts) if counts else 0

# ── Compute metrics ──────────────────────────────────────────────────────────
all_words = [w for s in sentences for w in s.split() if w]

print("Computing metrics (may take a minute)...")

ft  = fertility(tok_tiyat, sentences)
fn  = fertility(tok_nllb,  sentences)

fts = per_sentence_fertility(tok_tiyat, sentences)
fns = per_sentence_fertility(tok_nllb,  sentences)

st = single_token_rate(tok_tiyat, all_words)
sn = single_token_rate(tok_nllb,  all_words)

ut = unk_rate(tok_tiyat, sentences)
un = unk_rate(tok_nllb,  sentences)

# ── Print results ────────────────────────────────────────────────────────────
SEP = "─" * 65

print(f"\n{SEP}")
print("METRIC 1 — FERTILITY (tokens ÷ words)  [lower = better]")
print(SEP)
print(f"  Tiyat:    {ft:.3f}  (median: {statistics.median(fts):.2f})")
print(f"  NLLB-200: {fn:.3f}  (median: {statistics.median(fns):.2f})")
if ft > 0:
    print(f"  Ratio:    NLLB produces {fn/ft:.2f}× more tokens than Tiyat")

print(f"\n{SEP}")
print("METRIC 2 — SINGLE-TOKEN WORD RATE  [higher = better]")
print(SEP)
print(f"  Tiyat:    {st:.1%} of words map to 1 token")
print(f"  NLLB-200: {sn:.1%} of words map to 1 token")

print(f"\n{SEP}")
print("METRIC 3 — UNKNOWN TOKEN RATE  [lower = better, None = no <unk>]")
print(SEP)
print(f"  Tiyat:    {f'{ut:.2%}' if ut is not None else 'N/A (no <unk> token)'}")
print(f"  NLLB-200: {f'{un:.2%}' if un is not None else 'N/A (no <unk> token)'}")

print(f"\n{SEP}")
print("METRIC 4 — MORPHEME BOUNDARY INSPECTION")
print(SEP)
print(f"  {'Word':<28} {'Expected (IDIEZ)':<25} {'Tiyat':<30} NLLB-200")
print(f"  {'─'*28} {'─'*25} {'─'*30} {'─'*30}")
for word, expected in TEST_WORDS:
    t = tokenize_safe(tok_tiyat, word)
    n = tokenize_safe(tok_nllb,  word)
    # Clean up token display (remove sentencepiece ▁ prefix)
    t_str = " | ".join(tok.replace("▁","").replace("Ġ","") for tok in t)
    n_str = " | ".join(tok.replace("▁","").replace("Ġ","") for tok in n)
    print(f"  {word:<28} {expected:<25} {t_str:<30} {n_str}")

print(f"\n{SEP}")
print("METRIC 5 — SENTENCE EXAMPLES (first 5)")
print(SEP)
for sent in sentences[:5]:
    t = tokenize_safe(tok_tiyat, sent)
    n = tokenize_safe(tok_nllb,  sent)
    t_str = " | ".join(tok.replace("▁","").replace("Ġ","") for tok in t)
    n_str = " | ".join(tok.replace("▁","").replace("Ġ","") for tok in n)
    print(f"\n  Source ({len(sent.split())} words): {sent}")
    print(f"  Tiyat  ({len(t):2d} tokens): {t_str}")
    print(f"  NLLB   ({len(n):2d} tokens): {n_str}")

print(f"\n{SEP}")
print("SUMMARY")
print(SEP)
ratio = fn/ft if ft > 0 else 0
if ratio < 1.1:
    verdict = "NLLB tokenizer is roughly equivalent — no action needed"
elif ratio < 1.3:
    verdict = "Tiyat moderately better — consider custom SentencePiece later"
elif ratio < 2.0:
    verdict = "Tiyat significantly better — building a custom tokenizer is worthwhile"
else:
    verdict = "NLLB is dramatically worse — strongly consider Tiyat or custom tokenizer"
print(f"  Fertility ratio (NLLB/Tiyat): {ratio:.2f}×")
print(f"  Verdict: {verdict}")
print(SEP)
