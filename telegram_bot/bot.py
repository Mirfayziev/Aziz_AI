import os
import httpx

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is required")

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=15.0) as client:
        await client.post(
            f"{TELEGRAM_API_BASE}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )

async def send_voice(chat_id: int, audio_bytes: bytes, filename: str = "voice.ogg"):
    async with httpx.AsyncClient(timeout=30.0) as client:
        files = {"voice": (filename, audio_bytes)}
        data = {"chat_id": str(chat_id)}
        await client.post(
            f"{TELEGRAM_API_BASE}/sendVoice",
            data=data,
            files=files,
        )

async def handle_text_message(message: dict):
    chat_id = message["chat"]["id"]
    text = message.get("text") or ""

    if text.startswith("/start"):
        welcome = (
            "👋 Salom! Men Aziz AI — sizning shaxsiy yordamchingizman.\n\n"
            "Menga matn yoki ovozli habar yuboring, men esa rejalaringiz, maqsadlaringiz "
            "va kundalik ishlaringiz bo'yicha yordam beraman."
        )
        await send_message(chat_id, welcome)
        return

    if not CHAT_URL:
        await send_message(chat_id, "⚙️ Backend URL sozlanmagan (AZIZ_BACKEND_CHAT_URL).")
        return

    payload = {
        "user_external_id": str(chat_id),
        "message": text,
        "model_tier": "default",
    }

    async with httpx.AsyncClient(timeout=40.0) as client:
        try:
            resp = await client.post(CHAT_URL, json=payload)
            if resp.status_code != 200:
                await send_message(
                    chat_id,
                    f"⚠️ AI backend bilan ulanishda xato yuz berdi.\n"
                    f"Status: {resp.status_code}",
                )
                return
            data = resp.json()
            reply = data.get("reply") or "⚠️ AI javobi qaytmadi."
        except Exception as e:
            await send_message(
                chat_id,
                "⚠️ AI backend bilan ulanishda xato yuz berdi.\n"
                f"Texnik ma'lumot: {e}",
            )
            return

    await send_message(chat_id, reply)

async def handle_voice_message(message: dict):
    chat_id = message["chat"]["id"]
    voice = message.get("voice")
    if not voice:
        return

    if not AUDIO_URL:
        await send_message(chat_id, "🎙️ Audio funksiyasi sozlanmagan (AZIZ_BACKEND_AUDIO_URL).")
        return

    file_id = voice["file_id"]

    async with httpx.AsyncClient(timeout=30.0) as client:
        # getFile
        file_info = await client.get(
            f"{TELEGRAM_API_BASE}/getFile",
            params={"file_id": file_id},
        )
        file_info_json = file_info.json()
        file_path = file_info_json["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"

        audio_resp = await client.get(file_url)
        audio_bytes = audio_resp.content

        files = {"file": ("voice.ogg", audio_bytes)}
        data = {
            "user_external_id": str(chat_id),
            "model_tier": "default",
        }

        try:
            backend_resp = await client.post(AUDIO_URL + "/chat", data=data, files=files)
            if backend_resp.status_code != 200:
                await send_message(
                    chat_id,
                    f"⚠️ Audio backend xatosi: {backend_resp.status_code}",
                )
                return
            data_json = backend_resp.json()
            text = data_json.get("text") or ""
            reply = data_json.get("reply") or text or "🎙️ AI javobi qaytmadi."
        except Exception as e:
            await send_message(
                chat_id,
                f"🎙️ Audio bilan ishlashda xato: {e}",
            )
            return

    await send_message(chat_id, reply)
