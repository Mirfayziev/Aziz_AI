from services.chat_service import chat_with_ai
from services.tts_service import text_to_speech_bytes

async def brain_query(text: str):
    answer = await chat_with_ai(text)
    audio_bytes = await text_to_speech_bytes(answer)
    return answer, audio_bytes
