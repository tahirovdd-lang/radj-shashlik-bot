import logging
import json
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "ВАШ_BOT_TOKEN"
ADMIN_ID = 6013591658  # твой Telegram ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        types.KeyboardButton(
            "🍽 Открыть меню",
            web_app=types.WebAppInfo(url="https://tahirovdd-lang.github.io/radj-shashlik-bot/")
        )
    )
    await msg.answer("Добро пожаловать в Radj Shashlik 👋", reply_markup=kb)


# 🔥 ВОТ ОН — КЛЮЧЕВОЙ ХЭНДЛЕР
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def webapp_data(msg: types.Message):
    try:
        data = json.loads(msg.web_app_data.data)
        logging.info(f"📩 WebApp data: {data}")

        order = data.get("order", {})
        total = data.get("total")
        phone = data.get("phone")

        text = "🧾 <b>Новый заказ</b>\n\n"
        for item, count in order.items():
            if count > 0:
                text += f"• {item} × {count}\n"

        text += f"\n💰 Итого: {total} сум"
        text += f"\n📱 Телефон: {phone}"

        # админу
        await bot.send_message(ADMIN_ID, text)

        # клиенту
        await msg.answer("✅ Заказ принят! Мы скоро с вами свяжемся.")

    except Exception as e:
        logging.error(e)
        await msg.answer("❌ Ошибка при оформлении заказа")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)


