import os
import json
import logging
import requests
from aiogram import Bot, Dispatcher, executor, types

# === НАСТРОЙКИ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6013591658

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxSG6M86JhMZr34RI1ajn3xZhEJDXsbX44tiXGiW-YtXLGY9X2T59HBpHs2CrRuuy49/exec"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


# === /start ===
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )
    keyboard.add(
        types.KeyboardButton(
            text="🍽 Открыть меню",
            web_app=types.WebAppInfo(
                url="https://tahirovdd-lang.github.io/radj-shashlik-bot/"
            )
        )
    )

    await message.answer(
        "👋 Добро пожаловать!\nНажмите кнопку ниже, чтобы сделать заказ.",
        reply_markup=keyboard
    )


# === ПРИЁМ ЗАКАЗА ИЗ WEB APP ===
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def get_order(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
    except Exception as e:
        logging.error(f"JSON error: {e}")
        return

    order = data.get("order", {})
    phone = data.get("phone", "—")
    comment = data.get("comment", "—")
    total = data.get("total", "0")
    lang = data.get("lang", "ru")
    delivery = data.get("delivery", "—")
    address = data.get("address", "—")

    user = message.from_user
    username = f"@{user.username}" if user.username else "—"

    items_text = "\n".join(
        f"• {name} × {qty}"
        for name, qty in order.items()
        if qty > 0
    ) or "—"

    admin_message = (
        "📥 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 ID: <code>{user.id}</code>\n"
        f"👤 Ник: {username}\n"
        f"📞 Телефон: {phone}\n"
        f"🚚 Тип: {delivery}\n"
        f"📍 Адрес: {address}\n"
        f"💬 Комментарий: {comment}\n\n"
        f"{items_text}\n\n"
        f"💰 <b>{total} сум</b>"
    )

    # 👉 Админу (обязательно)
    try:
        await bot.send_message(ADMIN_ID, admin_message)
    except Exception as e:
        logging.error(f"Admin send error: {e}")

    # 👉 Google Sheets (вторично)
    try:
        requests.post(
            GOOGLE_SCRIPT_URL,
            json={
                "user_id": user.id,
                "username": username,
                "phone": phone,
                "delivery": delivery,
                "address": address,
                "comment": comment,
                "items": items_text,
                "total": total
            },
            timeout=10
        )
    except Exception as e:
        logging.error(f"Google Sheets error: {e}")

    replies = {
        "ru": "✅ Заказ принят! Мы скоро свяжемся с вами.",
        "uz": "✅ Buyurtma qabul qilindi! Tez orada bog‘lanamiz.",
        "en": "✅ Order received! We will contact you shortly."
    }

    await message.answer(replies.get(lang, replies["ru"]))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)










