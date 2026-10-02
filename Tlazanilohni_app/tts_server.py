from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from TTS.api import TTS
import tempfile, os

app = FastAPI()

REFERENCE_VOICE = os.path.expanduser("~/Tlazanilohni_server/reference_voice.wav")

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)


class SynthRequest(BaseModel):
    text: str
    language: str = "es"


@app.post("/synthesize")
def synthesize(req: SynthRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is empty")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        tts.tts_to_file(
            text=req.text,
            speaker_wav=REFERENCE_VOICE,
            language=req.language,
            file_path=tmp_path,
        )
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
    finally:
        os.unlink(tmp_path)
    return Response(content=audio_bytes, media_type="audio/wav")


@app.get("/health")
def health():
    return {"status": "ok"}
