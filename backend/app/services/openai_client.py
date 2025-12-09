from openai import OpenAI
from ..config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_model_by_tier(tier: str) -> str:
    tier = tier.lower()
    if tier == "fast":
        return settings.MODEL_FAST
    if tier == "deep":
        return settings.MODEL_DEEP
    return settings.MODEL_DEFAULT
