import os
import httpx

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


# ==================================================
# SHAHARNI AJRATISH
# ==================================================
def extract_city(query: str) -> str | None:
    q = query.lower()

    cities = [
        "toshkent", "tashkent",
        "samarqand", "samarkand",
        "buxoro", "bukhara",
        "andijon", "andijan",
        "farg'ona", "fergana",
        "namangan",
        "qarshi",
        "nukus"
    ]

    for city in cities:
        if city in q:
            return city.capitalize()

    return None


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
        return {"error": f"{city} uchun ob-havo topilmadi"}

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
    q = query.lower()

    # -------- OB-HAVO (1-PRIORITET) --------
    if any(k in q for k in [
        "ob-havo", "ob havo", "obhavo",
        "harorat", "yomg'ir", "yomgir",
        "shamol", "weather", "forecast", "prognoz"
    ]):
        city = extract_city(query) or "Tashkent"
        return {
            "type": "weather",
            "data": await get_weather(city)
        }

    # -------- YANGILIKLAR --------
    if any(k in q for k in [
        "yangilik", "yangiliklar",
        "xabar", "xabarlar",
        "news", "headline"
    ]):
        return {
            "type": "news",
            "data": await get_news()
        }

    # -------- KRIPTO --------
    if any(k in q for k in ["bitcoin", "btc", "eth", "kripto", "crypto"]):
        return {
            "type": "crypto",
            "data": await get_crypto()
        }

    # -------- VALYUTA --------
    if any(k in q for k in ["dollar", "kurs", "valyuta", "usd", "eur", "rubl", "rub"]):
        return {
            "type": "currency",
            "data": await get_currency()
        }

    return None
