"""
audiobook_builder.py — converts a parsed Nahuatl Google Sheet into MP3 audiobook chapters.

Run from the project directory so normalizer.py is importable:
  cd $TPROJ && py3 audiobook_builder.py --sheet SHEET_ID --tab TAB_NAME --book "Book Title"

Examples:
  py3 audiobook_builder.py \
      --sheet 1IcIhyhDsRCzcKBJqL0Z2ObUWz1T1Cwyto11zMko49Gg \
      --tab Crispin \
      --book "Nahuatl Tequitl Crispin"

  py3 audiobook_builder.py \
      --sheet 1zNNZW51_9n0W4NLYa1p47jVdJjDDhsyhKxRQXtuRXFw \
      --tab Eduardo \
      --book "Cenyahtoc Cintli Tonacayo"
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import time
import wave

import gspread
import requests
from google.oauth2.service_account import Credentials

from normalizer import normalize

# ── config ────────────────────────────────────────────────────────────────────

SERVER      = "http://100.68.100.23:8000"
SA_KEY      = "/storage/self/primary/PY_Projects/Financial_Analysis_App/python/service_account.json"
OUTPUT_BASE = "/storage/emulated/0/Music/Tlazanilohni"
FFMPEG      = "/data/data/com.termux/files/usr/bin/ffmpeg"
MAX_CHARS   = 220   # XTTS-v2 hallucination threshold
MAX_RETRIES = 3

# ── helpers ───────────────────────────────────────────────────────────────────

def is_section_title(text: str) -> bool:
    t = text.strip()
    if not t or len(t) > 50:
        return False
    for ch in ".?!,;:-":
        if ch in t:
            return False
    return True

def safe_name(text: str, max_len: int = 40) -> str:
    return re.sub(r"[^\w]", "_", text[:max_len]).strip("_")

def split_sentences(text: str) -> list:
    parts = re.split(r"(?<=[.?!])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]

def post_tts(normalized: str) -> bytes | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                f"{SERVER}/synthesize",
                json={"text": normalized, "language": "es"},
                timeout=90,
            )
            resp.raise_for_status()
            return resp.content
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"    retry {attempt + 1}: {e}")
                time.sleep(5)
            else:
                print(f"    FAILED: {e}")
                return None

def synthesize_sentence(sentence: str) -> bytes | None:
    norm = normalize(sentence)
    if not norm.strip():
        return None
    # split further at commas if over limit
    parts = [p.strip() for p in re.split(r",\s*", norm) if p.strip()] \
            if len(norm) > MAX_CHARS else [norm]
    chunks = []
    for part in parts:
        wav = post_tts(part)
        if wav:
            chunks.append(wav)
    if not chunks:
        return None
    if len(chunks) == 1:
        return chunks[0]
    # join multiple chunks via wave module
    buf = io.BytesIO()
    with wave.open(buf, "wb") as out:
        for i, wav_bytes in enumerate(chunks):
            with wave.open(io.BytesIO(wav_bytes)) as inp:
                if i == 0:
                    out.setparams(inp.getparams())
                out.writeframes(inp.readframes(inp.getnframes()))
    return buf.getvalue()

def flush_chapter(wav_paths: list, chapter_num: int, chapter_title: str, book_dir: str) -> str | None:
    if not wav_paths:
        return None
    title_safe = safe_name(chapter_title or "intro")
    mp3_name   = f"chapter_{chapter_num:03d}_{title_safe}.mp3"
    mp3_path   = os.path.join(book_dir, mp3_name)
    filelist   = mp3_path + ".txt"
    print(f"\n  Flushing chapter {chapter_num}: '{chapter_title}' ({len(wav_paths)} sentences)")

    with open(filelist, "w") as f:
        for p in wav_paths:
            f.write(f"file '{p}'\n")

    result = subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", filelist,
         "-codec:a", "libmp3lame", "-q:a", "4", "-loglevel", "error", mp3_path],
        capture_output=True,
    )
    os.unlink(filelist)

    if result.returncode != 0:
        # fallback to WAV if MP3 encoding fails
        wav_fallback = mp3_path.replace(".mp3", ".wav")
        subprocess.run(
            [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", filelist + "_",
             "-loglevel", "error", wav_fallback],
            capture_output=True,
        )
        # just leave the WAVs if both fail
        print(f"    ffmpeg MP3 error: {result.stderr.decode()[-200:]}")
        print(f"    leaving WAVs in _tmp/ for manual handling")
        return None

    print(f"    -> {mp3_name}")
    for p in wav_paths:
        try:
            os.unlink(p)
        except OSError:
            pass
    return mp3_path

def write_playlist(book_dir: str):
    mp3s = sorted(f for f in os.listdir(book_dir) if f.endswith(".mp3"))
    playlist = os.path.join(book_dir, "playlist.m3u")
    with open(playlist, "w") as f:
        f.write("#EXTM3U\n")
        for mp3 in mp3s:
            f.write(os.path.join(book_dir, mp3) + "\n")
    print(f"\nPlaylist: {playlist} ({len(mp3s)} chapters)")

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheet", required=True, help="Google Sheet ID")
    parser.add_argument("--tab",   required=True, help="Worksheet tab name")
    parser.add_argument("--book",  required=True, help="Book title (used for folder name)")
    args = parser.parse_args()

    book_dir      = os.path.join(OUTPUT_BASE, safe_name(args.book))
    tmp_dir       = os.path.join(book_dir, "_tmp")
    progress_file = os.path.join(book_dir, "progress.json")
    errors_file   = os.path.join(book_dir, "errors.txt")
    os.makedirs(tmp_dir, exist_ok=True)

    # ── load resume state ────────────────────────────────────────────────────
    start_row     = 0
    chapter_num   = 0
    chapter_title = ""
    chapter_wavs  = []

    if os.path.exists(progress_file):
        with open(progress_file) as f:
            p = json.load(f)
        start_row     = p.get("last_row", 0)
        chapter_num   = p.get("chapter_num", 0)
        chapter_title = p.get("chapter_title", "")
        # recover any WAVs already synthesized for the current chapter
        chapter_wavs = sorted(
            os.path.join(tmp_dir, f)
            for f in os.listdir(tmp_dir)
            if f.startswith("r") and f.endswith(".wav")
        )
        print(f"Resuming from row {start_row}, chapter {chapter_num} "
              f"({len(chapter_wavs)} WAVs already in buffer)")

    # ── connect to sheet ─────────────────────────────────────────────────────
    creds = Credentials.from_service_account_file(
        SA_KEY,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    gc = gspread.authorize(creds)
    ws = gc.open_by_key(args.sheet).worksheet(args.tab)
    rows     = ws.get_all_values()
    data     = rows[3:]   # skip 3-row header block
    total    = len(data)
    print(f"\nBook:  {args.book}")
    print(f"Sheet: {args.tab}  —  {total} data rows  (starting at {start_row})")
    print(f"Output: {book_dir}\n")

    # ── synthesis loop ───────────────────────────────────────────────────────
    for row_idx, row in enumerate(data):
        if row_idx < start_row:
            continue

        cell = row[1].strip() if len(row) > 1 else ""
        if not cell:
            continue

        pct = row_idx / total * 100
        print(f"[{pct:5.1f}%] row {row_idx + 1}/{total}: ", end="", flush=True)

        if is_section_title(cell):
            print(f"CHAPTER BREAK — '{cell}'")
            mp3 = flush_chapter(chapter_wavs, chapter_num, chapter_title, book_dir)
            chapter_wavs  = []
            chapter_num  += 1
            chapter_title = cell
            continue

        print(f"{cell[:70]}{'...' if len(cell) > 70 else ''}")
        wav_bytes = synthesize_sentence(cell)

        if wav_bytes:
            tmp_path = os.path.join(tmp_dir, f"r{row_idx:05d}.wav")
            with open(tmp_path, "wb") as f:
                f.write(wav_bytes)
            chapter_wavs.append(tmp_path)
        else:
            with open(errors_file, "a") as f:
                f.write(f"row {row_idx + 1}: {cell}\n")
            print(f"    [skipped — logged to errors.txt]")

        # persist progress after every sentence
        with open(progress_file, "w") as f:
            json.dump({
                "last_row":      row_idx + 1,
                "chapter_num":   chapter_num,
                "chapter_title": chapter_title,
            }, f)

    # ── flush final chapter ──────────────────────────────────────────────────
    flush_chapter(chapter_wavs, chapter_num, chapter_title, book_dir)

    # ── playlist ─────────────────────────────────────────────────────────────
    write_playlist(book_dir)

    # cleanup empty tmp dir
    try:
        os.rmdir(tmp_dir)
    except OSError:
        pass

    print(f"\nDone. Open: Files app -> Internal Storage -> Music -> Tlazanilohni -> {safe_name(args.book)}")

if __name__ == "__main__":
    main()
