import os
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

async def chat_with_ai(text: str) -> str:
    """
    OpenAI bilan asosiy chat
    """
    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Sen Aziz AI san. Foydalanuvchiga aniq, tushunarli va foydali javob ber."},
            {"role": "user", "content": text}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content
