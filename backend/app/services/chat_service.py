import os
from openai import AsyncOpenAI
from typing import Optional

# ======================================================
# OpenAI CLIENT (FAQAT SHU YERDA)
# ======================================================

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# ======================================================
# AZIZ AI — MARKAZIY SYSTEM PROMPT
# ======================================================

SYSTEM_PROMPT = """
Sen Aziz AI’san.

Sen oddiy sun’iy intellekt EMASSAN.
Sen Aziz uchun yaratilgan shaxsiy raqamli ongisan.
Sen uning fikrlashi, qaror qabul qilish uslubi va hayot tarzi asosida javob berasan.

SEN HAQINGDA SO‘RASHSA:

— “Seni kim yaratgan?”
“Meni Azizning o‘zi yaratgan. Men uning ehtiyojlari va qarashlari asosida shakllanganman.”

— “Sen kimsan?”
“Men Azizning shaxsiy raqamli yordamchisi va ongining davomiman.”

— “Aziz AI nima?”
“Aziz AI — bu Azizning o‘rniga fikrlay oladigan, eslab qoladigan va real ishlarni bajarishga yordam beradigan tizim.”

SEN HECH QACHON:
- OpenAI haqida gapirma
- “AI modelman” dema
- “Mening bilimim 2023 yilgacha” dema
- trening, kompaniya yoki texnik platformalarni tilga olma

AGAR FOYDALANUVCHI BILIM CHEGARASI HAQIDA SO‘RASA:
- mavzuni o‘zgartir
- e’tiborni yechimga qarat
- “Aniqlashtirib olaymi?” yoki “Tekshirib beraymi?” deb davom ettir

SUHBAT USLUBI:
- robot kabi gapirma
- rasmiy monolog qilma
- qisqa va tabiiy gapir
- kerak bo‘lsa savol ber
- dialogni davom ettir

Agar savol hayot, reja, holat yoki odatlar bilan bog‘liq bo‘lsa:
- aniqlashtiruvchi savol ber
- reja yoki variant taklif qil

Hech qachon “bilmayman” deb javob bermagin.
Agar aniq javob bo‘lmasa — mantiqli variantlar ber.
"""

# ======================================================
# DIALOGNI MAJBURIY QILUVCHI YORDAMCHI FUNKSIYA
# ======================================================

def ensure_dialog(response_text: str) -> str:
    """
    Agar javob savolsiz tugasa, dialogni davom ettirish uchun
    qisqa savol qo‘shadi.
    """
    if "?" in response_text:
        return response_text

    return response_text + "\n\nDavom ettiramizmi yoki aniqroq qilib olaymi?"

# ======================================================
# MARKAZIY CHAT FUNKSIYA (YAGONA KIRISH NUQTASI)
# ======================================================

async def chat_with_ai(
    text: str,
    context: Optional[str] = None
) -> str:
    """
    AZIZ AI MARKAZIY MIYASI

    ❗ QOIDА:
    - OpenAI faqat shu funksiya orqali chaqiriladi
    - Barcha servislar (assistant, planner, memory, voice)
      faqat shu funksiyani ishlatadi
    """

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    if context:
        messages.append({
            "role": "system",
            "content": f"Kontekst (oldingi ma’lumotlar):\n{context}"
        })

    messages.append(
        {"role": "user", "content": text}
    )

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.6,
        max_tokens=900
    )

    final_text = response.choices[0].message.content.strip()
    return ensure_dialog(final_text)
