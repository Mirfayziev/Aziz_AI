from sqlalchemy.orm import Session
from app.models.chat import ChatMessage
from app.core.ai_client import client

def create_chat_reply(db: Session, external_id: str, message: str):

    history = db.query(ChatMessage).filter(
        ChatMessage.external_id == external_id
    ).order_by(ChatMessage.timestamp).all()

    messages = [{"role": "system", "content": "You are Aziz AI."}]

    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": message})

    response = client.responses.create(
        model="gpt-5.1",
        messages=messages
    )

    reply_text = response.output_text

    db_message_user = ChatMessage(
        external_id=external_id,
        role="user",
        content=message
    )
    db_message_bot = ChatMessage(
        external_id=external_id,
        role="assistant",
        content=reply_text
    )

    db.add(db_message_user)
    db.add(db_message_bot)
    db.commit()

    return reply_text
