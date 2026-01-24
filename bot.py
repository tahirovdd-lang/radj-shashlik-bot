import logging
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6013591658
WEBAPP_URL = "https://tahirovdd-lang.github.io/radj-shashlik-bot/"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# /start
@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🍽 Открыть меню", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )
    await message.answer("👋 Добро пожаловать!", reply_markup=kb)

# WebApp data
@dp.message()
async def webapp(message: types.Message):
    if not message.web_app_data:
        return

    logging.info(f"WEBAPP DATA: {message.web_app_data.data}")

    data = json.loads(message.web_app_data.data)
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

    await bot.send_message(ADMIN_ID, admin_text)

    replies = {
        "ru": "✅ Заказ принят! Мы свяжемся с вами.",
        "uz": "✅ Buyurtma qabul qilindi!",
        "en": "✅ Order received!"
    }

    await message.answer(replies.get(lang, replies["ru"]))

if __name__ == "__main__":
    from aiogram import F
    from aiogram.fsm.storage.memory import MemoryStorage
    from aiogram import Router
    from aiogram import Dispatcher
    from aiogram import executor

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(Router())
    executor.start_polling(dp)





