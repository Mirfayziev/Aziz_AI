from openai import OpenAI
from fastapi import HTTPException
import os
from app.db import get_user_context, save_user_message, save_ai_message

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def create_chat_reply(db, external_id: str, message: str):
    try:
        # 1) User kontekstini olish
        history = get_user_context(db, external_id)

        messages = [{"role": "system", "content": "You are Aziz AI assistant."}]

        # oldingi tarixni qo‘shish
        for h in history:
            messages.append({"role": h.role, "content": h.content})

        # userning yangi xabarini qo‘shish
        messages.append({"role": "user", "content": message})

        # 2) OpenAI so‘rovi
        response = client.chat.completions.create(
            model="gpt-5.1-mini",
            messages=messages,
            temperature=0.8,
        )

        # 3) YANGI FORMATDA JAVOBNI OLISh
        reply_text = response.choices[0].message.content

        # 4) Xotiraga yozish
        save_user_message(db, external_id, message)
        save_ai_message(db, external_id, reply_text)

        return reply_text

    except Exception as e:
        print("AI xato:", e)
        raise HTTPException(500, detail="AI bilan ulanishda xatolik")
