import httpx
from datetime import datetime
from app.models.daily_routine import DailyRoutine
from app.services.config import WEATHER_API_KEY, NEWS_API_KEY


async def get_weather(city: str):
    """OpenWeatherMap orqali real ob-havo olish"""
    if not WEATHER_API_KEY:
        return "⚠️ Ob-havo API kaliti mavjud emas."

    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric", "lang": "uz"}

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)

    if r.status_code != 200:
        return "⚠️ Ob-havo ma'lumotini olishda xatolik."

    data = r.json()
    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    desc = data["weather"][0]["description"]

    return f"{city} shahrida hozir {temp}°C, sezilishi {feels}°C. Havo: {desc}."


async def get_latest_news():
    """NewsAPI orqali so‘nggi yangiliklarni olish"""
    if not NEWS_API_KEY:
        return "⚠️ Yangiliklar API kaliti mavjud emas."

    url = "https://newsapi.org/v2/top-headlines"
    params = {"country": "us", "apiKey": NEWS_API_KEY, "pageSize": 5}

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)

    if r.status_code != 200:
        return "⚠️ Yangiliklarni olishda xatolik yuz berdi."

    articles = r.json().get("articles", [])
    if not articles:
        return "⚠️ Yangiliklar topilmadi."

    text = "📰 So‘nggi yangiliklar:\n\n"
    for a in articles:
        text += f"- {a['title']} ({a['source']['name']})\n"

    return text


def analyze_daily_routine(routine: DailyRoutine) -> str:
    """Kun tartibini chuqur tahlil qilish va taklif berish"""

    score = 0
    tips = []

    # Uyg‘onish
    if routine.wake_time > 8:
        tips.append("• Ertaroq uyg‘onish samaradorlikni oshiradi.")
    else:
        score += 1

    # Nonushta
    if not routine.breakfast:
        tips.append("• Nonushta qilmaslik energiya pasayishiga olib keladi.")

    # Uyqu
    if routine.sleep_hours < 6:
        tips.append("• Kam uxlayapsiz, kamida 7-8 soat tavsiya etiladi.")
    else:
        score += 1

    # Ish balansi
    if routine.work_hours > 10:
        tips.append("• Juda ko‘p ishlayapsiz, mental charchash xavfi yuqori.")
    else:
        score += 1

    # Sport
    if not routine.exercise:
        tips.append("• Kuniga 10–20 min yurish yoki yengil mashqlar qo‘shing.")

    result = f"📊 Kun tartibi bo‘yicha tahlil natijasi: {score}/4\n"
    if tips:
        result += "\nTavsiya va takliflar:\n" + "\n".join(tips)

    return result


async def create_chat_reply(db, external_id: str, message: str):
    """
    Asosiy AI javob generatsiya qiluvchi funksiyaga
    real-time modul (weather/news/daily analysis) ni qo‘shib ketamiz.
    """

    msg = message.lower().strip()

    # OB-HAVO BLOKI
    if any(x in msg for x in ["ob havo", "havo", "weather"]):
        return await get_weather("Tashkent")

    # YANGILIKLAR BLOKI
    if any(x in msg for x in ["yangilik", "news", "so‘nggi yangilik"]):
        return await get_latest_news()

    # KUN TARTIBI TАHLILI BLOKI
    if "kun tartibi" in msg or "routine" in msg:
        sample = DailyRoutine(
            wake_time=8,
            breakfast=False,
            work_hours=10,
            sleep_hours=5,
            exercise=False
        )
        return analyze_daily_routine(sample)

    # 🔥 ASOSIY AI JAVOBI (hozircha mock — sizning backend AI bilan ulaysiz)
    return f"🤖 AI javobi: {message}"
