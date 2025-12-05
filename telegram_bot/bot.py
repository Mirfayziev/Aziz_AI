import os
import httpx

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")

BOT_API = f"https://api.telegram.org/bot{TOKEN}"


async def send_message(chat_id: int, text: str):
    """Telegramga matn yuborish."""
    payload = {"chat_id": chat_id, "text": text}

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            await client.post(f"{BOT_API}/sendMessage", json=payload)
        except Exception as e:
            print("Telegram send error:", e)


async def process_update(update):
    """Telegram update-ni qayta ishlash."""
    
    # message yo'q bo'lsa chiqib ketamiz
    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

    # /start komandasi
    if user_text.lower() == "/start":
        welcome = (
            "👋 *Salom!* Men — *Aziz AI*, sizning shaxsiy yordamchingiz.\n\n"
            "✨ Savollar, rejalashtirish, maslahat — hammasida yordam beraman.\n"
            "✍️ Istalgan savolni yozavering."
        )
        await send_message(chat_id, welcome)
        return

    # ====== BACKENDGA AI SO‘ROV ======
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                CHAT_URL,
                json={"message": user_text},
            )

        data = response.json()

        # Backendda AI javobi har doim "response" maydonida
        ai_answer = data.get("response") or data.get("reply") or "⚠️ AI javobi qaytmadi!"

    except Exception as e:
        ai_answer = f"⚠️ Xatolik: {e}"

    # ====== TELEGRAMGA AI JAVOBINI YUBORAMIZ ======
    await send_message(chat_id, ai_answer)
