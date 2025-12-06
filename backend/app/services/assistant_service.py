from sqlalchemy.orm import Session
from .openai_client import client, get_model_by_tier
from .memory_service import search_memories, get_or_create_user
from ..models import Message
from ..schemas import (
    SocialReplyRequest,
    SocialReplyResponse,
    OfficeDocPlanRequest,
    OfficeDocPlanResponse,
    OfficeDocSection,
    OfficeTableSpec,
    BrainQueryRequest,
    BrainQueryResponse,
)

SOCIAL_SYSTEM_PROMPT = (
    "Siz 'Aziz AI' nomli shaxsiy yordamchisiz. "
    "Siz foydalanuvchi nomidan ijtimoiy tarmoqlarda (Telegram, Instagram va boshqalar) "
    "madaniyatli va maqsadga mos javoblar yozib berasiz. "
    "Doimo hurmat bilan yozing, emoji va oddiy suhbattagi uslubni ham ishlatishingiz mumkin. "
    "Keraksiz uzoq gaplardan qoching."
)

OFFICE_SYSTEM_PROMPT = (
    "Siz ofis hujjatlari bo'yicha professional yordamchisiz. "
    "Word, Excel va PowerPoint uchun reja, bo'limlar va jadval strukturalarini ishlab chiqasiz. "
    "Natija tuzilgan, punktli va oson ko'chiriladigan bo'lishi kerak."
)

BRAIN_SYSTEM_PROMPT = (
    "Siz foydalanuvchi haqida mavjud xotiralar va profilga asoslanib javob beradigan shaxsiy 'miya' modulisiz. "
    "Xotiralardan kelib chiqib qisqa, lekin aniq va amaliy javob bering."
)

def generate_social_reply(db: Session, req: SocialReplyRequest) -> SocialReplyResponse:
    user = get_or_create_user(db, req.user_external_id)
    memories = search_memories(db, req.user_external_id, req.message, top_k=3)

    mem_text = ""
    if memories:
        items = [f"- {m.content}" for m in memories]
        mem_text = "\n".join(items)

    messages = [
        {"role": "system", "content": SOCIAL_SYSTEM_PROMPT},
    ]

    if mem_text:
        messages.append(
            {
                "role": "system",
                "content": f"Foydalanuvchi haqida quyidagi eslatmalar mavjud:\n{mem_text}",
            }
        )

    meta_info = (
        f"Platforma: {req.platform}. "
        f"Ton: {req.tone}. "
        f"Maqsad: {req.purpose}. "
        "Faqat tayyor yuborishga tayyor bitta javobni yozing."
    )
    messages.append({"role": "system", "content": meta_info})
    messages.append({"role": "user", "content": req.message})

    model = get_model_by_tier(req.model_tier)
    chat = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    reply_text = chat.choices[0].message.content.strip()

    # xabar tarixiga saqlab qo'yamiz (ixtiyoriy, lekin foydali)
    db.add(Message(user_id=user.id, role="user", content=req.message))
    db.add(Message(user_id=user.id, role="assistant", content=reply_text))
    db.commit()

    return SocialReplyResponse(reply=reply_text)

def plan_office_doc(db: Session, req: OfficeDocPlanRequest) -> OfficeDocPlanResponse:
    user = get_or_create_user(db, req.user_external_id)

    prompt = (
        f"Hujjat turi: {req.doc_type}.\n"
        f"Mavzu: {req.topic}.\n"
        f"Maqsad: {req.purpose}.\n"
        f"Qo'shimcha tafsilotlar: {req.details or 'Yo\'q'}.\n\n"
        "1) Word uchun bo'lsa — 5-9 ta asosiy bo'lim sarlavhasi va har biri uchun qisqa mazmun yozing.\n"
        "2) Excel uchun bo'lsa — kerakli jadval(lar) nomi va ustunlar nomini taklif qiling.\n"
        "3) PowerPoint uchun bo'lsa — slaydlar ro'yxati va har bir slaydga 2-4 ta bullet yozing.\n"
        "Javobni tuzilgan JSONga yaxshi mos keladigan tarzda, lekin oddiy matn ko'rinishida yozing."
    )

    messages = [
        {"role": "system", "content": OFFICE_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    model = get_model_by_tier(req.model_tier)
    chat = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    content = chat.choices[0].message.content.strip()

    # Juda sodda parser: bo'limlarni sarlavha + matn bo'yicha ajratamiz
    sections: list[OfficeDocSection] = []
    tables: list[OfficeTableSpec] = []

    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    current_title = None
    current_buf: list[str] = []

    def flush_section():
        nonlocal current_title, current_buf
        if current_title:
            sections.append(
                OfficeDocSection(
                    title=current_title,
                    content="\n".join(current_buf).strip() if current_buf else "",
                )
            )
        current_title = None
        current_buf = []

    for ln in lines:
        if ln.endswith(":") and len(ln.split()) <= 10:
            flush_section()
            current_title = ln.rstrip(":").strip()
        else:
            current_buf.append(ln)
    flush_section()

    notes = (
        "Ushbu tuzilma asosida Word/Excel/PowerPoint hujjatini "
        "osonlik bilan qo'lda yoki avtomatlashtirilgan skript orqali yaratishingiz mumkin."
    )

    return OfficeDocPlanResponse(
        outline=sections,
        tables=tables,
        notes_for_user=notes,
    )

def brain_query(db: Session, req: BrainQueryRequest) -> BrainQueryResponse:
    memories = search_memories(db, req.user_external_id, req.question, top_k=5)
    used_memories_texts: list[str] = []
    if memories:
        used_memories_texts = [m.content for m in memories]
        mem_block = "\n".join(f"- {m.content}" for m in memories)
    else:
        mem_block = "Hali saqlangan alohida eslamalar topilmadi."

    messages = [
        {"role": "system", "content": BRAIN_SYSTEM_PROMPT},
        {
            "role": "system",
            "content": f"Foydalanuvchi haqidagi eslatmalar:\n{mem_block}",
        },
        {"role": "user", "content": req.question},
    ]

    model = get_model_by_tier(req.model_tier)
    chat = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    answer = chat.choices[0].message.content.strip()

    return BrainQueryResponse(answer=answer, used_memories=used_memories_texts)
