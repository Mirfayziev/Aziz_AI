# app/services/realtime.py

import os
import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/realtime")

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# =======================
# 1) OB-HAVO
# =======================

@router.get("/weather")
async def weather(city: str = "Tashkent"):
    if not WEATHER_API_KEY:
        return {"error": "WEATHER_API_KEY yo'q"}

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=uz"
    )

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.json()

# =======================
# 2) DOLLAR / EURO / RUB KURSLARI
# =======================

@router.get("/currency")
async def currency():
    url = "https://v6.exchangerate-api.com/v6/latest/USD"

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()

        if "conversion_rates" not in data:
            return {"error": "Kurs API ishlamadi"}

        rates = data["conversion_rates"]

        return {
            "USD_UZS": round(rates.get("UZS", 0)),
            "EUR_UZS": round(rates.get("UZS", 0) * 0.93),
            "RUB_UZS": round(rates.get("UZS", 0) * 0.011)
        }

# =======================
# 3) BITCOIN / ETH NARXLARI
# =======================

@router.get("/crypto")
async def crypto():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd"
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        data = r.json()

        return {
            "BTC_USD": data.get("bitcoin", {}).get("usd"),
            "ETH_USD": data.get("ethereum", {}).get("usd"),
        }

# =======================
# 4) SO‘NGGI YANGILIKLAR
# =======================

@router.get("/news")
async def news():
    if not NEWS_API_KEY:
        return {"error": "NEWS_API_KEY yo'q"}

    url = (
        f"https://newsapi.org/v2/top-headlines?"
        f"country=us&pageSize=5&apiKey={NEWS_API_KEY}"
    )

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()

        articles = data.get("articles", [])

        return [
            {
                "title": a.get("title"),
                "source": a.get("source", {}).get("name"),
                "url": a.get("url")
            }
            for a in articles
        ]
