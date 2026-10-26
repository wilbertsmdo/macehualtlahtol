from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from TTS.api import TTS
import os
import tempfile
from typing import List

app = FastAPI()

SERVER_DIR = os.path.expanduser("~/Tlazanilohni_server")

VOICES: dict[str, str] = {
    "default": os.path.join(SERVER_DIR, "reference_voice.wav"),
    "voice2":  os.path.join(SERVER_DIR, "reference_voice2.wav"),
    "voice3":  os.path.join(SERVER_DIR, "reference_voice3.wav"),
}

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)


class SynthRequest(BaseModel):
    text: str
    language: str = "es"
    voices: List[str] = ["default"]


@app.post("/synthesize")
def synthesize(req: SynthRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is empty")

    speaker_wavs = [VOICES[v] for v in req.voices if v in VOICES]
    if not speaker_wavs:
        speaker_wavs = [VOICES["default"]]
    # XTTS-v2 accepts a list and blends the voice embeddings
    speaker_wav = speaker_wavs if len(speaker_wavs) > 1 else speaker_wavs[0]

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        tts.tts_to_file(
            text=req.text,
            speaker_wav=speaker_wav,
            language=req.language,
            file_path=tmp_path,
        )
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
    finally:
        os.unlink(tmp_path)
    return Response(content=audio_bytes, media_type="audio/wav")


@app.get("/voices")
def list_voices():
    return {
        name: {"path": path, "exists": os.path.exists(path)}
        for name, path in VOICES.items()
    }


@app.get("/health")
def health():
    return {"status": "ok"}
