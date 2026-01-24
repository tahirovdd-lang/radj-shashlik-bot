import logging
import json
import os
from aiogram import Bot, Dispatcher, executor, types

# ================= НАСТРОЙКИ =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6013591658
WEBAPP_URL = "https://tahirovdd-lang.github.io/radj-shashlik-bot/"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# ================= /start =================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        types.KeyboardButton(
            "🍽 Открыть меню",
            web_app=types.WebAppInfo(url=WEBAPP_URL)
        )
    )

    await message.answer(
        "👋 Добро пожаловать!\nНажмите кнопку ниже 👇",
        reply_markup=kb
    )

# ================= ПРИЁМ ДАННЫХ ИЗ WEBAPP =================
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def webapp(message: types.Message):
    try:
        logging.info(f"WEBAPP DATA: {message.web_app_data.data}")

        data = json.loads(message.web_app_data.data)

        order = data.get("order", {})
        phone = data.get("phone", "—")
        lang = data.get("lang", "ru")
        total = int(data.get("total", 0))
        delivery = data.get("delivery", "—")

        items = "\n".join(
            [f"• {name} × {count}" for name, count in order.items() if count > 0]
        )

        admin_text = (
            "📥 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
            f"👤 ID: <code>{message.from_user.id}</code>\n"
            f"📞 Телефон: {phone}\n"
            f"🚚 Способ: {delivery}\n\n"
            f"{items}\n\n"
            f"💰 <b>{total} сум</b>"
        )

        await bot.send_message(ADMIN_ID, admin_text)

        replies = {
            "ru": "✅ Заказ принят! Мы свяжемся с вами.",
            "uz": "✅ Buyurtma qabul qilindi! Tez orada bog‘lanamiz.",
            "en": "✅ Order received! We will contact you."
        }

        await message.answer(replies.get(lang, replies["ru"]))

    except Exception as e:
        logging.exception("Ошибка обработки заказа")
        await message.answer("❌ Ошибка при оформлении заказа. Попробуйте ещё раз.")

# ================= ЗАПУСК =================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)







