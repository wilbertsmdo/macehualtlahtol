import time
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

DOC_ID = "1VVrd_fxaE_O5N_6p8OSiqTaOcYfApDSmn8zDcKQREiY"
SA_KEY = "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json"
SCOPES = ["https://www.googleapis.com/auth/documents"]

creds = Credentials.from_service_account_file(SA_KEY, scopes=SCOPES)
docs = build("docs", "v1", credentials=creds)

doc = docs.documents().get(documentId=DOC_ID).execute()

def extract_lines(doc):
    lines = []
    for elem in doc.get("body", {}).get("content", []):
        para = elem.get("paragraph")
        if para is None:
            continue
        text = "".join(
            r.get("textRun", {}).get("content", "")
            for r in para.get("elements", [])
        )
        lines.append(text.rstrip("\n"))
    return lines

lines = extract_lines(doc)

# ── Sort within categories ──────────────────────────────────────────────────
# Split into segments: pre-content, then alternating [header, word_block]
segments = []  # list of dicts: {type: 'pre'|'header'|'words', lines: [...]}

pre = []
i = 0
# Collect any lines before the first category header
while i < len(lines) and not lines[i].strip().startswith("#"):
    pre.append(lines[i])
    i += 1
if pre:
    segments.append({"type": "pre", "lines": pre})

# Now collect category + words pairs
while i < len(lines):
    if lines[i].strip().startswith("#"):
        header = lines[i]
        i += 1
        words = []
        while i < len(lines) and not lines[i].strip().startswith("#"):
            words.append(lines[i])
            i += 1
        # Separate trailing empty lines from word entries
        trailing = []
        while words and words[-1].strip() == "":
            trailing.insert(0, words.pop())
        # Sort non-empty words case-insensitively; keep empty lines at end
        non_empty = [w for w in words if w.strip()]
        empty_mid  = [w for w in words if not w.strip()]
        non_empty.sort(key=lambda x: x.lstrip().lower())
        segments.append({"type": "header", "line": header})
        segments.append({"type": "words", "lines": non_empty + empty_mid + trailing})
    else:
        i += 1

# ── Rebuild sorted lines list ───────────────────────────────────────────────
new_lines = []
for seg in segments:
    if seg["type"] == "pre":
        new_lines.extend(seg["lines"])
    elif seg["type"] == "header":
        new_lines.append(seg["line"])
    elif seg["type"] == "words":
        new_lines.extend(seg["lines"])

# Verify category order is unchanged
orig_cats = [l for l in lines      if l.strip().startswith("#")]
new_cats  = [l for l in new_lines  if l.strip().startswith("#")]
assert orig_cats == new_cats, "Category order changed — aborting"
print(f"Categories preserved: {orig_cats}")
print(f"Original line count: {len(lines)}  →  New line count: {len(new_lines)}")

# ── Compute document end index ──────────────────────────────────────────────
body = doc.get("body", {})
doc_end = body.get("content", [])[-1].get("endIndex", 1)
# Google Docs always keeps a final segment-end marker at doc_end;
# we can safely delete from index 1 to doc_end - 1.
delete_end = doc_end - 1

new_text = "\n".join(new_lines)
# Don't add a trailing newline — Google Docs appends its own end-of-body.

print(f"Document end index: {doc_end}  (will delete 1..{delete_end})")
print(f"New text length (chars): {len(new_text)}")
print("--- Preview first 5 words in #Verb after sort ---")
verb_start = next(i for i, l in enumerate(new_lines) if l.strip() == "#Verb")
for l in new_lines[verb_start:verb_start+6]:
    print(" ", repr(l))

# ── Apply to document ───────────────────────────────────────────────────────
requests = []

if delete_end > 1:
    requests.append({
        "deleteContentRange": {
            "range": {"startIndex": 1, "endIndex": delete_end}
        }
    })

requests.append({
    "insertText": {
        "location": {"index": 1},
        "text": new_text
    }
})

print("\nSending batchUpdate …")
docs.documents().batchUpdate(
    documentId=DOC_ID,
    body={"requests": requests}
).execute()
print("Done! Document updated successfully.")
