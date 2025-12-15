import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

async def speech_to_text(audio_path: str) -> str:
    with open(audio_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            language="uz"
        )
    return transcript.text
