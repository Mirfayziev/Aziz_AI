import os
import uuid
import time
import requests
from typing import Dict, Any, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# =========================
# ENV / SETTINGS
# =========================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Aziz AI backend endpoint (AI javobni shu yerdan olamiz)
BACKEND_URL = os.getenv("BACKEND_URL", "https://azizai-production.up.railway.app/aziz-ai")

# Sizning Telegram ID (admin) — DRAFT faqat sizga keladi
# Example: ADMIN_TELEGRAM_ID=123456789
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")

# Tasdiqlashni kutish vaqti (sekund)
# Masalan 300 = 5 daqiqa
APPROVAL_TIMEOUT_SEC = int(os.getenv("APPROVAL_TIMEOUT_SEC", "300"))

# Tasdiqlanmasa userga yuboriladigan avtomatik xabar
BUSY_MESSAGE = os.getenv("BUSY_MESSAGE", "Aziz hozir band, keyin javob beradi.")

# =========================
# In-memory drafts storage
# (prod uchun keyin DB qilamiz, hozir barqaror MVP)
# =========================
DRAFTS: Dict[str, Dict[str, Any]] = {}
# draft structure:
# {
#   "draft_id": str,
#   "created_at": float,
#   "status": "pending"|"approved"|"rejected"|"expired",
#   "from_chat_id": int,
#   "from_user_id": int,
#   "from_username": str,
#   "from_fullname": str,
#   "original_text": str,
#   "draft_reply": str,
#   "admin_message_id": Optional[int],
#   "timeout_job_name": str,
# }

# =========================
# Helpers
# =========================
def _require_admin() -> int:
    if not ADMIN_TELEGRAM_ID:
        raise RuntimeError("ADMIN_TELEGRAM_ID env yo'q. Railway Variables ga ADMIN_TELEGRAM_ID qo'shing.")
    try:
        return int(ADMIN_TELEGRAM_ID)
    except ValueError as e:
        raise RuntimeError("ADMIN_TELEGRAM_ID raqam bo'lishi kerak (Telegram user id).") from e


def _build_admin_draft_text(d: Dict[str, Any]) -> str:
    user_line = d["from_fullname"]
    if d.get("from_username"):
        user_line += f" (@{d['from_username']})"

    return (
        "📝 *Draft javob tayyor*\n\n"
        f"👤 *Kimdan:* {user_line}\n"
        f"🆔 *Chat ID:* `{d['from_chat_id']}`\n\n"
        f"📩 *Xabar:* {d['original_text']}\n\n"
        f"🤖 *Draft:* {d['draft_reply']}\n\n"
        "Tasdiqlaysizmi?"
    )


async def _ask_ai_for_draft(user_text: str, user_external_id: str) -> str:
    """
    Backend'dan AI draft javobini oladi.
    """
    r = requests.post(
        BACKEND_URL,
        json={
            "user_external_id": user_external_id,
            "message": user_text,
            "model_tier": "default",
        },
        timeout=45,
    )

    if r.status_code != 200:
        body_preview = (r.text or "")[:500]
        return f"⚠️ Backend xato ({r.status_code}). {body_preview}"

    data = r.json() if r.content else {}
    # Backend odatda {"reply": "..."} qaytaradi
    return data.get("reply") or data.get("text") or "Javob yo‘q"


async def _expire_if_pending(context: ContextTypes.DEFAULT_TYPE):
    """
    Timeout bo'lganda draft pending bo'lsa, userga BUSY_MESSAGE yuboradi.
    """
    job = context.job
    draft_id = job.data.get("draft_id")
    if not draft_id or draft_id not in DRAFTS:
        return

    d = DRAFTS[draft_id]
    if d["status"] != "pending":
        return

    d["status"] = "expired"

    # userga band xabari
    try:
        await context.bot.send_message(
            chat_id=d["from_chat_id"],
            text=BUSY_MESSAGE
        )
    except Exception:
        # user bloklagan bo'lishi mumkin; jim o'tamiz
        pass

    # admin draft xabarini yangilash (ixtiyoriy)
    try:
        if d.get("admin_message_id"):
            await context.bot.send_message(
                chat_id=_require_admin(),
                text=f"⏳ Draft muddati tugadi (tasdiqlanmadi). Userga band xabari yuborildi.\nDraft ID: {draft_id}"
            )
    except Exception:
        pass


def _draft_keyboard(draft_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yuborish", callback_data=f"approve:{draft_id}"),
            InlineKeyboardButton("❌ Bekor", callback_data=f"reject:{draft_id}"),
        ]
    ])


