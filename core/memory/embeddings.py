# core/memory/embeddings.py

import os
from openai import OpenAI

# OpenAI klient
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Embedding modeli
EMBED_MODEL = "text-embedding-3-large"

async def get_embedding(text: str):
    """Matndan vektor yaratish"""
    text = text.replace("\n", " ")
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding
