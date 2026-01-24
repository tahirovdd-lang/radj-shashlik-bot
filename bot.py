import os
import json
import logging
from aiogram import Bot, Dispatcher, executor, types

# === НАСТРОЙКИ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6013591658  # твой Telegram ID
WEBAPP_URL = "https://tahirovdd-lang.github.io/radj-shashlik-bot/"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


# === /start ===
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "🍽 Открыть меню",
            web_app=types.WebAppInfo(url=WEBAPP_URL)
        )
    )
    await message.answer(
        "👋 Добро пожаловать!\nНажмите кнопку ниже, чтобы сделать заказ.",
        reply_markup=keyboard
    )


# === ПРИЁМ ЗАКАЗА ИЗ ПРИЛОЖЕНИЯ ===
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def get_order(message: types.Message):
    data = json.loads(message.web_app_data.data)

    order = data.get("order", {})
    phone = data.get("phone", "—")
    total = data.get("total", "0")
    lang = data.get("lang", "ru")
    delivery = data.get("delivery", "—")
    address = data.get("address", "—")

    items_text = "\n".join(
        f"• {name} × {qty}"
        for name, qty in order.items()
        if qty > 0
    )

    admin_message = (
        "📥 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 ID: <code>{message.from_user.id}</code>\n"
        f"📞 Телефон: {phone}\n"
        f"🚚 Тип: {delivery}\n"
        f"📍 Адрес: {address}\n\n"
        f"{items_text}\n\n"
        f"💰 <b>{total} сум</b>"
    )

    # 👉 ОТПРАВКА АДМИНУ
    await bot.send_message(ADMIN_ID, admin_message)

    # 👉 ОТВЕТ КЛИЕНТУ
    replies = {
        "ru": "✅ Заказ принят! Мы скоро свяжемся с вами.",
        "uz": "✅ Buyurtma qabul qilindi!",
        "en": "✅ Order received! We will contact you."
    }

    await message.answer(replies.get(lang, replies["ru"]))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)









