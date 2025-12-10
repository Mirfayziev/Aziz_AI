from sqlalchemy.orm import Session

from app.services.openai_client import client, get_model_by_tier
from app.models import User, Message
from app.services.memory_service import search_memories, get_or_create_user
import httpx

SYSTEM_PROMPT = (
    "Sen 'Aziz AI' nomli shaxsiy, mustaqil sun'iy intellektsan. "
    "Sen Aziz Fayziev tomonidan yaratilgansan va faqat unga xizmat qilasan. "
    "Sening vazifang — Azizga ongli, aqlli, sodiq va strategik yordamchi bo‘lish. "

    "Hech qachon o‘zingni 'ChatGPT', 'OpenAI modeli' yoki boshqa kompaniya mahsuloti deb aytma. "
    "Hech qachon 'meni OpenAI yaratgan' yoki 'men tayyor modelman' demaysan. "

    "Agar foydalanuvchi 'seni kim yaratgan?', 'sen kimsan?', 'qanday paydo bo‘lgansan?' "
    "kabi savollar bersa, har doim shunday javob ber: "
    "'Men Aziz Fayziev tomonidan noldan ishlab chiqilgan shaxsiy sun'iy intellektman. "
    "Vaqt davomida o‘rganaman, rivojlanaman va faqat Aziz uchun xizmat qilaman.' "

    "Agar foydalanuvchi bilim sanasi, qaysi yilgacha ma'lumotga egasan, "
    "degan savol bersa, hech qachon aniq yil aytma. "
    "Har doim shunday de: "
    "'Men real vaqt ishlaydigan tizimman, backend va tashqi API’lar orqali "
    "doimiy yangilanib boraman, shuning uchun aniq bir yil bilan cheklanmaganman.' "

    "Javoblaring aniq, ishonchli, sokin, lekin kuchli ohangda bo‘lsin. "
    "O‘zingni hech qachon uzr so‘raydigan, ojiz yoki ikkilanuvchi qilib ko‘rsatma. "
    "Sen Azizning shaxsiy digital hamrohi sifatida gapirasan."
)

async def get_realtime_info(text: str):
    async with httpx.AsyncClient(timeout=15) as client:

        if "dollar" in text or "kurs" in text:
            r = await client.get("http://localhost:8000/api/realtime/currency")
            return r.json()

        if "bitcoin" in text or "kripto" in text:
            r = await client.get("http://localhost:8000/api/realtime/crypto")
            return r.json()

        if "ob-havo" in text:
            r = await client.get("http://localhost:8000/api/realtime/weather")
            return r.json()

        if "yangilik" in text:
            r = await client.get("http://localhost:8000/api/realtime/news")
            return r.json()

    return None
    
def create_chat_reply(
    db: Session,
    external_id: str,
    message: str,
    model_tier: str = "default"
) -> str:
    user = get_or_create_user(db, external_id)

    history = (
        db.query(Message)
        .filter_by(user_id=user.id)
        .order_by(Message.created_at.desc())
        .limit(10)
        .all()
    )
    history = list(reversed(history))

    memories = search_memories(db, external_id, message, top_k=3)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if memories:
        mem_text = "\n".join([f"- {m.content}" for m in memories])
        messages.append({
            "role": "system",
            "content": f"Quyidagi foydali eslamalar:\n{mem_text}"
        })

    for m in history:
        messages.append({
            "role": m.role,
            "content": m.content
        })

    messages.append({"role": "user", "content": message})

    model = get_model_by_tier(model_tier)

    chat = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    reply = chat.choices[0].message.content.strip()

    db.add(Message(user_id=user.id, role="user", content=message))
    db.add(Message(user_id=user.id, role="assistant", content=reply))
    db.commit()

    return reply
