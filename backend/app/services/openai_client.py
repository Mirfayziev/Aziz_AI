import os
from openai import AsyncOpenAI

# ======================================================
# YAGONA OPENAI CLIENT (BUTUN LOYIHA UCHUN)
# ======================================================

openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
