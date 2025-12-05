from aiogram import Bot, Dispatcher, executor, types
from handlers import handle_text
from config import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# TEXT handler
@dp.message_handler(content_types=['text'])
async def text_handler(message: types.Message):
    await handle_text(message)

if __name__ == "__main__":
    print("🤖 Telegram polling bot started...")
    executor.start_polling(dp, skip_updates=True)
