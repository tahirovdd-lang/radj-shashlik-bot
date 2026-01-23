from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "8525626062:AAGqnee7mzlP9OjrEOYYirzArf2MYgIK95Q"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("🚀 Бот работает! Python 3.10.10 + aiogram 2.25.1")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
