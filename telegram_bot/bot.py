import os
import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp

# ---------------------------
# ENVIRONMENT VARIABLES
# ---------------------------

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")    # https://azizai-production.up.railway.app/api/chat/chat
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL") # https://azizai-production.up.railway.app/api/audio
TTS_URL = os.getenv("AZIZ_BACKEND_TTS_URL")     # https://azizai-production.up.railway.app/api/tts

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN topilmadi")
if not CHAT_URL:
    raise ValueError("AZIZ_BACKEND_CHAT_URL topilmadi")

# ---------------------------
# LOGGING
# ---------------------------

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("aziz_ai_bot")

# ---------------------------
# TELEGRAM API
# ---------------------------

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
TELEGRAM_FILE_API = f"https://api.telegram.org/file/bot{TOKEN}"


async def tg_get_updates(session: aiohttp.ClientSession, offset: int) -> Dict[str, Any]:
    params = {"timeout": 30, "offset": offset}
    async with session.get(f"{TELEGRAM_API}/getUpdates", params=params) as resp:
        return await resp.json()


async def tg_send_message(session: aiohttp.ClientSession, chat_id: int, text: str) -> None:
    payload = {"chat_id": chat_id, "text": text}
    await session.post(f"{TELEGRAM_API}/sendMessage", json=payload)


async def tg_send_voice(session: aiohttp.ClientSession, chat_id: int, audio_bytes: bytes) -> None:
    form = aiohttp.FormData()
    form.add_field("voice", audio_bytes, filename="reply.ogg", content_type="audio/ogg")

    await session.post(
        f"{TELEGRAM_API}/sendVoice",
        data=form,
        params={"chat_id": chat_id}
    )


async def tg_get_file_path(session: aiohttp.ClientSession, file_id: str) -> Optional[str]:
    async with session.get(f"{TELEGRAM_API}/getFile", params={"file_id": file_id}) as resp:
        data = await resp.json()
        if not data.get("ok"):
            log.error("getFile failed: %s", data)
            return None
        return data["result"]["file_path"]


async def tg_download_file(session: aiohttp.ClientSession, file_path: str) -> bytes:
    async with session.get(f"{TELEGRAM_FILE_API}/{file_path}") as resp:
        return await resp.read()


# ---------------------------
# BACKEND CHAT (QUERY PARAMS)
# ---------------------------

async def backend_chat(session: aiohttp.ClientSession, message: str, external_id: str) -> str:
    payload = {
        "message": message,
        "external_id": external_id
    }

    async with session.post(CHAT_URL, params=payload) as resp:
        if resp.status != 200:
            log.error("Backend chat status: %s", resp.status)
            return f"⚠️ Backend xatosi: {resp.status}"

        data = await resp.json()

        if isinstance(data, dict):
            return data.get("response") or data.get("reply") or str(data)

        return str(data)


# ---------------------------
# AUDIO (Speech → Text)
# ---------------------------

async def backend_transcribe_audio(session: aiohttp.ClientSession, voice_bytes: bytes, filename: str = "voice.ogg") -> Optional[str]:
    if not AUDIO_URL:
        return None

    form = aiohttp.FormData()
    form.add_field("file", voice_bytes, filename=filename, content_type="audio/ogg")

    async with session.post(AUDIO_URL, data=form) as resp:
        if resp.status != 200:
            log.error("Backend audio status: %s", resp.status)
            return None

        data = await resp.json()
        if isinstance(data, dict):
            return data.get("text") or data.get("transcript")

        return None


# ---------------------------
# TEXT → SPEECH (AI OVOZLI JAVOB)
# ---------------------------

async def backend_text_to_speech(session: aiohttp.ClientSession, text: str) -> Optional[bytes]:
    if not TTS_URL:
        return None

    async with session.post(TTS_URL, params={"text": text}) as resp:
        if resp.status != 200:
            log.error("Backend TTS status: %s", resp.status)
            return None

        data = await resp.json()
        audio_hex = data.get("audio_base64")

        if not audio_hex:
            return None

        return bytes.fromhex(audio_hex)


# ---------------------------
# UPDATE ISHLOVCHISI
# ---------------------------

async def process_update(session: aiohttp.ClientSession, update: Dict[str, Any]) -> None:
    try:
        message = update.get("message") or update.get("edited_message")
        if not message:
            return

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        if chat_id is None:
            return

        text = message.get("text")

        # /start
        if text == "/start":
            await tg_send_message(
                session,
                chat_id,
                "✅ Aziz AI ishga tushdi!\nMatn yoki ovoz yuboring."
            )
            return

        # -----------------------
        # MATNLI XABAR
        # -----------------------
        if text and not text.startswith("/"):
            reply = await backend_chat(session, text, str(chat_id))
            await tg_send_message(session, chat_id, reply)

            # ✅ AI OVOZLI JAVOB
            if TTS_URL:
                audio_reply = await backend_text_to_speech(session, reply)
                if audio_reply:
                    await tg_send_voice(session, chat_id, audio_reply)

            return

        # -----------------------
        # OVOZLI XABAR
        # -----------------------
        if "voice" in message and AUDIO_URL:
            voice = message["voice"]
            file_id = voice["file_id"]

            await tg_send_message(session, chat_id, "🎤 Ovoz qabul qilindi...")

            file_path = await tg_get_file_path(session, file_id)
            if not file_path:
                await tg_send_message(session, chat_id, "❌ Ovoz olinmadi.")
                return

            voice_bytes = await tg_download_file(session, file_path)

            text_from_audio = await backend_transcribe_audio(session, voice_bytes)
            if not text_from_audio:
                await tg_send_message(session, chat_id, "❌ Ovozdan matn olinmadi.")
                return

            await tg_send_message(session, chat_id, f"📝 Matn:\n{text_from_audio}")

            reply = await backend_chat(session, text_from_audio, str(chat_id))
            await tg_send_message(session, chat_id, reply)

            # ✅ AI OVOZLI JAVOB
            if TTS_URL:
                audio_reply = await backend_text_to_speech(session, reply)
                if audio_reply:
                    await tg_send_voice(session, chat_id, audio_reply)

    except Exception as e:
        log.exception("process_update xatosi: %s", e)


# ---------------------------
# POLLING
# ---------------------------

async def polling() -> None:
    offset = 0
    log.info("✅ Aziz AI Telegram Bot ishga tushdi (ovozli javob bilan)...")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                data = await tg_get_updates(session, offset)
                if "result" in data:
                    for update in data["result"]:
                        offset = update["update_id"] + 1
                        await process_update(session, update)
            except Exception as e:
                log.exception("Polling xatosi: %s", e)

            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(polling())
