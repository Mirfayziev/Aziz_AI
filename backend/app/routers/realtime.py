from fastapi import APIRouter
from services.realtime_service import (
    get_weather,
    get_news,
    get_crypto,
    get_currency
)

router = APIRouter(prefix="/api/realtime")

@router.get("/weather")
async def weather(city: str = "Tashkent"):
    return await get_weather(city)

@router.get("/news")
async def news():
    return await get_news()

@router.get("/crypto")
async def crypto():
    return await get_crypto()

@router.get("/currency")
async def currency():
    return await get_currency()
