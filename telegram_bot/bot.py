import os
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Agar xohlasangiz BACKEND_URL ni ham env'dan oling:
BACKEND_URL = os.getenv("BACKEND_URL", "https://azizai-production.up.railway.app/aziz-ai")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom Aziz 👋\nAziz AI online.\n\nSavolingni yoz."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = (update.message.text or "").strip()
    user_id = str(update.effective_user.id) if update.effective_user else "unknown"

    if not user_text:
        await update.message.reply_text("Matn topilmadi. Qaytadan yozing.")
        return

    try:
        r = requests.post(
            BACKEND_URL,
            json={
                "user_external_id": user_id,
                "message": user_text,
                "model_tier": "default",
            },
            timeout=30,
        )

        if r.status_code != 200:
            # Backend xatosini qisqa ko'rsatamiz
            body_preview = (r.text or "")[:500]
            answer = f"⚠️ Backend xato ({r.status_code}).\n{body_preview}"
        else:
            data = r.json() if r.content else {}
            answer = data.get("reply") or data.get("text") or "Javob yo‘q"

    except requests.exceptions.Timeout:
        answer = "⚠️ Backend juda sekin javob berdi (timeout)."
    except Exception as e:
        answer = f"⚠️ Backend bilan aloqa yo‘q: {e}"

    await update.message.reply_text(answer)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN env yo'q. Railway Variables ga qo'shing.")

    webhook_base = os.getenv("WEBHOOK_URL")
    if not webhook_base:
        raise RuntimeError("WEBHOOK_URL env yo'q. Masalan: https://<your-service>.up.railway.app")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Webhook faqat POST bilan keladi. Brauzer GET qilsa 405/404 bo'lishi normal.
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        url_path="/telegram/webhook",
        webhook_url=f"{webhook_base}/telegram/webhook",
    )


if __name__ == "__main__":
    main()
