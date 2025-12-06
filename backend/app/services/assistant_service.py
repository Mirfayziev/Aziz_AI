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
    "Siz foydalanuvchi nomidan ijtimoiy tarmoqlarda madaniyatli va maqsadga mos javoblar yozib berasiz. "
    "Doimo hurmat bilan yozing, emoji va oddiy suhbattagi uslubni ishlatishingiz mumkin. "
    "Keraksiz uzoq gaplardan qoching."
)

OFFICE_SYSTEM_PROMPT = (
    "Siz ofis hujjatlari bo'yicha professional yordamchisiz. "
    "Word, Excel va PowerPoint uchun reja, bo'limlar va jadval strukturalarini ishlab chiqasiz. "
    "Natija tuzilgan, punktli va oson ko'chiriladigan bo'lishi kerak."
)

BRAIN_SYSTEM_PROMPT = (
    "Siz foydalanuvchi haqidagi xotira va profilga asoslanib javob beradigan shaxsiy 'miyasisiz'. "
    "Aniq, qisqa va amaliy javob bering."
)

def generate_social_reply(db: Session, req: SocialReplyRequest) -> SocialReplyResponse:
    user = get_or_create_user(db, req.user_external_id)
    memories = search_memories(db, req.user_external_id, req.message, top_k=3)

    mem_text = ""
    if memories:
        mem_text = "\n".join(f"- {m.content}" for m in memories)

    meta_info = (
        "Platforma: " + req.platform + ". "
        "Ton: " + req.tone + ". "
        "Maqsad: " + req.purpose + ". "
        "Faqat yuborishga tayyor bitta javob yozing."
    )

    messages = [
        {"role": "system", "content": SOCIAL_SYSTEM_PROMPT},
    ]

    if mem_text:
        messages.append({"role": "system", "content": "Foydalanuvchi haqidagi eslatmalar:\n" + mem_text})

    messages.append({"role": "system", "content": meta_info})
    messages.append({"role": "user", "content": req.message})

    model = get_model_by_tier(req.model_tier)
    chat = client.chat.completions.create(model=model, messages=messages)
    reply_text = chat.choices[0].message.content.strip()

    db.add(Message(user_id=user.id, role="user", content=req.message))
    db.add(Message(user_id=user.id, role="assistant", content=reply_text))
    db.commit()

    return SocialReplyResponse(reply=reply_text)


def plan_office_doc(db: Session, req: OfficeDocPlanRequest) -> OfficeDocPlanResponse:
    user = get_or_create_user(db, req.user_external_id)

    prompt = (
        "Hujjat turi: " + req.doc_type + "\n"
        "Mavzu: " + req.topic + "\n"
        "Maqsad: " + req.purpose + "\n"
        "Tafsilotlar: " + (req.details or "Yo'q") + "\n\n"
        "1) Word: 5-9 ta bo'lim va qisqa mazmun.\n"
        "2) Excel: jadval nomlari va ustunlar.\n"
        "3) PowerPoint: slaydlar ro'yxati va bulletlar.\n"
    )

    messages = [
        {"role": "system", "content": OFFICE_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    model = get_model_by_tier(req.model_tier)
    chat = client.chat.completions.create(model=model, messages=messages)
    content = chat.choices[0].message.content.strip()

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    sections = []
    tables = []

    current_title = None
    current_buf = []

    def flush():
        nonlocal current_title, current_buf, sections
        if current_title:
            sections.append(OfficeDocSection(title=current_title, content="\n".join(current_buf)))
        current_title = None
        current_buf = []

    for ln in lines:
        if ln.endswith(":") and len(ln.split()) <= 10:
            flush()
            current_title = ln[:-1]
        else:
            current_buf.append(ln)
    flush()

    notes = "Ushbu tuzilma asosida hujjatlarni oson yaratishingiz mumkin."

    return OfficeDocPlanResponse(outline=sections, tables=tables, notes_for_user=notes)


def brain_query(db: Session, req: BrainQueryRequest) -> BrainQueryResponse:
    memories = search_memories(db, req.user_external_id, req.question, top_k=5)

    if memories:
        mem_block = "\n".join(f"- {m.content}" for m in memories)
        used = [m.content for m in memories]
    else:
        mem_block = "Hali hech qanday eslatma saqlanmagan."
        used = []

    messages = [
        {"role": "system", "content": BRAIN_SYSTEM_PROMPT},
        {"role": "system", "content": "Foydalanuvchi haqidagi eslatmalar:\n" + mem_block},
        {"role": "user", "content": req.question},
    ]

    model = get_model_by_tier(req.model_tier)
    chat = client.chat.completions.create(model=model, messages=messages)
    answer = chat.choices[0].message.content.strip()

    return BrainQueryResponse(answer=answer, used_memories=used)
