import os
import httpx
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# =====================================================
# CONFIG
# =====================================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BACKEND_URL = os.getenv("BACKEND_URL", "").rstrip("/")

if not BOT_TOKEN:
    print("⚠️ TELEGRAM_BOT_TOKEN not set")

if not BACKEND_URL:
    print("⚠️ BACKEND_URL not set (AI ulanmaydi, lekin bot ishlaydi)")

app = FastAPI()


# =====================================================
# TELEGRAM API HELPERS
# =====================================================

async def telegram_api(method: str, payload=None, files=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=payload, files=files)
        print(f"➡️ Telegram {method} → {r.status_code}")
        print(r.text)
        return r


async def send_message(chat_id: int, text: str):
    return await telegram_api("sendMessage", {
        "chat_id": chat_id,
        "text": text
    })


# =====================================================
# BACKEND (AI) CALL
# =====================================================

async def ask_backend_ai(text: str) -> str:
    if not BACKEND_URL:
        return "AI backend ulanmagan, lekin bot ishlayapti."

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"{BACKEND_URL}/assistant-message",
                json={"text": text}
            )
            r.raise_for_status()
            data = r.json()
            return data.get("text", "AI javob bermadi")
    except Exception as e:
        print("❌ BACKEND ERROR:", repr(e))
        return "AI vaqtincha javob bermayapti."


# =====================================================
# TELEGRAM WEBHOOK
# =====================================================

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        print("📩 UPDATE:", update)

        message = (
            update.get("message")
            or update.get("edited_message")
        )

        if not message:
            return JSONResponse({"ok": True})

        chat_id = message["chat"]["id"]

        # -------- TEXT MESSAGE --------
        if "text" in message:
            user_text = message["text"]
            await send_message(chat_id, "⏳ O‘ylayapman...")

            ai_answer = await ask_backend_ai(user_text)
            await send_message(chat_id, ai_answer)

        # -------- VOICE MESSAGE (hozircha stub) --------
        elif "voice" in message:
            await send_message(
                chat_id,
                "🎤 Ovoz qabul qilindi. STT keyingi bosqichda ulanadi."
            )

        return JSONResponse({"ok": True})

    except Exception:
        print("❌ WEBHOOK CRASH")
        print(traceback.format_exc())
        return JSONResponse({"ok": True})
