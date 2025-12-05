import logging
import asyncio

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN
from handlers import cmd_start, handle_text, handle_voice, handle_planner


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


async def main():
    log.info("Starting Aziz AI Pro Telegram bot (polling)...")

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    # komandalar
    app.add_handler(CommandHandler("start", cmd_start))

    # planner trigger (so'zlar bo'yicha)
    app.add_handler(
        MessageHandler(
            filters.TEXT
            & (
                filters.Regex("(?i)bugungi ishlar")
                | filters.Regex("(?i)ertangi reja")
                | filters.Regex("(?i)haftalik reja")
                | filters.Regex("(?i)/plan")
            ),
            handle_planner,
        )
    )

    # umumiy text handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # voice
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    await app.initialize()
    await app.start()
    log.info("Bot polling started...")
    await app.updater.start_polling()
    await app.updater.idle()


if __name__ == "__main__":
    asyncio.run(main())
