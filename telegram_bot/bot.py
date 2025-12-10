import os
import asyncio
import aiohttp

# ✅ Environment dan olinadi
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")   # ✅ /api/chat/chat bo‘lishi shart
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")  # ixtiyoriy, bo‘lmasayam ishlaydi


# ✅ Telegramga xabar yuborish
async def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    async with aiohttp.ClientSession() as session:
        await session.post(url, json=payload)


# ✅ Bitta update (xabar)ni qayta ishlash
async def process_update(update: dict):
    try:
        message = update.get("message") or update.get("edited_message")
        if not message:
            return

        chat_id = message["chat"]["id"]

        # ✅ /start
        if "text" in message and message["text"] == "/start":
            await send_message(chat_id, "✅ Aziz AI ishga tushdi!")
            return

        # ✅ Matnli xabar
        if "text" in message:
            user_text = message["text"]

            # ✅ BACKENDGA TO‘G‘RI YUBORISH (QUERY orqali)
            params = {
                "message": user_text,
                "external_id": str(chat_id)
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    CHAT_URL,
                    params=params   # ✅ JSON EMAS, QUERY PARAMS
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data.get("reply") or data.get("response") or "❌ AI javob bermadi"
                    else:
                        reply = f"⚠️ Backend xatosi: {resp.status}"

            await send_message(chat_id, reply)
            return

        # ✅ OVOZ (agar audio URL bo‘lsa)
        if "voice" in message and AUDIO_URL:
            file_id = message["voice"]["file_id"]
            await send_message(chat_id, "🎤 Ovoz qabul qilindi, ishlanmoqda...")

            params = {"file_id": file_id}

            async with aiohttp.ClientSession() as session:
                async with session.post(AUDIO_URL, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data.get("text", "❌ Ovozdan matn olinmadi")
                    else:
                        reply = f"⚠️ Audio backend xatosi: {resp.status}"

            await send_message(chat_id, reply)

    except Exception as e:
        print("process_update xatosi:", str(e))


# ✅ ✅ ✅ ASOSIY LONG POLLING QISMI
async def polling():
    offset = 0
    print("✅ Telegram bot polling boshlandi...")

    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {
                "timeout": 30,
                "offset": offset
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()

            if "result" in data:
                for update in data["result"]:
                    offset = update["update_id"] + 1
                    await process_update(update)

        except Exception as e:
            print("Polling xatosi:", str(e))

        await asyncio.sleep(1)


# ✅ START
if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN yo‘q")
    if not CHAT_URL:
        raise ValueError("❌ AZIZ_BACKEND_CHAT_URL yo‘q")

    asyncio.run(polling())
