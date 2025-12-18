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

# MUHIM: sen ishlatayotgan endpoint
BACKEND_URL = "https://azizai-production.up.railway.app/api/chat"

app = ApplicationBuilder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom Aziz 👋\n"
        "Aziz AI online.\n\n"
        "Savolingni yoz."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        r = requests.post(
            BACKEND_URL,
            json={"text": text},
            timeout=30,
        )
        data = r.json()
        answer = data.get("answer", "Javob yo‘q")
    except Exception:
        answer = "⚠️ Backend bilan aloqa yo‘q."

    await update.message.reply_text(answer)


app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))


if __name__ == "__main__":
    app.run_polling()
