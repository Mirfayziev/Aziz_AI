from fastapi import FastAPI, Request, UploadFile, File
import os
import tempfile

from app.services.assistant_service import brain_query
from app.services.stt_service import speech_to_text, STTServiceError
from app.services.assistant_service import get_daily_summary
from app.services.assistant_service import get_weekly_summary

app = FastAPI()

@app.get("/summary/weekly")
async def weekly_summary():
    return {
        "summary": await get_weekly_summary()
    }
    
@app.get("/summary")
async def daily_summary():
    return {
        "summary": await get_daily_summary()
    }
    
@app.post("/assistant-message")
async def assistant_message(request: Request):
    data = await request.json()
    text = (data.get("text") or "").strip()

    answer, audio_bytes = await brain_query(text)

    return {
        "text": answer,
        "audio": audio_bytes.hex()
    }

@app.post("/stt")
async def stt_endpoint(file: UploadFile = File(...)):
    # Accepts Telegram voice (.ogg) or any supported audio file.
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

@app.post("/voice-chat")
async def voice_chat(file: UploadFile = File(...)):
    # audio -> text (STT) -> answer+audio (TTS)
    suffix = os.path.splitext(file.filename or "")[1] or ".ogg"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            tmp.write(await file.read())
        text = speech_to_text(tmp_path)
        answer, audio_bytes = await brain_query(text)
        return {"input_text": text, "text": answer, "audio": audio_bytes.hex()}
    except STTServiceError as e:
        return {"error": str(e)}
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
