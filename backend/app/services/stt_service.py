# backend/services/stt_service.py

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def speech_to_text(audio_path: str, language: str | None = None) -> str:
    """
    audio_path: .ogg / .mp3 / .wav
    returns: recognized text
    """

    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="gpt-4o-transcribe",  # yoki "whisper-1"
            language=language  # None bo‘lsa avtomatik
        )

    return transcript.text.strip()
