from fastapi import APIRouter, Query
from app.services.external_data_service import get_weather, get_news, get_currency

router = APIRouter(prefix="/api", tags=["External"])

@router.get("/weather")
async def weather(city: str = Query(None), lang: str = Query("uz")):
    data = await get_weather(city=city, lang=lang)
    if not data.get("ok"):
        return {"ok": False, "text": f"❌ Ob-havo: {data.get('error')}", "raw": data}
    text = (
        f"🌤 Ob-havo ({data['city']}):\n"
        f"Holat: {data.get('description','—')}\n"
        f"Harorat: {data.get('temp_c','—')}°C (his: {data.get('feels_like_c','—')}°C)\n"
        f"Namlik: {data.get('humidity','—')}%\n"
        f"Shamol: {data.get('wind_mps','—')} m/s"
    )
    return {"ok": True, "text": text, "raw": data}

@router.get("/news")
async def news(q: str = Query(None)):
    data = await get_news(query=q)
    if not data.get("ok"):
        return {"ok": False, "text": f"❌ Yangiliklar: {data.get('error')}", "raw": data}
    lines = [f"📰 Yangiliklar: {data['query']}\n"]
    for a in data.get("articles", []):
        title = a.get("title") or "—"
        src = a.get("source") or ""
        url = a.get("url") or ""
        lines.append(f"• {title}" + (f" ({src})" if src else ""))
        if url:
            lines.append(url)
    return {"ok": True, "text": "\n".join(lines).strip(), "raw": data}

@router.get("/currency")
async def currency(base: str = Query("USD"), symbols: str = Query("UZS,EUR,RUB")):
    data = await get_currency(base=base, symbols=symbols)
    if not data.get("ok"):
        return {"ok": False, "text": f"❌ Valyuta: {data.get('error')}", "raw": data}
    if data.get("provider") == "cbu":
        rates = data.get("rates_in_uzs", {})
        lines = ["💱 Valyuta (CBU):"]
        for k,v in rates.items():
            lines.append(f"1 {k} = {v} UZS")
        return {"ok": True, "text": "\n".join(lines), "raw": data}

    rates = data.get("rates", {})
    lines = [f"💱 Valyuta (base: {data.get('base', base)}):"]
    for k,v in rates.items():
        lines.append(f"1 {data.get('base', base)} = {v} {k}")
    return {"ok": True, "text": "\n".join(lines), "raw": data}
