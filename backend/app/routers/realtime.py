import os
import httpx
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/realtime", tags=["realtime"])

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# ==================================================
# 1) OB-HAVO (REAL-TIME)
# ==================================================

@router.get("/weather")
async def weather(city: str = Query(default="Tashkent", max_length=50)):
    if not WEATHER_API_KEY:
        return {"error": "WEATHER_API_KEY yo'q"}

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "uz"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        data = r.json()

    if "main" not in data:
        return {"error": "Ob-havo topilmadi"}

    return {
        "city": city,
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["description"]
    }

# ==================================================
# 2) VALYUTA KURSLARI (USD / EUR / RUB → UZS)
# ==================================================

@router.get("/currency")
async def currency():
    url = "https://v6.exchangerate-api.com/v6/latest/USD"

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        data = r.json()

    rates = data.get("conversion_rates")
    if not rates:
        return {"error": "Valyuta API ishlamadi"}

    uzs = rates.get("UZS", 0)

    return {
        "USD_UZS": round(uzs),
        "EUR_UZS": round(uzs * 0.93),
        "RUB_UZS": round(uzs * 0.011)
    }

# ==================================================
# 3) KRIPTO (BITCOIN / ETH)
# ==================================================

@router.get("/crypto")
async def crypto():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        data = r.json()

    return {
        "BTC_USD": data.get("bitcoin", {}).get("usd"),
        "ETH_USD": data.get("ethereum", {}).get("usd")
    }

# ==================================================
# 4) SO‘NGGI YANGILIKLAR (REAL-TIME)
# ==================================================

@router.get("/news")
async def news(limit: int = Query(default=5, le=10)):
    if not NEWS_API_KEY:
        return {"error": "NEWS_API_KEY yo'q"}

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "pageSize": limit,
        "apiKey": NEWS_API_KEY
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        data = r.json()

    articles = data.get("articles", [])

    return [
        {
            "title": a.get("title"),
            "source": a.get("source", {}).get("name"),
            "url": a.get("url")
        }
        for a in articles
        if a.get("title")
    ]
