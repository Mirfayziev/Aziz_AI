import os
from typing import Dict

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

from app.services.assistant_service import (
    brain_query,
    get_daily_summary,
    get_weekly_summary,
    generate_tomorrow_plan,
)
from app.db import get_db

# ======================================================
# CONFIG
# ======================================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_PATH = "/aziz-ai"

app = FastAPI()

tg_app: Application = ApplicationBuilder().token(BOT_TOKEN).build()


# ======================================================
# TELEGRAM HANDLERS
# ======================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom Aziz 👋\n"
        "Men Aziz AI.\n\n"
        "/summary — kunlik xulosa\n"
        "/week — haftalik xulosa\n"
        "/plan — ertangi reja\n"
        "Oddiy yozsangiz — javob beraman."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer, _ = await brain_query(text)
    await update.message.reply_text(answer)


async def daily_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    summary = await get_daily_summary()
    await update.message.reply_text(summary)


async def weekly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    summary = await get_weekly_summary()
    await update.message.reply_text(summary)


async def tomorrow_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    external_id = str(update.effective_user.id)

    # DB session
    db = next(get_db())
    try:
        result = await generate_tomorrow_plan(db, external_id)
    finally:
        db.close()

    await update.message.reply_text(
        f"📅 {result['date']}\n"
        f"🎯 Fokus: {', '.join(result['focus'])}\n"
        f"📝 Tasks yaratildi: {result['tasks_created']}"
    )


# ======================================================
# REGISTER HANDLERS
# ======================================================

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("summary", daily_summary))
tg_app.add_handler(CommandHandler("week", weekly_summary))
tg_app.add_handler(CommandHandler("plan", tomorrow_plan))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))


# ======================================================
# WEBHOOK ENDPOINT
# ======================================================

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data: Dict = await request.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)
    return {"ok": True}
