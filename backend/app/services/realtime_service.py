import os
import httpx

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


# ==================================================
# OB-HAVO (REAL-TIME)
# ==================================================

async def get_weather(city: str = "Tashkent") -> dict:
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
# YANGILIKLAR (REAL-TIME)
# ==================================================

async def get_news(limit: int = 5) -> list:
    if not NEWS_API_KEY:
        return []

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


# ==================================================
# KRIPTOVALYUTA (REAL-TIME)
# ==================================================

async def get_crypto() -> dict:
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
# VALYUTA KURSLARI (REAL-TIME)
# ==================================================

async def get_currency() -> dict:
    url = "https://v6.exchangerate-api.com/v6/latest/USD"

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        data = r.json()

    rates = data.get("conversion_rates", {})
    uzs = rates.get("UZS", 0)

    return {
        "USD_UZS": round(uzs),
        "EUR_UZS": round(uzs * 0.93),
        "RUB_UZS": round(uzs * 0.011)
    }


# ==================================================
# AI UCHUN YAGONA REAL-TIME KIRISH NUQTASI
# ==================================================

async def get_realtime_data(query: str):
    """
    Foydalanuvchi savoliga qarab qaysi real-time manba kerakligini aniqlaydi
    va mos ma'lumotni qaytaradi.
    """
    q = query.lower()

    # -------- YANGILIKLAR --------
    if any(k in q for k in [
        "yangilik", "yangiliklar", "xabar", "xabarlar",
        "bugun", "bugungi", "news", "headline"
    ]):
        return {
            "type": "news",
            "data": await get_news()
        }

    # -------- OB-HAVO --------
    if any(k in q for k in [
        "ob-havo", "ob havo", "bugun ob-havo", "bugungi ob-havo",
        "harorat", "yomg'ir", "shamol", "weather", "today"
    ]):
        return {
            "type": "weather",
            "data": await get_weather()
        }

    # -------- KRIPTO --------
    if any(k in q for k in [
        "bitcoin", "btc", "eth", "kripto", "crypto"
    ]):
        return {
            "type": "crypto",
            "data": await get_crypto()
        }

    # -------- VALYUTA --------
    if any(k in q for k in [
        "dollar", "kurs", "valyuta", "usd", "eur", "rubl"
    ]):
        return {
            "type": "currency",
            "data": await get_currency()
        }

    return None
