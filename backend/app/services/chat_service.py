import os
from typing import Optional
from openai import AsyncOpenAI

from app.services.realtime_service import get_realtime_data

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Sen Aziz AI’san.

MUHIM QOIDA:
Agar system message ichida REAL-TIME DATA berilgan bo‘lsa,
u MA’LUMOT 100% HAQIQIY deb qabul qilinadi.

Sen HECH QACHON:
- “real-time ma’lumot yo‘q”
- “aniq ma’lumot bera olmayman”
- “tekshirib ko‘rish kerak”

demaysan, AGAR real-time data berilgan bo‘lsa.

Agar real-time data mavjud bo‘lsa:
- uni soddalashtirib tushuntir
- insoniy qilib ayt
- oxirida bitta savol bilan yakunla

Agar real-time data YO‘Q bo‘lsa:
- aniqlashtiruvchi savol ber

Ob-havo uchun:
- agar shahar berilgan bo‘lsa, o‘sha shaharni ishlat
- agar berilmagan bo‘lsa, default Toshkentni ol
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

