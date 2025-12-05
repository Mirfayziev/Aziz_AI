import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL")  # https://azizai-production.up.railway.app/api/chat


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom, Aziz! Men tayyorman 🤖")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user_id = str(update.message.chat.id)

    try:
        r = requests.post(
            BACKEND_CHAT_URL,
            json={"user_id": user_id, "message": text},
            timeout=20
        )

        reply = r.json().get("reply", "❗️ Backend javob bermadi")
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"❗️ Xatolik: {e}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🤖 Bot polling started...")
    app.run_polling()


if __name__ == "__main__":
    main()
