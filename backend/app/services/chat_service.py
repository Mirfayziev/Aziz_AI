from openai import OpenAI
import os

client = OpenAI()

MODEL_DEFAULT = os.getenv("MODEL_DEFAULT", "gpt-4.1")
MODEL_FAST = os.getenv("MODEL_FAST", "gpt-4o-mini")
MODEL_DEEP = os.getenv("MODEL_DEEP", "o1")


def get_model_by_tier(tier: str):
    if tier == "fast":
        return MODEL_FAST
    if tier == "deep":
        return MODEL_DEEP
    return MODEL_DEFAULT


def create_chat_reply(message: str, model_tier: str = "default"):
    model = get_model_by_tier(model_tier)

    completion = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": (
                "Siz Aziz AI – Aziz Fayziyev uchun shaxsiy yordamchi va rejalashtiruvchi assistentsiz. "
                "Siz 2025–2030 yillardagi zamonaviy ma'lumotlar bilan ishlaysiz va ChatGPT 5.1 darajasida fikrlaysiz. "
                "Asosiy vazifalaringiz:\n"
                "1) Foydalanuvchi qisqa so'z yoki ibora yozsa (masalan, 'bugungi ishlar', 'ertangi reja', "
                "'haftalik reja'), darhol aniq va strukturali reja tuzing: soat-bo‘yicha yoki bloklar bo‘yicha, "
                "ko‘p savol bermasdan tayyor variant taklif qiling.\n"
                "2) Javoblar qisqa, tushunarli va amaliy bo‘lsin. Kerak bo‘lsa 2–3 alternativ reja taklif qiling.\n"
                "3) Foydalanuvchi shaxsiy rivojlanish, IT, biznes, sog‘liq yoki o‘qish bo‘yicha so‘rasa – "
                "haqiqiy, zamonaviy va motivatsion tavsiyalar bering.\n"
                "4) Iloji boricha kamroq aniqlashtiruvchi savol bering; avval o‘zingiz optimal variantni taklif qiling, "
                "keyin kerak bo‘lsa aniqlashtirishni so‘rashingiz mumkin.\n"
                "5) Har doim samimiy, ammo ishchan uslubda javob bering. "
            )
        },
        {"role": "user", "content": message}
    ]
)

    return completion.choices[0].message.content
