from fastapi import APIRouter
import httpx
import os

router = APIRouter()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


@router.get("/weather")
async def weather(city: str = "Tashkent"):
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

    if r.status_code != 200:
        return {"error": "OpenWeather API xato javob berdi", "status": r.status_code}

    data = r.json()

    return {
        "city": city,
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"]
    }


@router.get("/currency")
async def currency():
    url = "https://api.exchangerate.host/latest"

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)

    if r.status_code != 200:
        return {"error": "Currency API xato javob berdi"}

    data = r.json()

    return data.get("rates", {})


@router.get("/crypto")
async def crypto():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)

    if r.status_code != 200:
        return {"error": "Crypto API xato berdi"}

    return r.json()


@router.get("/news")
async def news():
    if not NEWS_API_KEY:
        return {"error": "NEWS_API_KEY yo'q"}

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)

    if r.status_code != 200:
        return {"error": "News API xato berdi"}

    return r.json()
