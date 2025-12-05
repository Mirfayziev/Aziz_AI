import os
import base64
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# ====== ENV ======
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL", "").strip()
BACKEND_AUDIO_URL = os.getenv("BACKEND_AUDIO_URL", "").strip()
BACKEND_PLANNER_URL = os.getenv("BACKEND_PLANNER_URL", "").strip()

print("BACKEND_CHAT_URL =", BACKEND_CHAT_URL)
print("BACKEND_AUDIO_URL =", BACKEND_AUDIO_URL)
print("BACKEND_PLANNER_URL =", BACKEND_PLANNER_URL)

if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN o‘rnatilmagan!")
if not BACKEND_CHAT_URL:
    raise ValueError("❌ BACKEND_CHAT_URL o‘rnatilmagan!")


# ====== Planner trigger ======
def is_planner_query(text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    triggers = [
        "bugungi reja",
        "bugungi ishlar",
        "bugun nima qilay",
        "ertangi reja",
        "ertangi ishlar",
        "haftalik reja",
        "oylik reja",
        "plan tuz",
        "reja tuz",
    ]
    return any(x in t for x in triggers)


# ====== /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Aziz AI tayyor!\n"
        "- Matn yozing – chat javob beradi\n"
        "- Ovoz yuboring – ovozdan matn va javob olasiz\n"
        "- “bugungi ishlar”, “ertangi reja” kabi yozsangiz – planner ishlaydi"
    )


# ====== TEXT HANDLER (chat + planner) ======
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text or ""

    # 1) Planner so‘rovi bo‘lsa
    if BACKEND_PLANNER_URL and is_planner_query(text):
        await update.message.reply_text("⏳ Reja tuzilmoqda...")

        payload = {
            "user_id": user_id,
            "query": text,
            "model_tier": "default",
        }

        try:
            r = requests.post(BACKEND_PLANNER_URL, json=payload, timeout=40)
            if r.status_code != 200:
                await update.message.reply_text("⚠️ Planner xatosi.")
                print("Planner error:", r.status_code, r.text)
                return

            data = r.json()
            plan = data.get("result", "⚠️ Reja qaytmadi.")
            await update.message.reply_text(f"🗓 *Siz uchun reja:*\n\n{plan}", parse_mode="Markdown")

        except Exception as e:
            await update.message.reply_text(f"⚠️ Planner API xatosi: {e}")

        return

    # 2) Oddiy chat
    payload = {
        "user_id": user_id,
        "message": text,
    }

    try:
        r = requests.post(BACKEND_CHAT_URL, json=payload, timeout=25)
        if r.status_code != 200:
            await update.message.reply_text("❗ Backend chat javobi xato.")
            print("Chat error:", r.status_code, r.text)
            return

        data = r.json()
        reply = data.get("reply", "")

        if not reply:
            await update.message.reply_text("❗ AI javob qaytarmadi.")
            print("Empty reply:", data)
            return

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("❗ AI javob qaytarmadi.")
        print("Chat exception:", e)


# ====== VOICE HANDLER ======
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not BACKEND_AUDIO_URL:
        await update.message.reply_text("⚠️ Audio uchun BACKEND_AUDIO_URL sozlanmagan.")
        return

    user_id = update.message.from_user.id
    voice = update.message.voice

    try:
        # Telegramdan faylni yuklab olamiz
        file = await context.bot.get_file(voice.file_id)
        file_bytes = await file.download_as_bytearray()

        audio_b64 = base64.b64encode(file_bytes).decode()

        payload = {
            "user_id": user_id,
            "audio_base64": audio_b64,
        }

        r = requests.post(BACKEND_AUDIO_URL, json=payload, timeout=60)
        if r.status_code != 200:
            await update.message.reply_text("⚠️ Audio backend xatosi.")
            print("Audio error:", r.status_code, r.text)
            return

        data = r.json()
        text = data.get("text", "(matn olinmadi)")
        reply = data.get("reply", "(javob olinmadi)")

        await update.message.reply_text(
            f"🎙 *Matn:* {text}\n\n🤖 *Javob:* {reply}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text("⚠️ Audio qayta ishlashda xato.")
        print("Voice exception:", e)


# ====== APP ======
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Aziz AI bot polling boshlandi...")
    app.run_polling()


if __name__ == "__main__":
    main()
