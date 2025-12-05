from openai import OpenAI
from fastapi import HTTPException
import os

client = OpenAI()

# Variables from Railway
MODEL_DEFAULT = os.getenv("MODEL_DEFAULT", "gpt-4.1")      # Asosiy model — ChatGPT darajasi
MODEL_FAST = os.getenv("MODEL_FAST", "gpt-4o-mini")        # Tez model
MODEL_DEEP = os.getenv("MODEL_DEEP", "o1")                 # Chuqur fikrlash modeli


def get_model_by_tier(tier: str):
    """
    tier = 'default', 'fast', 'deep'
    """
    if tier == "fast":
        return MODEL_FAST
    if tier == "deep":
        return MODEL_DEEP
    return MODEL_DEFAULT   # default


def create_chat_reply(message: str, tier: str = "default"):
    """
    Chat javobi qaytaruvchi asosiy funksiya.
    tier → qaysi model ishlatilishini belgilaydi
    """

    model = get_model_by_tier(tier)

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Siz Aziz AI. Siz ChatGPT 5.1 darajasidagi sun'iy intellektsiz. "
                        "Siz 2025–2030 yillarga doir real ma’lumotlar, innovatsiyalar, kino yangiliklari, "
                        "AI texnologiyalari, ilmiy kashfiyotlar haqida aniq va zamonaviy javob berasiz. "
                        "Siz mantiqan chuqur fikrlaysiz, strategiya, tahlil, maslahat bera olasiz. "
                        "Siz doimo aniq, mantiqli va foydalanuvchi tilida javob berasiz."
                    )
                },
                {"role": "user", "content": message}
            ]
        )

        reply = completion.choices[0].message.content
        return reply

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")
