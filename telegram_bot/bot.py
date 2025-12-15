import base64
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def brain_query(user_id: str, text: str, need_audio: bool):
    # 1. AI response
    chat = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Sen Aziz AI — foydalanuvchining shaxsiy klonisan. Internetdan foydalanishing mumkin."},
            {"role": "user", "content": text}
        ]
    )

    answer = chat.choices[0].message.content

    # 2. TTS (chiroyli ovoz)
    audio_b64 = None
    if need_audio:
        audio = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=answer
        )
        audio_b64 = base64.b64encode(audio.read()).decode()

    return {
        "text": answer,
        "audio_base64": audio_b64
    }
