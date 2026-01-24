import os
import json
import logging
from aiogram import Bot, Dispatcher, executor, types

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6013591658

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            "🍽 Открыть меню",
            web_app=types.WebAppInfo(
                url="https://tahirovdd-lang.github.io/radj-shashlik-bot/"
            )
        )
    )
    await message.answer(
        "👋 Добро пожаловать!\nНажмите кнопку ниже, чтобы сделать заказ.",
        reply_markup=kb
    )


@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def get_order(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
    except Exception as e:
        await bot.send_message(ADMIN_ID, f"❌ Ошибка данных: {e}")
        return

    order = data.get("order", {})
    total = data.get("total", "0")
    lang = data.get("lang", "ru")
    delivery = data.get("delivery", "—")
    address = data.get("address", "—")

    items = "\n".join(
        f"• {name} × {qty}"
        for name, qty in order.items()
    )

    admin_text = (
        "📥 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 ID: <code>{message.from_user.id}</code>\n"
        f"🚚 Тип: {delivery}\n"
        f"📍 Адрес: {address}\n\n"
        f"{items}\n\n"
        f"💰 <b>{total} сум</b>"
    )

    # 🔔 админу
    await bot.send_message(ADMIN_ID, admin_text)

    # ✅ клиенту
    replies = {
        "ru": "✅ Заказ принят! Мы скоро свяжемся с вами.",
        "uz": "✅ Buyurtma qabul qilindi!",
        "en": "✅ Order received! We will contact you."
    }

    await message.answer(replies.get(lang, replies["ru"]))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)









