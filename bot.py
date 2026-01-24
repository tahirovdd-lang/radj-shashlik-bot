import logging
import json
import os
from aiogram import Bot, Dispatcher, executor, types

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6013591658

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    # Просто открываем WebApp как ссылку, MainButton не нужен
    kb.add(types.InlineKeyboardButton(
        "🍽 Открыть меню",
        url="https://tahirovdd-lang.github.io/radj-shashlik-bot/"
    ))
    await message.answer("👋 Добро пожаловать!", reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def webapp(message: types.Message):
    logging.info(f"WEBAPP DATA: {message.web_app_data.data}")

    data = json.loads(message.web_app_data.data)

    order = data.get("order", {})
    phone = data.get("phone", "—")
    lang = data.get("lang", "ru")
    delivery = data.get("delivery", "—")
    total = int(data.get("total", 0))

    items = "\n".join([f"• {k} × {v}" for k, v in order.items() if v > 0])

    admin_text = (
        "📥 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 ID: <code>{message.from_user.id}</code>\n"
        f"📞 Телефон: {phone}\n"
        f"🚚 Доставка/Самовывоз: {delivery}\n\n"
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






