import logging
import json
import os
from aiogram import Bot, Dispatcher, executor, types

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6013591658

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в <b>Radj Shashlik</b>\n\n"
        "Нажмите кнопку <b>🍽 Меню</b> внизу Telegram 👇\n"
        "и оформите заказ прямо в приложении."
    )


@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def webapp_handler(message: types.Message):
    logging.info(f"📩 WEB_APP_DATA: {message.web_app_data.data}")

    try:
        data = json.loads(message.web_app_data.data)
    except Exception as e:
        logging.error(e)
        return

    order = data.get("order", {})
    phone = data.get("phone", "—")
    lang = data.get("lang", "ru")
    total = int(data.get("total", 0))

    items = [f"• {k} × {v}" for k, v in order.items() if v > 0]

    if not items:
        await message.answer("❌ Корзина пуста")
        return

    text = (
        "📥 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 ID: <code>{message.from_user.id}</code>\n"
        f"📞 Телефон: {phone}\n\n"
        + "\n".join(items) +
        f"\n\n💰 <b>Итого:</b> {total} сум"
    )

    await bot.send_message(ADMIN_ID, text)

    replies = {
        "ru": "✅ Заказ принят! Мы скоро свяжемся с вами.",
        "uz": "✅ Buyurtmangiz qabul qilindi!",
        "en": "✅ Your order has been received!"
    }

    await message.answer(replies.get(lang, replies["ru"]))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)