# =========================
# Handlers
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom Aziz 👋\nAziz AI online.\n\nSavolingni yoz."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Draft rejim:
    - Agar admin yozsa: oddiy AI javob beradi (siz uchun ChatGPT o'rnida).
    - Agar boshqa odam yozsa: draft qilinadi va adminga tasdiqlashga yuboriladi.
    """
    admin_id = _require_admin()

    msg = update.message
    if not msg or not msg.text:
        return

    user_text = msg.text.strip()
    if not user_text:
        return

    from_user = update.effective_user
    from_chat = update.effective_chat

    if not from_user or not from_chat:
        return

    # Admin o'zi yozsa — direct chat (approvalsiz)
    if from_user.id == admin_id:
        # Siz o'zingiz bot bilan gaplashayotgan bo'lsangiz
        answer = await _ask_ai_for_draft(user_text=user_text, user_external_id=str(from_user.id))
        await msg.reply_text(answer)
        return

    # Boshqa odam yozsa — draft yaratamiz
    draft_id = uuid.uuid4().hex[:10]
    draft_reply = await _ask_ai_for_draft(user_text=user_text, user_external_id=str(from_user.id))

    d = {
        "draft_id": draft_id,
        "created_at": time.time(),
        "status": "pending",
        "from_chat_id": from_chat.id,
        "from_user_id": from_user.id,
        "from_username": from_user.username or "",
        "from_fullname": (from_user.full_name or "").strip() or "Unknown",
        "original_text": user_text,
        "draft_reply": draft_reply,
        "admin_message_id": None,
        "timeout_job_name": f"draft_timeout_{draft_id}",
    }
    DRAFTS[draft_id] = d

    # Adminga draft yuboramiz
    admin_text = _build_admin_draft_text(d)
    sent = await context.bot.send_message(
        chat_id=admin_id,
        text=admin_text,
        parse_mode="Markdown",
        reply_markup=_draft_keyboard(draft_id),
    )
    d["admin_message_id"] = sent.message_id

    # Timeout job schedule: agar tasdiqlanmasa userga BUSY_MESSAGE yuboriladi
    context.job_queue.run_once(
        _expire_if_pending,
        when=APPROVAL_TIMEOUT_SEC,
        name=d["timeout_job_name"],
        data={"draft_id": draft_id},
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ✅ approve / ❌ reject tugmalari.
    """
    query = update.callback_query
    if not query or not query.data:
        return

    admin_id = _require_admin()
    if update.effective_user and update.effective_user.id != admin_id:
        await query.answer("Bu tugmalar faqat Aziz uchun.")
        return

    action, _, draft_id = query.data.partition(":")
    if draft_id not in DRAFTS:
        await query.answer("Draft topilmadi yoki eskirgan.")
        return

    d = DRAFTS[draft_id]
    if d["status"] != "pending":
        await query.answer(f"Draft allaqachon: {d['status']}")
        return

    # timeout jobni o'chiramiz (agar bo'lsa)
    for job in context.job_queue.get_jobs_by_name(d["timeout_job_name"]):
        job.schedule_removal()

    if action == "approve":
        d["status"] = "approved"
        # userga draft javob yuboramiz
        try:
            await context.bot.send_message(
                chat_id=d["from_chat_id"],
                text=d["draft_reply"]
            )
        except Exception:
            # user bloklagan bo'lishi mumkin
            pass

        await query.answer("Yuborildi ✅")

        # admin xabarini yangilash
        try:
            await query.edit_message_reply_markup(reply_markup=None)
            await query.edit_message_text(
                text=_build_admin_draft_text(d) + "\n\n✅ *Yuborildi*",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    elif action == "reject":
        d["status"] = "rejected"
        # userga band xabar yuboramiz
        try:
            await context.bot.send_message(
                chat_id=d["from_chat_id"],
                text=BUSY_MESSAGE
            )
        except Exception:
            pass

        await query.answer("Bekor qilindi ❌")

        # admin xabarini yangilash
        try:
            await query.edit_message_reply_markup(reply_markup=None)
            await query.edit_message_text(
                text=_build_admin_draft_text(d) + "\n\n❌ *Bekor qilindi*",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    else:
        await query.answer("Noma'lum amal.")


# =========================
# Webhook runner
# =========================
def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN env yo'q. Railway Variables ga qo'shing.")

    _require_admin()  # validate admin id

    webhook_base = os.getenv("WEBHOOK_URL")
    if not webhook_base:
        raise RuntimeError("WEBHOOK_URL env yo'q. Masalan: https://<your-service>.up.railway.app")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        url_path="/telegram/webhook",
        webhook_url=f"{webhook_base}/telegram/webhook",
    )


if __name__ == "__main__":
    main()
