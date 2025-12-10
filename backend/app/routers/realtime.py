from fastapi import APIRouter
import httpx
import os

router = APIRouter(tags=["realtime"])

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# ✅ 1. VALYUTA KURSLARI (USD, EUR, RUB)
@router.get("/currency")
async def currency():
    url = "https://api.exchangerate.host/latest"
    params = {"base": "USD", "symbols": "UZS,EUR,RUB"}

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        data = r.json()

    return {
        "USD_UZS": data["rates"]["UZS"],
        "USD_EUR": data["rates"]["EUR"],
        "USD_RUB": data["rates"]["RUB"]
    }


# ✅ 2. KRIPTO (BTC, ETH)
@router.get("/crypto")
async def crypto():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd"
    }

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        data = r.json()

    return {
        "BTC_USD": data["bitcoin"]["usd"],
        "ETH_USD": data["ethereum"]["usd"]
    }


# ✅ 3. OB-HAVO (Toshkent)
@router.get("/weather")
async def weather(city: str = "Tashkent"):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "uz"
    }

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        data = r.json()

    return {
        "city": city,
        "temp": data["main"]["temp"],
        "description": data["weather"][0]["description"]
    }


# ✅ 4. SO‘NGGI YANGILIKLAR
@router.get("/news")
async def news():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        data = r.json()

    headlines = [a["title"] for a in data.get("articles", [])]
    return {"news": headlines}
