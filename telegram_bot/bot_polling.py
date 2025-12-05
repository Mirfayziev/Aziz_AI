import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# URL larni tozalash — bu eng muhim qadam!
BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL", "").strip()
BACKEND_AUDIO_URL = os.getenv("BACKEND_AUDIO_URL", "").strip()

print("BACKEND_CHAT_URL =", BACKEND_CHAT_URL)
print("BACKEND_AUDIO_URL =", BACKEND_AUDIO_URL)

if not BACKEND_CHAT_URL:
    raise ValueError("❌ BACKEND_CHAT_URL o‘rnatilmagan!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Aziz AI tayyor! Xabar yuboring.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message = update.message.text

    try:
        payload = {
            "user_id": user_id,
            "message": message
        }

        res = requests.post(
            BACKEND_CHAT_URL,
            json=payload,
            timeout=25
        )

        if res.status_code != 200:
            await update.message.reply_text("❗ Backend javobi xato.")
            print("Backend error:", res.text)
            return

        data = res.json()
        reply = data.get("reply", "")

        if reply:
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text("❗ AI javob qaytarmadi.")
            print("Empty AI reply:", data)

    except Exception as e:
        await update.message.reply_text("❗ AI javob qaytarmadi.")
        print("Bot error:", e)


# ---- BOT ----
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
