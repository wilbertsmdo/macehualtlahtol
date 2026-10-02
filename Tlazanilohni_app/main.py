import sys
import os
import io
import wave
import re
import subprocess
import requests
from normalizer import normalize

SERVER = "http://100.68.100.23:8000"
OUTPUT_DIR = "/storage/emulated/0/Music/Tlazanilohni"
MAX_CHARS = 220  # XTTS-v2 hallucinates beyond ~250 normalized chars

def split_sentences(text: str) -> list:
    """Split on sentence-ending punctuation, keeping the punctuation with the sentence."""
    parts = re.split(r"(?<=[.?!¿¡])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]

def post_tts(normalized: str) -> bytes:
    resp = requests.post(
        f"{SERVER}/synthesize",
        json={"text": normalized, "language": "es"},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.content

def concat_wavs(wav_bytes_list: list) -> bytes:
    """Concatenate WAV byte strings into one WAV using the wave module."""
    out_buf = io.BytesIO()
    with wave.open(out_buf, "wb") as out_wav:
        for i, wav_bytes in enumerate(wav_bytes_list):
            with wave.open(io.BytesIO(wav_bytes)) as in_wav:
                if i == 0:
                    out_wav.setparams(in_wav.getparams())
                out_wav.writeframes(in_wav.readframes(in_wav.getnframes()))
    return out_buf.getvalue()

def synthesize(text: str) -> bytes:
    sentences = split_sentences(text)
    chunks = []
    for i, sentence in enumerate(sentences):
        norm = normalize(sentence)
        if not norm.strip():
            continue
        # further split if a single sentence is still too long
        if len(norm) > MAX_CHARS:
            # split on comma as secondary boundary
            sub_parts = re.split(r",\s*", norm)
            sub_parts = [p.strip() for p in sub_parts if p.strip()]
        else:
            sub_parts = [norm]

        for part in sub_parts:
            print(f"  [{i+1}/{len(sentences)}] {part}")
            chunks.append(post_tts(part))

    if len(chunks) == 1:
        return chunks[0]
    return concat_wavs(chunks)

def save(audio_bytes: bytes, text: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe = "".join(c if c.isalnum() else "_" for c in text[:30])
    path = os.path.join(OUTPUT_DIR, f"{safe}.wav")
    with open(path, "wb") as f:
        f.write(audio_bytes)
    print(f"Saved: {path}")
    return path

def play(path: str):
    if subprocess.run(["which", "termux-open"], capture_output=True).returncode == 0:
        subprocess.run(["termux-open", path])
    elif subprocess.run(["which", "termux-media-player"], capture_output=True).returncode == 0:
        subprocess.run(["termux-media-player", "play", path])
    else:
        print(f"Open manually: {path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = input("Enter Nahuatl text: ").strip()

    print(f"Input: {text[:80]}{'...' if len(text) > 80 else ''}")
    audio = synthesize(text)
    path = save(audio, text)
    play(path)
