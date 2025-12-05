
import os
import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL", "").strip().rstrip("/")
BACKEND_AUDIO_URL = os.getenv("BACKEND_AUDIO_URL", "").strip().rstrip("/")
BACKEND_PLANNER_URL = os.getenv("BACKEND_PLANNER_URL", "").strip().rstrip("/")


def _is_planner_trigger(text: str) -> bool:
    t = text.lower()
    triggers = [
        "bugungi ishlar",
        "bugungi reja",
        "ertangi reja",
        "haftalik reja",
        "oylik reja",
        "plan tuz",
        "reja tuz",
    ]
    return any(x in t for x in triggers)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Aziz AI tayyor!\n"
        "- Matn yozing: chat javobi olasiz\n"
        "- Ovoz yuboring: ovozdan matn va javob olasiz\n"
        "- 'bugungi ishlar' deb yozsangiz planner ishga tushadi."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    text = update.message.text or ""

    # Planner trigger
    if BACKEND_PLANNER_URL and _is_planner_trigger(text):
        try:
            payload = {"user_id": user_id, "query": text}
            r = requests.post(BACKEND_PLANNER_URL, json=payload, timeout=40)
            if r.status_code != 200:
                await update.message.reply_text("⚠️ Planner xatosi.")
                logger.error("Planner error %s %s", r.status_code, r.text)
                return
            data = r.json()
            plan = data.get("result", "⚠️ Reja qaytmadi.")
            await update.message.reply_text(f"🗓 Reja:\n\n{plan}")
            return
        except Exception as e:
            await update.message.reply_text(f"⚠️ Planner API xatosi: {e}")
            return

    # Chat
    try:
        payload = {"user_id": user_id, "message": text}
        r = requests.post(BACKEND_CHAT_URL, json=payload, timeout=30)
        if r.status_code != 200:
            await update.message.reply_text("❗ Chat backend xatosi.")
            logger.error("Chat error %s %s", r.status_code, r.text)
            return
        data = r.json()
        reply = data.get("reply", "")
        if not reply:
            await update.message.reply_text("❗ AI javob qaytarmadi.")
            logger.error("Empty reply: %s", data)
            return
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("❗ AI javob qaytarmadi.")
        logger.exception("Chat exception: %s", e)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not BACKEND_AUDIO_URL:
        await update.message.reply_text("⚠️ Audio uchun BACKEND_AUDIO_URL sozlanmagan.")
        return

    user_id = str(update.effective_chat.id)
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    file_bytes = await file.download_as_bytearray()

    files = {"file": ("voice.ogg", file_bytes, "audio/ogg")}
    data = {"user_id": user_id}

    try:
        r = requests.post(BACKEND_AUDIO_URL, data=data, files=files, timeout=60)
        if r.status_code != 200:
            await update.message.reply_text("⚠️ Audio backend xatosi.")
            logger.error("Audio error %s %s", r.status_code, r.text)
            return
        data = r.json()
        text = data.get("text", "(matn olinmadi)")
        reply = data.get("reply", "(javob olinmadi)")
        await update.message.reply_text(f"🎙 Matn: {text}\n\n🤖 Javob: {reply}")
    except Exception as e:
        await update.message.reply_text("⚠️ Audio qayta ishlash xatosi.")
        logger.exception("Audio exception: %s", e)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN o'rnatilmagan.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Aziz AI Telegram bot polling boshlandi...")
    app.run_polling()


if __name__ == "__main__":
    main()
