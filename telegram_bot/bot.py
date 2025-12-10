import os
import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp

# ---------------------------
# ENVIRONMENT VARIABLES
# ---------------------------

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")     # masalan: https://azizai-production.up.railway.app/api/chat/chat
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")   # masalan: https://azizai-production.up.railway.app/api/audio
TTS_URL = os.getenv("AZIZ_BACKEND_TTS_URL")       # masalan: https://azizai-production.up.railway.app/api/tts

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environmentda topilmadi")

if not CHAT_URL:
    raise RuntimeError("AZIZ_BACKEND_CHAT_URL environmentda topilmadi")

if not AUDIO_URL:
    raise RuntimeError("AZIZ_BACKEND_AUDIO_URL environmentda topilmadi")

if not TTS_URL:
    raise RuntimeError("AZIZ_BACKEND_TTS_URL environmentda topilmadi")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
TELEGRAM_FILE_API = f"https://api.telegram.org/file/bot{TOKEN}"

# ---------------------------
# LOGGING
# ---------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger("aziz_ai_bot")


# ---------------------------
# TELEGRAM API HELPERS
# ---------------------------

async def tg_get_updates(session: aiohttp.ClientSession, offset: Optional[int] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {"timeout": 25}
    if offset is not None:
        params["offset"] = offset

    async with session.get(f"{TELEGRAM_API}/getUpdates", params=params) as resp:
        return await resp.json()


async def tg_send_message(
    session: aiohttp.ClientSession,
    chat_id: int,
    text: str,
    reply_to_message_id: Optional[int] = None,
) -> None:
    payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id

    async with session.post(f"{TELEGRAM_API}/sendMessage", json=payload) as resp:
        data = await resp.json()
        if not data.get("ok"):
            log.error("Telegram sendMessage error: %s", data)


async def tg_send_voice(
    session: aiohttp.ClientSession,
    chat_id: int,
    voice_bytes: bytes,
    reply_to_message_id: Optional[int] = None,
) -> None:
    form = aiohttp.FormData()
    form.add_field("chat_id", str(chat_id))
    form.add_field(
        "voice",
        voice_bytes,
        filename="reply.mp3",
        content_type="audio/mpeg",
    )
    if reply_to_message_id:
        form.add_field("reply_to_message_id", str(reply_to_message_id))

    async with session.post(f"{TELEGRAM_API}/sendVoice", data=form) as resp:
        data = await resp.json()
        if not data.get("ok"):
            log.error("Telegram sendVoice error: %s", data)


async def tg_get_file(session: aiohttp.ClientSession, file_id: str) -> Optional[str]:
    async with session.get(f"{TELEGRAM_API}/getFile", params={"file_id": file_id}) as resp:
        data = await resp.json()
        if data.get("ok") and data.get("result"):
            return data["result"]["file_path"]
        log.error("Telegram getFile error: %s", data)
        return None


async def tg_download_file(session: aiohttp.ClientSession, file_path: str) -> Optional[bytes]:
    url = f"{TELEGRAM_FILE_API}/{file_path}"
    async with session.get(url) as resp:
        if resp.status != 200:
            log.error("Telegram download file status: %s", resp.status)
            return None
        return await resp.read()


# ---------------------------
# BACKEND HELPERS
# ---------------------------

async def backend_chat(session: aiohttp.ClientSession, chat_id: int, message: str) -> str:
    """
    Chat endpoint: /api/chat/chat
    FastAPI bu yerda query param sifatida qabul qilmoqda: message, external_id.
    """
    params = {
        "message": message,
        "external_id": str(chat_id),
    }
    async with session.post(CHAT_URL, params=params) as resp:
        if resp.status != 200:
            log.error("Backend chat status: %s", resp.status)
            return "⚠️ Back-end bilan ulanishda xatolik yuz berdi."

        data = await resp.json()
        if isinstance(data, dict):
            return data.get("reply") or data.get("text") or str(data)
        return str(data)


async def backend_transcribe_audio(
    session: aiohttp.ClientSession,
    voice_bytes: bytes,
    filename: str = "voice.ogg",
) -> Optional[str]:
    """
    Audio endpoint: /api/audio
    file (audio/ogg) bilan FormData yuboriladi, javobda 'text' yoki 'transcript' kutiladi.
    """
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


async def backend_tts(session: aiohttp.ClientSession, text: str) -> Optional[bytes]:
    """
    TTS endpoint: /api/tts
    JSON body: {"text": "..."} yuboramiz.
    Javob: {"audio_base64": "<hex-encoded-bytes>"}.
    """
    if not text:
        return None

    try:
        async with session.post(
            TTS_URL,
            json={"text": text},
            headers={"Content-Type": "application/json"},
        ) as resp:
            if resp.status != 200:
                log.error("Backend TTS status: %s", resp.status)
                return None

            data = await resp.json()
            audio_hex = data.get("audio_base64")
            if not audio_hex:
                log.error("Backend TTS: audio_base64 yo'q")
                return None

            return bytes.fromhex(audio_hex)

    except Exception as e:
        log.error("TTS exception: %s", e)
        return None


# ---------------------------
# UPDATE (XABAR)NI QAYTA ISHLASH
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

        message_id = message.get("message_id")
        text = message.get("text")

        # -------- TEXT MESSAGE --------
        if text:
            text_strip = text.strip()

            if text_strip.startswith("/start"):
                welcome = (
                    "Assalomu alaykum! 👋\n\n"
                    "Men *Aziz AI* — sizning shaxsiy yordamchingiz.\n"
                    "Matn yozing yoki ovozli xabar yuboring — men javob beraman, "
                    "hatto ovoz bilan ham javob qaytara olaman. 🔊"
                )
                await tg_send_message(session, chat_id, welcome, reply_to_message_id=message_id)
                return

            # oddiy chat oqimi
            user_text = text_strip
            reply_text = await backend_chat(session, chat_id, user_text)
            await tg_send_message(session, chat_id, reply_text, reply_to_message_id=message_id)

            # ovozli javob
            audio_bytes = await backend_tts(session, reply_text)
            if audio_bytes:
                await tg_send_voice(session, chat_id, audio_bytes, reply_to_message_id=message_id)

            return

        # -------- VOICE MESSAGE --------
        voice = message.get("voice")
        if voice:
            file_id = voice.get("file_id")
            if not file_id:
                return

            await tg_send_message(session, chat_id, "🎤 Ovoz qabul qilindi...", reply_to_message_id=message_id)

            file_path = await tg_get_file(session, file_id)
            if not file_path:
                await tg_send_message(session, chat_id, "❌ Ovoz faylini olishda xato bo'ldi.")
                return

            voice_bytes = await tg_download_file(session, file_path)
            if not voice_bytes:
                await tg_send_message(session, chat_id, "❌ Ovoz faylini yuklashda xato bo'ldi.")
                return

            # STT: Ovoz → Matn
            text_from_audio = await backend_transcribe_audio(session, voice_bytes)
            if not text_from_audio:
                await tg_send_message(session, chat_id, "❌ Ovozdan matn olinmadi.", reply_to_message_id=message_id)
                return

            await tg_send_message(
                session,
                chat_id,
                f"📝 Matn:\n{text_from_audio}",
                reply_to_message_id=message_id,
            )

            # Chat javobi
            reply_text = await backend_chat(session, chat_id, text_from_audio)
            await tg_send_message(session, chat_id, reply_text, reply_to_message_id=message_id)

            # TTS: Matn → Ovoz
            audio_bytes = await backend_tts(session, reply_text)
            if audio_bytes:
                await tg_send_voice(session, chat_id, audio_bytes, reply_to_message_id=message_id)

    except Exception as e:
        log.exception("Update processing error: %s", e)


# ---------------------------
# POLLING LOOP
# ---------------------------

async def polling() -> None:
    offset: Optional[int] = None

    async with aiohttp.ClientSession() as session:
        log.info("Aziz AI Telegram Bot ishga tushdi (ovozli javob bilan)...")

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
