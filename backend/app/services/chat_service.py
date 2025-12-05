from sqlalchemy.orm import Session
from .openai_client import client, get_model_by_tier
from ..models import User, Message
from .memory_service import search_memories, get_or_create_user

SYSTEM_PROMPT = (
    "Siz 'Aziz AI' nomli shaxsiy yordamchisiz. "
    "Foydalanuvchi Aziz Fayziev bilan uzoq muddatli munosabatga ega bo'lasiz. "
    "Profil ma'lumotlari, maqsadlari va kundalik odatlarini yodda tuting. "
    "Javoblaringiz qisqa, aniq va samimiy bo'lsin."
)

def create_chat_reply(
    db: Session,
    external_id: str,
    message: str,
    model_tier: str = "default"
) -> str:
    user = get_or_create_user(db, external_id)

    # Oxirgi 10 ta xabarni tarix sifatida olamiz
    history = (
        db.query(Message)
        .filter_by(user_id=user.id)
        .order_by(Message.created_at.desc())
        .limit(10)
        .all()
    )
    history = list(reversed(history))

    # Eslanmalar (vector memory) bilan kontekst
    memories = search_memories(db, external_id, message, top_k=3)

    # OpenAI chat so'rovini tayyorlash
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if memories:
        mem_text = "\n".join([f"- {m.content}" for m in memories])
        messages.append({
            "role": "system",
            "content": f"Quyidagi foydali eslamalar: \n{mem_text}"
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

    # bazaga saqlash
    db.add(Message(user_id=user.id, role="user", content=message))
    db.add(Message(user_id=user.id, role="assistant", content=reply))
    db.commit()

    return reply
