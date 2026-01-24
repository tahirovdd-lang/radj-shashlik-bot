import logging
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6013591658

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

WEBAPP_URL = "https://tahirovdd-lang.github.io/radj-shashlik-bot/"

# Команда /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        "🍽 Открыть меню",
        url=WEBAPP_URL  # В aiogram 2.x используем url, WebAppInfo только в v3
    ))
    await message.answer("👋 Добро пожаловать!", reply_markup=keyboard)

# Получение данных с WebApp
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_webapp(message: types.Message):
    try:
        data = json.loads(message.text)
    except:
        await message.answer("⚠️ Ошибка данных")
        return

    order = data.get("order", {})
    phone = data.get("phone", "—")
    lang = data.get("lang", "ru")
    total = int(data.get("total", 0))

    items = "\n".join([f"• {k} × {v}" for k, v in order.items() if v > 0])

    admin_text = (
        "📥 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 ID: <code>{message.from_user.id}</code>\n"
        f"📞 Телефон: {phone}\n\n"
        f"{items}\n\n"
        f"💰 <b>{total} сум</b>"
    )

    # Отправка админу
    await bot.send_message(ADMIN_ID, admin_text)

    replies = {
        "ru": "✅ Заказ принят! Мы свяжемся с вами.",
        "uz": "✅ Buyurtma qabul qilindi!",
        "en": "✅ Order received!"
    }

    await message.answer(replies.get(lang, replies["ru"]))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)





