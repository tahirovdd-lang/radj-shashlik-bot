import logging
import json
import os
from aiogram import Bot, Dispatcher, executor, types

# ================= НАСТРОЙКИ =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6013591658
WEBAPP_URL = "https://tahirovdd-lang.github.io/radj-shashlik-bot/"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в переменных окружения")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# ================= /start =================
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
        "👋 Добро пожаловать!\n\n"
        "Нажмите кнопку ниже, чтобы оформить заказ 👇",
        reply_markup=kb
    )

# ================= ПРИЁМ ДАННЫХ ИЗ WEBAPP =================
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def handle_webapp_data(message: types.Message):
    logging.info(f"📩 WebApp data: {message.web_app_data.data}")

    try:
        data = json.loads(message.web_app_data.data)
    except Exception as e:
        logging.error(f"JSON error: {e}")
        await message.answer("❌ Ошибка данных заказа")
        return

    order = data.get("order", {})
    phone = data.get("phone", "Не указан")
    lang = data.get("lang", "ru")

    try:
        total = int(data.get("total", 0))
    except ValueError:
        total = 0

    items = [
        f"• {name} × {qty}"
        for name, qty in order.items()
        if isinstance(qty, int) and qty > 0
    ]

    if not items or total <= 0:
        await message.answer("❌ Корзина пуста")
        return

    items_text = "\n".join(items)

    # ===== АДМИН =====
    admin_text = (
        "📥 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 Клиент ID: <code>{message.from_user.id}</code>\n"
        f"📞 Телефон: {phone}\n\n"
        f"{items_text}\n\n"
        f"💰 <b>Итого:</b> {total} сум"
    )

    await bot.send_message(ADMIN_ID, admin_text)

    # ===== КЛИЕНТ =====
    replies = {
        "ru": "✅ Заказ принят! Мы скоро свяжемся с вами.",
        "uz": "✅ Buyurtmangiz qabul qilindi! Tez orada bog‘lanamiz.",
        "en": "✅ Your order has been received! We will contact you soon."
    }

    await message.answer(replies.get(lang, replies["ru"]))

# ================= ЗАПУСК =================
if __name__ == "__main__":
    executor.start_polling(dp)  # ❗ БЕЗ skip_updates

