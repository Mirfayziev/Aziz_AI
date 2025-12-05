import os
import requests
import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL", "").strip().rstrip("/")
BACKEND_AUDIO_URL = os.getenv("BACKEND_AUDIO_URL", "").strip().rstrip("/")
BACKEND_PLANNER_URL = os.getenv("BACKEND_PLANNER_URL", "").strip().rstrip("/")

print("BACKEND_CHAT_URL =", BACKEND_CHAT_URL)
print("BACKEND_AUDIO_URL =", BACKEND_AUDIO_URL)
print("BACKEND_PLANNER_URL =", BACKEND_PLANNER_URL)

# ============ TEXT CHAT ============
def handle_text(update, context):
    user_id = update.message.chat_id
    text = update.message.text

    try:
        payload = {"user_id": user_id, "message": text}
        response = requests.post(f"{BACKEND_CHAT_URL}", json=payload, timeout=30)

        if response.status_code == 200:
            reply = response.json().get("reply", "❗️ Javob topilmadi.")
            update.message.reply_text(reply)
        else:
            update.message.reply_text(f"❗️ Backend chat xatosi: {response.status_code}")

    except Exception as e:
        update.message.reply_text(f"❗️ Chat xatosi: {str(e)}")


# ============ VOICE (AUDIO) MODE ============
def handle_voice(update, context):
    user_id = update.message.chat_id

    voice_file = update.message.voice.get_file()
    file_path = voice_file.download()

    files = {"file": open(file_path, "rb")}
    data = {"user_id": user_id}

    try:
        response = requests.post(BACKEND_AUDIO_URL, files=files, data=data, timeout=40)

        if response.status_code == 200:
            reply = response.json().get("reply", "❗️ Audio javob topilmadi.")
            update.message.reply_text(reply)
        else:
            update.message.reply_text("❗️ Audio qayta ishlash xatosi.")

    except Exception as e:
        update.message.reply_text(f"❗️ Audio xatosi: {str(e)}")


# ============ PLANNER ============
def planner(update, context):
    user_id = update.message.chat_id

    try:
        response = requests.post(BACKEND_PLANNER_URL, json={"user_id": user_id}, timeout=20)

        if response.status_code == 200:
            reply = response.json().get("plan", "❗️ Reja topilmadi.")
            update.message.reply_text(reply)
        else:
            update.message.reply_text("❗️ Planner xatosi!")

    except Exception as e:
        update.message.reply_text(str(e))


# ============ START BOT ============
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", planner))
    dp.add_handler(CommandHandler("plan", planner))
    dp.add_handler(MessageHandler(Filters.voice, handle_voice))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
