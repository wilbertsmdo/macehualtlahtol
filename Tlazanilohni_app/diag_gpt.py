BASE = "/home/wslinux/nllb-env/lib/python3.12/site-packages"
path = BASE + "/TTS/tts/layers/xtts/gpt_inference.py"
with open(path) as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print("=== method definitions ===")
for i, line in enumerate(lines):
    if line.strip().startswith("def ") or line.strip().startswith("class "):
        print(f"{i+1}: {line}", end='')
