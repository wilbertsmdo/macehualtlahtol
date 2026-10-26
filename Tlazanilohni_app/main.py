import argparse
import io
import os
import re
import subprocess
import wave

import requests

from normalizer import normalize

SERVER = "http://100.68.100.23:8000"
OUTPUT_DIR = "/storage/emulated/0/Music/Tlazanilohni"
MAX_CHARS = 220  # XTTS-v2 hallucinates beyond ~250 normalized chars


def split_sentences(text: str) -> list:
    parts = re.split(r"(?<=[.?!¿¡])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def post_tts(normalized: str, voices: list) -> bytes:
    resp = requests.post(
        f"{SERVER}/synthesize",
        json={"text": normalized, "language": "es", "voices": voices},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.content


def concat_wavs(wav_bytes_list: list) -> bytes:
    out_buf = io.BytesIO()
    with wave.open(out_buf, "wb") as out_wav:
        for i, wav_bytes in enumerate(wav_bytes_list):
            with wave.open(io.BytesIO(wav_bytes)) as in_wav:
                if i == 0:
                    out_wav.setparams(in_wav.getparams())
                out_wav.writeframes(in_wav.readframes(in_wav.getnframes()))
    return out_buf.getvalue()


def synthesize(text: str, voices: list) -> bytes:
    sentences = split_sentences(text)
    chunks = []
    for i, sentence in enumerate(sentences):
        norm = normalize(sentence)
        if not norm.strip():
            continue
        if len(norm) > MAX_CHARS:
            sub_parts = re.split(r",\s*", norm)
            sub_parts = [p.strip() for p in sub_parts if p.strip()]
        else:
            sub_parts = [norm]

        for part in sub_parts:
            print(f"  [{i+1}/{len(sentences)}] {part}")
            chunks.append(post_tts(part, voices))

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
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="*", help="Nahuatl text to synthesize")
    parser.add_argument(
        "--voice", default="default",
        help="Voice name(s), comma-separated: default | voice2 | default,voice2"
    )
    args = parser.parse_args()

    voices = [v.strip() for v in args.voice.split(",") if v.strip()]
    text = " ".join(args.text) if args.text else input("Enter Nahuatl text: ").strip()

    print(f"Input:  {text[:80]}{'...' if len(text) > 80 else ''}")
    print(f"Voices: {voices}")
    audio = synthesize(text, voices)
    path = save(audio, text)
    play(path)
