import base64
from openai import OpenAI
from .chat_service import create_chat_reply

client = OpenAI()


def process_audio_message(db, external_id: str, audio_base64: str, model_tier: str):
    # 1) Base64 → Bytes
    audio_bytes = base64.b64decode(audio_base64)

    # 2) Speech-to-Text (Whisper)
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.ogg", audio_bytes)
    )

    text = transcription.text

    # 3) AI javobi yaratish (chat model)
    reply = create_chat_reply(
        db=db,
        external_id=external_id,
        message=text,
        model_tier=model_tier
    )

    return text, reply


# ALIAS (router bilan moslik uchun)
def process_audio(db, external_id: str, audio_base64: str, model_tier: str):
    return process_audio_message(db, external_id, audio_base64, model_tier)
