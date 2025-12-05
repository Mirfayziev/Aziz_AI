import io
import logging
from datetime import datetime

import requests
from telegram import Update
from telegram.ext import ContextTypes

from .config import BACKEND_CHAT_URL, BACKEND_AUDIO_URL, BACKEND_PLANNER_URL

log = logging.getLogger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name if user else "do'stim"
    text = (
        f"Salom, {name}! Men Aziz AI Pro 🤖\n\n"
        "Men sen bilan o'zbek, rus yoki ingliz tilida gaplasha olaman.\n"
        "Yoz: oddiy savollar, reja tuzish, maslahatlar.\n"
        "Ovoz yuborsang ham tushunaman.\n\n"
        "Bugun bilateralammi? 🙂"
    )
    await update.message.reply_text(text)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    user_id = str(update.effective_user.id)

    payload = {
        "user_id": user_id,
        "message": text,
        "model_tier": "default",
    }

    try:
        r = requests.post(BACKEND_CHAT_URL, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        reply = data.get("reply", "(javob olinmadi)")
    except Exception as e:
        log.exception("Chat backend xatosi: %s", e)
        reply = "❗️ Chat backend bilan bog'lanishda xato yuz berdi."

    await update.message.reply_text(reply)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.voice:
        return

    user_id = str(update.effective_user.id)

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    bio = io.BytesIO()
    await file.download_to_memory(out=bio)
    bio.seek(0)

    files = {
        "file": ("audio.ogg", bio, "audio/ogg"),
    }
    data = {
        "user_id": user_id,
    }

    try:
        r = requests.post(BACKEND_AUDIO_URL, data=data, files=files, timeout=120)
        r.raise_for_status()
        res = r.json()
        text = res.get("text", "(matn olinmadi)")
        reply = res.get("reply", "(javob olinmadi)")
        msg = f"🎙 Matn: {text}\n\n🤖 Javob: {reply}"
    except Exception as e:
        log.exception("Audio backend xatosi: %s", e)
        msg = "❗️ Audio backend bilan bog'lanishda xato yuz berdi."

    await update.message.reply_text(msg)


async def handle_planner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /plan komandasi yoki 'bugungi ishlar', 'ertangi reja' ga reja yaratish. """
    if not update.message:
        return

    text = update.message.text or ""
    user_id = str(update.effective_user.id)

    lowered = text.lower()
    if "ertangi" in lowered:
        mode = "tomorrow"
    elif "hafta" in lowered:
        mode = "week"
    else:
        mode = "today"

    payload = {
        "user_id": user_id,
        "text": text,
        "mode": mode,
    }

    try:
        r = requests.post(BACKEND_PLANNER_URL, json=payload, timeout=90)
        r.raise_for_status()
        data = r.json()
        plan = data.get("plan_text", "")
    except Exception as e:
        log.exception("Planner backend xatosi: %s", e)
        plan = "❗️ Reja tuzishda xato yuz berdi."

    header = "🗓 Siz uchun reja tayyor:\n\n"
    await update.message.reply_text(header + plan)
