import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class STTServiceError(Exception):
    pass


def speech_to_text(audio_path: str) -> str:
    """
    Telegram voice (.ogg) → text
    """

    if not os.path.exists(audio_path):
        raise STTServiceError("Audio file not found")

    try:
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1"
            )

        text = transcription.text.strip()

        if not text:
            raise STTServiceError("Empty transcription")

        return text

    except Exception as e:
        raise STTServiceError(str(e))
