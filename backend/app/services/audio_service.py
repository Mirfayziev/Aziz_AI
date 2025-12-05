import base64
import openai
from .chat_service import create_chat_reply

def process_audio_message(db, external_id: str, audio_base64: str, model_tier: str):
    # Base64 → binary
    audio_bytes = base64.b64decode(audio_base64)

    # Speech-to-text
    text = openai.Audio.transcriptions.create(
        model="gpt-4o-mini-tts",
        file=("audio.ogg", audio_bytes)
    ).text

    # AI javobi
    reply = create_chat_reply(
        db=db,
        external_id=external_id,
        message=text,
        model_tier=model_tier
    )

    return text, reply
