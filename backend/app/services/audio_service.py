import base64
import io
from sqlalchemy.orm import Session
from openai import OpenAI

from app.services.chat_service import create_chat_reply

client = OpenAI()


def process_audio(db: Session, user_id: int, audio_base64: str):
    """
    1) Telegramdan kelgan audio_base64 ni dekod qiladi
    2) OpenAI Whisper orqali matnga aylantiradi
    3) Chat AI (memory bilan) orqali javob oladi
    4) {"text": ..., "reply": ...} qaytaradi
    """

    # 1) Base64 → Bytes
    audio_bytes = base64.b64decode(audio_base64)

    # file-like obyekt (OpenAI uchun)
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.ogg"  # format nomi

    # 2) Speech-to-Text (Whisper)
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    text = transcription.text

    # 3) AI javobi (chat_service dan foydalanamiz)
    reply = create_chat_reply(user_id=user_id, message=text, db=db)

    return {
        "text": text,
        "reply": reply
    }
