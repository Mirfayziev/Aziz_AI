from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..schemas import (
    SocialReplyRequest,
    SocialReplyResponse,
    OfficeDocPlanRequest,
    OfficeDocPlanResponse,
    BrainQueryRequest,
    BrainQueryResponse,
)
from ..services.assistant_service import (
    generate_social_reply,
    plan_office_doc,
    brain_query,
)

router = APIRouter(tags=["assistant"])

@router.post("/social-reply", response_model=SocialReplyResponse)
def social_reply(req: SocialReplyRequest, db: Session = Depends(get_db)):
    try:
        return generate_social_reply(db, req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/office-plan", response_model=OfficeDocPlanResponse)
def office_plan(req: OfficeDocPlanRequest, db: Session = Depends(get_db)):
    try:
        return plan_office_doc(db, req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brain-query", response_model=BrainQueryResponse)
def brain_query_endpoint(req: BrainQueryRequest, db: Session = Depends(get_db)):
    try:
        return brain_query(db, req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from pydantic import BaseModel
from typing import Optional
import re
from app.services.external_data_service import get_weather, get_news, get_currency
from app.services.chat_service import create_chat_reply
from app.routers.tts import text_to_speech

class AssistantMessageRequest(BaseModel):
    external_id: str
    message: str
    want_voice: bool = True
    city: Optional[str] = None
    news_query: Optional[str] = None

def _looks_weather(t: str) -> bool:
    t = t.lower()
    return any(k in t for k in ["ob-havo", "obhavo", "havo", "harorat", "weather"])

def _looks_news(t: str) -> bool:
    t = t.lower()
    return any(k in t for k in ["yangilik", "news", "so'nggi yangilik", "so‘nggi yangilik"])

def _looks_currency(t: str) -> bool:
    t = t.lower()
    return any(k in t for k in ["valyuta", "kurs", "dollar", "usd", "eur", "rub", "курс"])

def _extract_city(text: str) -> Optional[str]:
    m = re.search(r"/ob-?havo\s+(.+)$", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"\b([A-Za-zА-Яа-яʻʼ’\- ]{3,})da\b.*\bhavo\b", text, flags=re.IGNORECASE)
    if m2:
        return m2.group(1).strip()
    return None

@router.post("/assistant-message")
async def assistant_message(req: AssistantMessageRequest, db: Session = Depends(get_db)):
    msg = (req.message or "").strip()
    tool = "chat"

    if _looks_weather(msg) or msg.lower().startswith("/ob-havo") or msg.lower().startswith("/obhavo"):
        city = req.city or _extract_city(msg)
        data = await get_weather(city=city, lang="uz")
        if data.get("ok"):
            tool = "weather"
            text = (
                f"🌤 Ob-havo ({data['city']}):\n"
                f"Holat: {data.get('description','—')}\n"
                f"Harorat: {data.get('temp_c','—')}°C (his: {data.get('feels_like_c','—')}°C)\n"
                f"Namlik: {data.get('humidity','—')}%\n"
                f"Shamol: {data.get('wind_mps','—')} m/s"
            )
        else:
            text = f"❌ Ob-havo: {data.get('error','xatolik')}"
    elif _looks_news(msg) or msg.lower().startswith("/yangilik"):
        q = req.news_query or msg.replace("/yangilik", "").strip() or None
        data = await get_news(query=q)
        if data.get("ok"):
            tool = "news"
            lines = [f"📰 Yangiliklar: {data['query']}\n"]
            for a in data.get("articles", []):
                title = a.get("title") or "—"
                src = a.get("source") or ""
                url = a.get("url") or ""
                lines.append(f"• {title}" + (f" ({src})" if src else ""))
                if url:
                    lines.append(url)
            text = "\n".join(lines).strip()
        else:
            text = f"❌ Yangiliklar: {data.get('error','xatolik')}"
    elif _looks_currency(msg) or msg.lower().startswith("/valyuta"):
        data = await get_currency(base="USD", symbols="UZS,EUR,RUB")
        tool = "currency"
        if data.get("ok"):
            if data.get("provider") == "cbu":
                rates = data.get("rates_in_uzs", {})
                lines = ["💱 Valyuta (CBU):"]
                for k,v in rates.items():
                    lines.append(f"1 {k} = {v} UZS")
                text = "\n".join(lines)
            else:
                rates = data.get("rates", {})
                lines = [f"💱 Valyuta (base: {data.get('base','USD')}):"]
                for k,v in rates.items():
                    lines.append(f"1 {data.get('base','USD')} = {v} {k}")
                text = "\n".join(lines)
        else:
            text = f"❌ Valyuta: {data.get('error','xatolik')}"
    else:
        text = create_chat_reply(db, req.external_id, msg)

    audio_hex = None
    if req.want_voice:
        try:
            audio = await text_to_speech({"text": text})
            audio_hex = audio.get("audio_base64")  # hex bytes of ogg
        except Exception:
            audio_hex = None

    return {"ok": True, "tool": tool, "text": text, "audio_hex": audio_hex}
