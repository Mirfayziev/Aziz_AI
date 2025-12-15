import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def chat_with_ai(text: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Sen Aziz AI — insoniy, muloyim va tabiiy ohangda javob ber."
            },
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content
