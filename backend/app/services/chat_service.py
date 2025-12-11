# app/services/chat_service.py

from openai import OpenAI
from app.db import get_user_context, save_user_context, save_ai_message

from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


# AI javob yaratish
async def create_chat_reply(user_id: str, user_message: str) -> str:
    # Eski kontekstni olish
    previous_context = get_user_context(user_id)

    # Modelga yuboriladigan to'plam
    messages = []
    if previous_context:
        messages.append({"role": "system", "content": previous_context})

    messages.append({"role": "user", "content": user_message})

    # ChatGPT dan javob olish
    ai_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply_text = ai_response.choices[0].message["content"]

    # KONTEXT YANGILANADI (eslab qolish xotira)
    new_context = previous_context + f"\nUser: {user_message}\nAI: {reply_text}"
    save_user_context(user_id, new_context)

    # Chat history ga yozish
    save_ai_message(user_id, "assistant", reply_text)

    return reply_text
