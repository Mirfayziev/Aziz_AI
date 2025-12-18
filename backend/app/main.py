from fastapi import FastAPI, Request, UploadFile, File
import os
import tempfile

from app.services.assistant_service import (
    brain_query,
    get_daily_summary,
    get_weekly_summary,
)
from app.services.stt_service import speech_to_text, STTServiceError

app = FastAPI(title="Aziz AI", version="1.0.0")


# ======================================================
# SUMMARY ENDPOINTS
# ======================================================

@app.get("/summary")
async def daily_summary():
    """
    Aziz AI — kunlik summary
    """
    return {
        "summary": await get_daily_summary()
    }


@app.get("/summary/weekly")
async def weekly_summary():
    """
    Aziz AI — haftalik summary
    """
    return {
        "summary": await get_weekly_summary()
    }


# ======================================================
# TEXT CHAT (TELEGRAM / WEB)
# ======================================================

@app.post("/assistant-message")
async def assistant_message(request: Request):
    """
    Text -> Aziz AI -> Text (+ audio placeholder)
    """
    data = await request.json()
    text = (data.get("text") or "").strip()

    if not text:
        return {"error": "Text is empty"}

    answer, audio_bytes = await brain_query(text)

    return {
        "text": answer,
        # audio hozircha hex ko‘rinishda (TTS keyin to‘liq ishlatiladi)
        "audio": audio_bytes.hex() if audio_bytes else None
    }


# ======================================================
# STT — SPEECH TO TEXT
# ======================================================

@app.post("/stt")
async def stt_endpoint(file: UploadFile = File(...)):
    """
    Audio (ogg/mp3/wav) -> text
    Telegram voice bilan mos
    """
    suffix = os.path.splitext(file.filename or "")[1] or ".ogg"
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            tmp.write(await file.read())

        text = speech_to_text(tmp_path)
        return {"text": text}

    except STTServiceError as e:
        return {"error": str(e)}

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


# ======================================================
# VOICE CHAT (STT -> AI -> TTS)
# (hozircha ishlaydi, lekin ovoz strategik yoqilgan emas)
# ======================================================

@app.post("/voice-chat")
async def voice_chat(file: UploadFile = File(...)):
    """
    Audio -> text (STT) -> Aziz AI -> text (+ audio)
    """
    suffix = os.path.splitext(file.filename or "")[1] or ".ogg"
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            tmp.write(await file.read())

        text = speech_to_text(tmp_path)
        answer, audio_bytes = await brain_query(text)

        return {
            "input_text": text,
            "text": answer,
            "audio": audio_bytes.hex() if audio_bytes else None
        }

    except STTServiceError as e:
        return {"error": str(e)}

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
