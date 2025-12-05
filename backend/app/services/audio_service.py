
import io
from sqlalchemy.orm import Session
from openai import OpenAI

from app.services.chat_service import create_chat_reply
from app.services.memory_service import get_or_create_user

client = OpenAI()


def process_audio(db: Session, external_user_id: str, audio_bytes: bytes, full_name: str | None = None):
    user = get_or_create_user(db, external_id=external_user_id, full_name=full_name)

    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.ogg"

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
    )

    text = transcript.text

    reply = create_chat_reply(db, external_user_id, text, full_name=full_name)

    return {"text": text, "reply": reply}
