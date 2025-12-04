import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from sqlalchemy.orm import Session

from app import schemas
from app.core.config import settings
from app.database import get_db
from app.models import MemoryEntry, VectorMemory
from app.utils_vector import cosine_similarity

router = APIRouter(prefix="/chat", tags=["chat"])

client = OpenAI(api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"))


def get_embeddings(text: str) -> List[float]:
    if not text.strip():
        return []
    try:
        emb = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
        )
        return emb.data[0].embedding
    except Exception:
        return []


@router.post("/", response_model=schemas.ChatReply)
def chat(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    if not settings.OPENAI_API_KEY and not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY topilmadi")

    # 1) History (oxirgi 15 ta)
    history_entries = (
        db.query(MemoryEntry)
        .filter(MemoryEntry.chat_id == req.chat_id)
        .order_by(MemoryEntry.created_at.asc())
        .limit(15)
        .all()
    )
    history_msgs: List[dict] = []
    for m in history_entries:
        history_msgs.append({"role": m.role, "content": m.content})

    # 2) Semantik o'xshash xotiralarni topish (vector memory)
    emb_query = get_embeddings(req.message)
    similar_msgs: List[dict] = []
    if emb_query:
        candidates = (
            db.query(VectorMemory)
            .filter(VectorMemory.chat_id == req.chat_id)
            .all()
        )
        scored = []
        for c in candidates:
            if not c.embedding:
                continue
            score = cosine_similarity(emb_query, c.embedding)
            scored.append((score, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = [c for s, c in scored[:5] if s > 0.5]

        for c in top:
            similar_msgs.append(
                {
                    "role": "system",
                    "content": f"Avvalgi muhim kontekst: {c.content}",
                }
            )

    messages: List[dict] = []
    messages.append(
        {
            "role": "system",
            "content": "Sen Azizning shaxsiy AI yordamchisisan. "
                       "Faqat Aziz uchun ishlaysan, suhbatdan o'rganasan, lekin hech qachon shaxsiy ma'lumotlarni boshqalar bilan ulashmaysan.",
        }
    )
    messages.extend(similar_msgs)
    messages.extend(history_msgs)
    messages.append({"role": "user", "content": req.message})

    try:
        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI xato: {e}")

    reply = completion.choices[0].message["content"]

    # 3) Oddiy xotira (MemoryEntry)
    user_mem = MemoryEntry(chat_id=req.chat_id, role="user", content=req.message)
    asst_mem = MemoryEntry(chat_id=req.chat_id, role="assistant", content=reply)
    db.add(user_mem)
    db.add(asst_mem)
    db.commit()
    db.refresh(user_mem)

    # 4) Vektor xotira (faqat user xabarlarini saqlaymiz)
    if emb_query:
        v = VectorMemory(
            chat_id=req.chat_id,
            message_id=user_mem.id,
            role="user",
            content=req.message,
            embedding=emb_query,
        )
        db.add(v)
        db.commit()

    return schemas.ChatReply(reply=reply)
