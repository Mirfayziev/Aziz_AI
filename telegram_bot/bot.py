import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Backend FastAPI endpoint
BACKEND_URL = "https://azizai-production.up.railway.app/aziz-ai"

app = ApplicationBuilder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom Aziz 👋\nAziz AI online.\n\nSavolingni yoz."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = requests.post(
            BACKEND_URL,
            json={
                "type": "chat",
                "text": user_text,
            },
            timeout=30,
        )

        data = response.json()
        answer = data.get("text", "Javob yo‘q")

    except Exception:
        answer = "⚠️ Backend bilan aloqa yo‘q."

    await update.message.reply_text(answer)


app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))


if __name__ == "__main__":
    app.run_polling()
