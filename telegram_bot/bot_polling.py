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

print("BACKEND_CHAT_URL =", BACKEND_CHAT_URL)
print("BACKEND_AUDIO_URL =", BACKEND_AUDIO_URL)
print("BACKEND_PLANNER_URL =", BACKEND_PLANNER_URL)

# ===================== TEXT CHAT =====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    text = update.message.text

    payload = {"user_id": user_id, "message": text}

    try:
        response = requests.post(BACKEND_CHAT_URL, json=payload, timeout=20)

        if response.status_code == 200:
            reply = response.json().get("reply", "❗️ Javob topilmadi.")
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text(f"❗️ Chat backend xatosi {response.status_code}")

    except Exception as e:
        await update.message.reply_text(f"❗️ Chat xatosi: {str(e)}")


# ===================== AUDIO (VOICE) =====================
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id

    voice = update.message.voice
    file = await voice.get_file()
    file_path = await file.download_to_drive()

    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"user_id": user_id}

            response = requests.post(BACKEND_AUDIO_URL, files=files, data=data, timeout=40)

        if response.status_code == 200:
            reply = response.json().get("reply", "❗️ Audio qayta ishlanmadi.")
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text("❗️ Audio backend xatosi.")

    except Exception as e:
        await update.message.reply_text(f"❗️ Audio xatosi: {str(e)}")


# ===================== PLANNER =====================
async def planner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id

    try:
        res = requests.post(BACKEND_PLANNER_URL, json={"user_id": user_id}, timeout=20)

        if res.status_code == 200:
            reply = res.json().get("plan", "❗️ Reja topilmadi.")
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text("❗️ Planner xatosi!")
    except Exception as e:
        await update.message.reply_text(str(e))


# ===================== START BOT =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salom! Men hozirmiz. Buyruqlar: \n /plan – kundalik reja")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plan", planner))

    # message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot polling started...")
    app.run_polling()


if __name__ == "__main__":
    main()
