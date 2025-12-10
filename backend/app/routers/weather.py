from fastapi import APIRouter
import httpx
import os

router = APIRouter(tags=["weather"])

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

@router.get("")
async def get_weather(city: str = "Tashkent"):
    if not WEATHER_API_KEY:
        return {"error": "WEATHER_API_KEY topilmadi"}

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "uz"
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params)

    data = r.json()

    if r.status_code != 200:
        return {"error": "Ob-havo maʼlumotini olishda xatolik"}

    return {
        "city": city,
        "temp": round(data["main"]["temp"], 1),
        "feels_like": round(data["main"]["feels_like"], 1),
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"]
    }
