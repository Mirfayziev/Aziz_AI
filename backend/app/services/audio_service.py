import tempfile
from typing import Tuple

from fastapi import UploadFile
from sqlalchemy.orm import Session

from ..config import get_openai_client, get_settings
from .chat_service import create_chat_reply
from .memory_service import get_or_create_user

settings = get_settings()
client = get_openai_client()


async def process_audio_message(
    db: Session,
    external_user_id: str,
    file: UploadFile,
) -> Tuple[str, str]:
    """
    Audio faylni matnga aylantiradi, so‘ng chat_service orqali javob oladi.
    return: (reply_text, transcribed_text)
    """
    user = get_or_create_user(db, external_user_id)

    suffix = ".ogg"
    with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()

        with open(tmp.name, "rb") as audio_f:
            transcript = client.audio.transcriptions.create(
                model=settings.TRANSCRIBE_MODEL,
                file=audio_f,
            )

    text = transcript.text.strip() if hasattr(transcript, "text") else str(transcript)

    reply, _ = create_chat_reply(
        db,
        external_user_id=user.external_id,
        message=text,
        model_tier="default",
    )

    return reply, text
