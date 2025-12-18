import os
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = "https://azizai-production.up.railway.app/aziz-ai"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom Aziz 👋\nAziz AI online.\n\nSavolingni yoz."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        r = requests.post(
            BACKEND_URL,
            json={"type": "chat", "text": user_text},
            timeout=30,
        )
        data = r.json()
        answer = data.get("text", "Javob yo‘q")
    except Exception:
        answer = "⚠️ Backend bilan aloqa yo‘q."

    await update.message.reply_text(answer)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        url_path="/telegram/webhook",
        webhook_url=f"{os.getenv('WEBHOOK_URL')}/telegram/webhook",
    )


if __name__ == "__main__":
    main()
