from app.services.memory_service import get_memory_context, save_memory
from app.services.models import ChatMessage
from db import SessionLocal

def create_chat_reply(user_id: int, message: str):
    db = SessionLocal()

    # Xotira konteksti olish
    memory = get_memory_context(user_id=user_id, db=db)

    # OpenAI chaqirish
    reply = call_openai_with_memory(message, memory)

    # Xotirani saqlash
    save_memory(user_id=user_id, message=message, reply=reply, db=db)

    db.close()
    return reply
