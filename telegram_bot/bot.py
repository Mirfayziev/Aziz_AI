import os
import asyncio
import aiohttp

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # ✅ TELEGRAM_TOKEN emas, shu bo‘lishi shart
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")


async def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    async with aiohttp.ClientSession() as session:
        await session.post(url, json=payload)


async def process_update(update: dict):
    try:
        message = update.get("message") or update.get("edited_message")
        if not message:
            return

        chat_id = message["chat"]["id"]

        if "text" in message:
            user_text = message["text"]

            # /start uchun oddiy javob
            if user_text == "/start":
                await send_message(chat_id, "✅ Aziz AI ishga tushdi!")
                return

            # Backend chat API ga yuboramiz
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    CHAT_URL,
                    json={"message": user_text}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data.get("reply") or data.get("response", "❌ AI javob bera olmadi")
                    else:
                        reply = f"⚠️ Backend xatosi: {resp.status}"

            await send_message(chat_id, reply)

        if "voice" in message and AUDIO_URL:
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


# ✅ ✅ ✅ LONG POLLING QISMI — ASOSIY YETISHMAYOTGAN JOY SHU EDI
async def polling():
    offset = 0
    print("✅ Telegram bot polling boshlandi...")

    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"timeout": 30, "offset": offset}

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


if __name__ == "__main__":
    asyncio.run(polling())
