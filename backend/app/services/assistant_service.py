import os
from sqlalchemy.orm import Session

from openai import OpenAI

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def brain_query(db: Session, req):
    """
    Aziz AI miyasi: text + (xohlasa) audio_hex qaytaradi.
    req: Pydantic object (BrainQueryRequest) yoki dict bo‘lishi mumkin.
    """

    # req dict bo‘lib kelib qolsa ham ishlashi uchun
    if isinstance(req, dict):
        external_id = str(req.get("external_id", "unknown"))
        user_text = req.get("message") or "Salom"
        want_voice = bool(req.get("want_voice", True))
    else:
        external_id = str(getattr(req, "external_id", "unknown"))
        user_text = getattr(req, "message", None) or "Salom"
        want_voice = bool(getattr(req, "want_voice", True))

    # === GPT javob ===
    chat = client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini"),
        messages=[
            {"role": "system", "content": "Sen Aziz AI. Foydalanuvchiga aniq va foydali javob ber."},
            {"role": "user", "content": user_text},
        ],
        temperature=0.7,
    )
    answer = chat.choices[0].message.content.strip()

    audio_hex = None
    if want_voice:
        # === TTS ===
        tts = client.audio.speech.create(
            model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
            voice=os.getenv("OPENAI_TTS_VOICE", "alloy"),
            input=answer,
        )
        audio_hex = tts.read().hex()

    return {"text": answer, "audio_hex": audio_hex}
