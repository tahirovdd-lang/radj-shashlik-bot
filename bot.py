import logging
import json
from aiogram import Bot, Dispatcher, executor, types

# 🔑 ВСТАВЬ ТОКЕН НАПРЯМУЮ
BOT_TOKEN = "8525626062:AAGqnee7mzlP9OjrEOYYirzArf2MYgIK95Q"

ADMIN_ID = 6013591658
WEBAPP_URL = "https://tahirovdd-lang.github.io/radj-shashlik-bot/"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            "🍽 Открыть меню",
            web_app=types.WebAppInfo(url=WEBAPP_URL)
        )
    )
    await message.answer("👋 Добро пожаловать!", reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def webapp(message: types.Message):
    try:
        logging.info(f"WEBAPP DATA: {message.web_app_data.data}")
        data = json.loads(message.web_app_data.data)
    except Exception as e:
        logging.error(e)
        await message.answer("❌ Ошибка обработки заказа")
        return

    order = data.get("order", {})
    phone = data.get("phone", "—")
    lang = data.get("lang", "ru")

    try:
        total = int(data.get("total", 0))
    except:
        total = 0

    items = "\n".join(
        [f"• {k} × {v}" for k, v in order.items() if v > 0]
    )

    admin_text = (
        "📥 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 ID: <code>{message.from_user.id}</code>\n"
        f"📞 Телефон: {phone}\n\n"
        f"{items}\n\n"
        f"💰 <b>{total} сум</b>"
    )

    await bot.send_message(ADMIN_ID, admin_text)

    replies = {
        "ru": "✅ Заказ принят! Мы свяжемся с вами.",
        "uz": "✅ Buyurtma qabul qilindi!",
        "en": "✅ Order received!"
    }

    await message.answer(replies.get(lang, replies["ru"]))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)






