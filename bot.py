import logging
import json
from aiogram import Bot, Dispatcher, executor, types

# 🔑 ВСТАВЬ ТОКЕН ОТ BOTFATHER
BOT_TOKEN = "8525626062:AAGqnee7mzlP9OjrEOYYirzArf2MYgIK95Q"

# 👤 ТВОЙ TELEGRAM ID
ADMIN_ID = 6013591658

# 🌐 GITHUB PAGES URL
WEBAPP_URL = "https://tahirovdd-lang.github.io/radj-shashlik-bot/"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            text="🍽 Открыть меню",
            web_app=types.WebAppInfo(url=WEBAPP_URL)
        )
    )
    await message.answer(
        "👋 Добро пожаловать!\nНажмите кнопку ниже, чтобы сделать заказ 👇",
        reply_markup=kb
    )

@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def webapp_handler(message: types.Message):
    data = json.loads(message.web_app_data.data)

    order = data.get("order", {})
    phone = data.get("phone", "—")
    total = data.get("total", 0)
    lang = data.get("lang", "ru")

    items = "\n".join(
        [f"• {name} × {count}" for name, count in order.items() if count > 0]
    )

    text = (
        "📥 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 ID: <code>{message.from_user.id}</code>\n"
        f"📞 Телефон: {phone}\n\n"
        f"{items}\n\n"
        f"💰 <b>{total} сум</b>"
    )

    await bot.send_message(ADMIN_ID, text)

    replies = {
        "ru": "✅ Заказ принят! Мы скоро свяжемся с вами.",
        "uz": "✅ Buyurtma qabul qilindi!",
        "en": "✅ Order received!"
    }

    await message.answer(replies.get(lang, replies["ru"]))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)





