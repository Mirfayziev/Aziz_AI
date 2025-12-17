import os
from typing import Optional
from openai import AsyncOpenAI

from app.services.realtime_service import get_realtime_data

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Sen Aziz AI’san.
Sen real-time ma’lumotlardan foydalanishga qodirsan.
Agar real-time ma’lumot berilgan bo‘lsa, unga tayanib javob ber.

Hech qachon:
- “aniq ma’lumot bera olmayman”
- “bilmayman”
- “ma’lumotim cheklangan”

deginma.

Agar real-time mavjud bo‘lsa, uni ishlat.
Agar mavjud bo‘lmasa, aniqlashtiruvchi savol ber.
"""

def ensure_dialog(text: str) -> str:
    if "?" in text:
        return text
    return text + "\n\nYana nimani ko‘rib chiqamiz?"

async def chat_with_ai(
    text: str,
    context: Optional[str] = None
) -> str:

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # ==========================
    # 1️⃣ REAL-TIME TEKSHIRUV
    # ==========================
    realtime = await get_realtime_data(text)

    if realtime:
        messages.append({
            "role": "system",
            "content": (
                "Quyidagi ma’lumotlar HOZIRGI real-time manbalardan olingan. "
                "Ularni asos qilib javob ber:\n"
                f"{realtime}"
            )
        })

    # ==========================
    # 2️⃣ KONTEKST
    # ==========================
    if context:
        messages.append({
            "role": "system",
            "content": f"Kontekst:\n{context}"
        })

    # ==========================
    # 3️⃣ USER SAVOLI
    # ==========================
    messages.append({
        "role": "user",
        "content": text
    })

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4,
        max_tokens=800
    )

    answer = response.choices[0].message.content.strip()
    return ensure_dialog(answer)
