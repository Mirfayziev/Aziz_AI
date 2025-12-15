from __future__ import annotations
import os
import httpx
from typing import Optional, Dict, Any

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
CURRENCY_PROVIDER = os.getenv("CURRENCY_PROVIDER", "cbu").lower()  # cbu | exchangerate
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY", "")

DEFAULT_CITY = os.getenv("WEATHER_DEFAULT_CITY", "Tashkent")
NEWS_DEFAULT_QUERY = os.getenv("NEWS_DEFAULT_QUERY", "Uzbekistan")
NEWS_LANG = os.getenv("NEWS_LANG", "ru")
MAX_NEWS_ITEMS = int(os.getenv("MAX_NEWS_ITEMS", "5"))

async def get_weather(city: Optional[str] = None, lang: str = "uz") -> Dict[str, Any]:
    city = (city or DEFAULT_CITY).strip()
    if not WEATHER_API_KEY:
        return {"ok": False, "error": "WEATHER_API_KEY is not set", "city": city}

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric", "lang": lang}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params)
        if r.status_code != 200:
            return {"ok": False, "error": f"OpenWeather error {r.status_code}", "city": city, "details": r.text}
        data = r.json()

    w = (data.get("weather") or [{}])[0]
    main = data.get("main") or {}
    wind = data.get("wind") or {}
    return {
        "ok": True,
        "city": data.get("name", city),
        "description": w.get("description"),
        "temp_c": main.get("temp"),
        "feels_like_c": main.get("feels_like"),
        "humidity": main.get("humidity"),
        "wind_mps": wind.get("speed"),
    }

async def get_news(query: Optional[str] = None) -> Dict[str, Any]:
    q = (query or NEWS_DEFAULT_QUERY).strip()
    if not NEWS_API_KEY:
        return {"ok": False, "error": "NEWS_API_KEY is not set", "query": q}

    url = "https://newsapi.org/v2/everything"
    params = {"q": q, "language": NEWS_LANG, "pageSize": MAX_NEWS_ITEMS, "sortBy": "publishedAt"}
    headers = {"X-Api-Key": NEWS_API_KEY}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params, headers=headers)
        if r.status_code != 200:
            return {"ok": False, "error": f"NewsAPI error {r.status_code}", "query": q, "details": r.text}
        data = r.json()

    articles = []
    for a in (data.get("articles") or [])[:MAX_NEWS_ITEMS]:
        articles.append({
            "title": a.get("title"),
            "source": (a.get("source") or {}).get("name"),
            "url": a.get("url"),
            "publishedAt": a.get("publishedAt"),
        })
    return {"ok": True, "query": q, "articles": articles}

async def get_currency(base: str = "USD", symbols: str = "UZS,EUR,RUB") -> Dict[str, Any]:
    base = base.upper().strip()
    symbols_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]

    if CURRENCY_PROVIDER == "cbu":
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get("https://cbu.uz/ru/arkhiv-kursov-valyut/json/")
            if r.status_code != 200:
                return {"ok": False, "error": f"CBU error {r.status_code}", "details": r.text}
            data = r.json()
        rates = {}
        for code in symbols_list:
            if code in ["UZS", base]:
                continue
            item = next((x for x in data if x.get("Ccy") == code), None)
            if item and item.get("Rate"):
                rates[code] = float(item["Rate"])
        return {"ok": True, "provider": "cbu", "base": "UZS", "rates_in_uzs": rates}

    url = "https://api.exchangerate.host/latest"
    params = {"base": base, "symbols": ",".join(symbols_list)}
    if CURRENCY_API_KEY:
        params["apikey"] = CURRENCY_API_KEY
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params)
        if r.status_code != 200:
            return {"ok": False, "error": f"ExchangeRate error {r.status_code}", "details": r.text}
        data = r.json()
    return {"ok": True, "provider": "exchangerate.host", "base": data.get("base", base), "date": data.get("date"), "rates": data.get("rates") or {}}
