import requests
import json
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "https://azizai-production.up.railway.app")  # backend URL
TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ========================
# 🔹 Helper: matn yuborish
# ========================
def send_text(chat_id, text):
    requests.post(
        f"{TG_API}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

# ========================
# 🔹 Helper: ovoz yuborish
# ========================
def send_voice(chat_id, audio_bytes):
    url = f"{TG_API}/sendVoice"
    files = {"voice": ("reply.ogg", audio_bytes)}
    data = {"chat_id": chat_id}
    requests.post(url, data=data, files=files)

# ========================
# 🔹 Ovoz → matn Convert 
# ========================
def convert_voice_to_text(file_bytes):
    resp = requests.post(
        f"{BACKEND_URL}/api/transcribe",
        files={"file": ("voice.ogg", file_bytes)},
    )
    if resp.ok:
        return resp.json().get("text", "")
    return "(ovozni o‘qishda xato)"

# ========================
# 🔹 ChatGPT javobi olish
# ========================
def get_ai_reply(text, user_id):
    resp = requests.post(
        f"{BACKEND_URL}/api/chat",
        json={"user_id": user_id, "message": text},
        timeout=20
    )
    if resp.ok:
        return resp.json().get("reply", "🤖 Xabarni tushunmadim.")
    return "⚠️ Server bilan bog‘lanishda xato!"

# ========================
# 🔹 Ovozli javob olish
# ========================
def ai_tts(text):
    resp = requests.post(
        f"{BACKEND_URL}/api/tts",
        json={"text": text},
        timeout=20
    )
    if resp.ok:
        return resp.content
    return None

# ========================
# 🔹 ASOSIY HANDLER
# ========================
def handle_update(update):
    if "message" not in update:
        return

    msg = update["message"]
    chat_id = msg["chat"]["id"]
    user_id = str(chat_id)

    # ====================
    # 🔹 /start komandasi
    # ====================
    if "text" in msg and msg["text"].lower().startswith("/start"):
        welcome = (
            "🤖 *Assalomu alaykum, Aziz!*\n\n"
            "Men – **Aziz AI**, sizning shaxsiy sun’iy intellekt yordamchingiz.\n"
            "Siz haqingizda o‘rganaman, odatlaringizni eslab boraman va vaqt o‘tishi bilan yanada aqlli bo‘laman.\n\n"
            "✨ *Menga nimalar buyurishingiz mumkin?*\n"
            "• Savollarga insondek javob berish\n"
            "• Reja, kun tartibi, vazifalar tuzib berish\n"
            "• O‘zingiz haqingizda ma’lumotni eslab qolish\n"
            "• Ovoz orqali suhbatlashish\n\n"
            "Endi men doimo yoningizdaman, Aziz. 😌\n"
            "Xohlagan narsani yozing yoki ovoz yuboring 🎤"
        )
        send_text(chat_id, welcome)
        return

    # ====================
    # 🔹 Agar ovoz yuborsa
    # ====================
    if "voice" in msg:
        file_id = msg["voice"]["file_id"]

        # file path olish
        file_data = requests.get(f"{TG_API}/getFile?file_id={file_id}").json()
        file_path = file_data["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"

        file_bytes = requests.get(file_url).content
        text = convert_voice_to_text(file_bytes)

    # ====================
    # 🔹 Agar matn yuborsa
    # ====================
    elif "text" in msg:
        text = msg["text"]

    else:
        send_text(chat_id, "⚠️ Men faqat matn yoki ovoz qabul qila olaman.")
        return

    # ====================
    # 🔹 AI javobi
    # ====================
    reply = get_ai_reply(text, user_id)

    # Matn yuboramiz
    send_text(chat_id, reply)

    # Ovozni ham qaytaramiz
    audio = ai_tts(reply)
    if audio:
        send_voice(chat_id, audio)
