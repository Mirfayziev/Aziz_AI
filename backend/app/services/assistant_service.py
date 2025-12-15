from app.services.chat_service import chat_with_ai

async def brain_query(text: str, user_id: str = "telegram", source: str = "telegram"):
    """
    Aziz AI miyasi (bitta joyda)
    """
    response = await chat_with_ai(text)
    return response
