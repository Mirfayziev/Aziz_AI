# core/personality/service.py

from core.personality.model import personality
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def apply_personality(user_message: str) -> str:
    """
    Foydalanuvchi xabariga Aziz AI shaxs modelini qo‘llaydi.
    """

    system_prompt = f"""
    Sen {personality.name}, {personality.role}.
    Gapirish uslubi: {personality.speaking_style}.
    Ovozing: {personality.tone_style}.

    SENING ASOSIY QOIDALARING:
    {personality.core_values}

    SENING XOTIRA QOIDALARING:
    {personality.memory_rules}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
    )

    return response.choices[0].message["content"]
