import base64
import re
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.schemas import (
    SocialReplyRequest,
    SocialReplyResponse,
    OfficeDocPlanRequest,
    OfficeDocPlanResponse,
    BrainQueryRequest,
    BrainQueryResponse,
)
from app.services.assistant_service import (
    generate_social_reply,
    plan_office_doc,
    brain_query,
)
from app.services.chat_service import chat_with_ai
from app.services.external_data_service import get_weather, get_news, get_currency
from app.services.tts_service import text_to_speech_bytes

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/social-reply", response_model=SocialReplyResponse)
async def social_reply(req: SocialReplyRequest):
    try:
        return await generate_social_reply(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/office-plan", response_model=OfficeDocPlanResponse)
async def office_plan(req: OfficeDocPlanRequest):
    try:
        return await plan_office_doc(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/brain-query", response_model=BrainQueryResponse)
async def brain_query_endpoint(req: BrainQueryRequest):
    try:
        answer, _ = await brain_query(req.question)
        return BrainQueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AssistantMessageRequest(BaseModel):
    user_external_id: str
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
async def assistant_message(req: AssistantMessageRequest):
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
                for k, v in rates.items():
                    lines.append(f"1 {k} = {v} UZS")
                text = "\n".join(lines)
            else:
                rates = data.get("rates", {})
                lines = [f"💱 Valyuta (base: {data.get('base','USD')}):"]
                for k, v in rates.items():
                    lines.append(f"1 {data.get('base','USD')} = {v} {k}")
                text = "\n".join(lines)
        else:
            text = f"❌ Valyuta: {data.get('error','xatolik')}"
    else:
        text = await chat_with_ai(text=msg, user_id=req.user_external_id)

    audio_base64 = None
    if req.want_voice:
        try:
            audio_bytes = await text_to_speech_bytes(text)
            audio_base64 = base64.b64encode(audio_bytes).decode("ascii")
        except Exception:
            audio_base64 = None

    return {"ok": True, "tool": tool, "text": text, "audio_base64": audio_base64}
