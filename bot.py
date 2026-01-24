import logging
import json
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import MenuButtonWebApp, WebAppInfo

# ================= НАСТРОЙКИ =================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # ОБЯЗАТЕЛЬНО через env
ADMIN_ID = 6013591658
WEBAPP_URL = "https://tahirovdd-lang.github.io/"

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден в переменных окружения")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# ================= УСТАНОВКА КНОПКИ МЕНЮ =================
async def set_menu_button():
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🍽 Меню",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    )
    logging.info("✅ Menu Button успешно установлена")

async def on_startup(dp):
    await set_menu_button()

# ================= /start =================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Нажмите кнопку <b>🍽 Меню</b> внизу экрана, чтобы оформить заказ."
    )

# ================= ПРИЁМ ДАННЫХ ИЗ WEBAPP =================
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def handle_webapp(message: types.Message):
    logging.info(f"📩 RAW WEBAPP DATA: {message.web_app_data.data}")

    try:
        data = json.loads(message.web_app_data.data)
    except Exception as e:
        logging.error(f"❌ JSON ERROR: {e}")
        await message.answer("❌ Ошибка данных заказа")
        return

    order = data.get("order", {})
    phone = data.get("phone", "Не указан")
    lang = data.get("lang", "ru")

    try:
        total = int(data.get("total", 0))
    except:
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

    # ===== СООБЩЕНИЕ АДМИНУ =====
    admin_text = (
        "📥 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 Клиент ID: <code>{message.from_user.id}</code>\n"
        f"📞 Телефон: {phone}\n\n"
        f"{items_text}\n\n"
        f"💰 <b>Итого:</b> {total} сум"
    )

    try:
        await bot.send_message(ADMIN_ID, admin_text)
        logging.info("✅ Заказ отправлен админу")
    except Exception as e:
        logging.error(f"❌ Ошибка отправки админу: {e}")

    # ===== ОТВЕТ КЛИЕНТУ =====
    replies = {
        "ru": "✅ Заказ принят! Мы скоро свяжемся с вами.",
        "uz": "✅ Buyurtmangiz qabul qilindi! Tez orada bog‘lanamiz.",
        "en": "✅ Your order has been received! We will contact you soon."
    }

    await message.answer(replies.get(lang, replies["ru"]))

# ================= ЗАПУСК =================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)




