import os
import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp

# ---------------------------
# ENVIRONMENT VARIABLES
# ---------------------------

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")
TTS_URL = os.getenv("AZIZ_BACKEND_TTS_URL")

# REPLY MODE: text / voice / both
REPLY_MODE = os.getenv("BOT_REPLY_MODE", "text").lower()

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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger("aziz_ai_bot")


# ---------------------------
# TELEGRAM API HELPERS
# ---------------------------

async def tg_send_message(session, chat_id, text, reply_to=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to

    async with session.post(f"{TELEGRAM_API}/sendMessage", json=payload) as resp:
        res = await resp.json()
        if not res.get("ok"):
            log.error("sendMessage error: %s", res)


async def tg_send_voice(session, chat_id, voice_bytes, reply_to=None):
    form = aiohttp.FormData()
    form.add_field("chat_id", str(chat_id))
    form.add_field("voice", voice_bytes, filename="voice.mp3", content_type="audio/mpeg")

    if reply_to:
        form.add_field("reply_to_message_id", str(reply_to))

    async with session.post(f"{TELEGRAM_API}/sendVoice", data=form) as resp:
        res = await resp.json()
        if not res.get("ok"):
            log.error("sendVoice error: %s", res)


async def tg_get_updates(session, offset=None):
    params = {"timeout": 25}
    if offset:
        params["offset"] = offset
    async with session.get(f"{TELEGRAM_API}/getUpdates", params=params) as resp:
        return await resp.json()


async def tg_get_file(session, file_id):
    async with session.get(f"{TELEGRAM_API}/getFile", params={"file_id": file_id}) as resp:
        data = await resp.json()
        if data.get("ok"):
            return data["result"]["file_path"]
        return None


async def tg_download_file(session, path):
    url = f"{TELEGRAM_FILE_API}/{path}"
    async with session.get(url) as resp:
        if resp.status == 200:
            return await resp.read()
        return None


# ---------------------------
# BACKEND HELPERS
# ---------------------------

async def backend_chat(session, chat_id, message):
    params = {"message": message, "external_id": str(chat_id)}
    async with session.post(CHAT_URL, params=params) as resp:
        if resp.status != 200:
            return "⚠️ Back-end bilan ulanishda xato yuz berdi."
        data = await resp.json()
        return data.get("reply") or data.get("text") or str(data)


async def backend_transcribe_audio(session, audio_bytes):
    form = aiohttp.FormData()
    form.add_field("file", audio_bytes, filename="voice.ogg", content_type="audio/ogg")

    async with session.post(AUDIO_URL, data=form) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
        return data.get("text") or data.get("transcript")


async def backend_tts(session, text):
    if REPLY_MODE == "text":
        return None  # ovozli javobni o‘chiradi

    async with session.post(TTS_URL, json={"text": text}) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
        if not data.get("audio_base64"):
            return None
        return bytes.fromhex(data["audio_base64"])


# ---------------------------
# UPDATE HANDLER
# ---------------------------

async def process_update(session, update):
    try:
        msg = update.get("message") or update.get("edited_message")
        if not msg:
            return

        chat_id = msg["chat"]["id"]
        msg_id = msg.get("message_id")
        text = msg.get("text")

        # ---------------------------
        # TEXT MESSAGE
        # ---------------------------
        if text:
            user_text = text.strip()

            reply = await backend_chat(session, chat_id, user_text)
            await tg_send_message(session, chat_id, reply, reply_to=msg_id)

            if REPLY_MODE in ["voice", "both"]:
                audio = await backend_tts(session, reply)
                if audio:
                    await tg_send_voice(session, chat_id, audio, reply_to=msg_id)

            return

        # ---------------------------
        # VOICE MESSAGE
        # ---------------------------
        if msg.get("voice"):
            file_id = msg["voice"]["file_id"]
            file_path = await tg_get_file(session, file_id)
            audio_bytes = await tg_download_file(session, file_path)

            text_from_audio = await backend_transcribe_audio(session, audio_bytes)
            if not text_from_audio:
                await tg_send_message(session, chat_id, "❌ Ovozdan matn olinmadi.", reply_to=msg_id)
                return

            await tg_send_message(session, chat_id, f"📝 Matn:\n{text_from_audio}", reply_to=msg_id)

            reply = await backend_chat(session, chat_id, text_from_audio)
            await tg_send_message(session, chat_id, reply, reply_to=msg_id)

            if REPLY_MODE in ["voice", "both"]:
                audio = await backend_tts(session, reply)
                if audio:
                    await tg_send_voice(session, chat_id, audio, reply_to=msg_id)

    except Exception as e:
        log.exception("process_update error: %s", e)


# ---------------------------
# POLLING LOOP
# ---------------------------

async def polling():
    offset = None
    async with aiohttp.ClientSession() as session:
        log.info("Aziz AI Bot Started...")
        while True:
            try:
                updates = await tg_get_updates(session, offset)
                if updates.get("result"):
                    for u in updates["result"]:
                        offset = u["update_id"] + 1
                        await process_update(session, u)
            except Exception as e:
                log.exception("Polling error: %s", e)

            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(polling())
