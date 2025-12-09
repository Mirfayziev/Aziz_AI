import os
import aiohttp

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")

async def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    async with aiohttp.ClientSession() as session:
        await session.post(url, json=payload)

async def process_update(update: dict):
    """Bu funksiya server.py ichidan webhook kelganda chaqiriladi"""
    try:
        message = update.get("message") or update.get("edited_message")
        if not message:
            return

        chat_id = message["chat"]["id"]

        # Foydalanuvchi matn yuborganda
        if "text" in message:
            user_text = message["text"]

            # Backend chat API ga yuborish
            async with aiohttp.ClientSession() as session:
                async with session.post(CHAT_URL, json={"message": user_text}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data.get("response", "❌ AI javob bera olmadi")
                    else:
                        reply = f"⚠️ Backend xatosi: {resp.status}"

            await send_message(chat_id, reply)

        # Agar ovoz yuborsa
        if "voice" in message:
            file_id = message["voice"]["file_id"]
            await send_message(chat_id, "🎤 Ovoz qabul qilindi, ishlanmoqda...")

            async with aiohttp.ClientSession() as session:
                async with session.post(AUDIO_URL, json={"file_id": file_id}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data.get("text", "❌ Ovozdan matn olinmadi")
                    else:
                        reply = f"⚠️ Audio backend xatosi: {resp.status}"

            await send_message(chat_id, reply)

    except Exception as e:
        print("process_update xatosi:", str(e))
