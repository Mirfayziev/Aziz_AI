from app.services.chat_service import chat_with_ai
from app.services.tts_service import text_to_speech_bytes
from app.services.summary_service import summary_service

async def brain_query(text: str):
    answer = await chat_with_ai(text)
    audio_bytes = await text_to_speech_bytes(answer)
    return answer, audio_bytes

async def get_daily_summary() -> str:
    """
    Aziz AI — kunlik summary
    """
    return await summary_service.generate_daily_summary()
