import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def text_to_speech_bytes(text: str) -> bytes:
    # Telegram sendVoice expects OGG/OPUS. We request OPUS to avoid format issues.
    response = await client.audio.speech.create(
        model=os.getenv("TTS_MODEL", "gpt-4o-mini-tts"),
        voice=os.getenv("TTS_VOICE", "alloy"),
        input=text,
        response_format="opus"
    )
    return response.read()
