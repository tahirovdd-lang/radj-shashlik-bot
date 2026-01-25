import os
import json
import logging
import requests
import uuid
from aiogram import Bot, Dispatcher, executor, types
from aiohttp import web

# === НАСТРОЙКИ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6013591658

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxSG6M86JhMZr34RI1ajn3xZhEJDXsbX44tiXGiW-YtXLGY9X2T59HBpHs2CrRuuy49/exec"

CLICK_TEST_URL = "https://my.click.uz/services/pay"  # CLICKtest
CLICK_SERVICE_ID = "99999"  # тестовый service_id
CLICK_MERCHANT_ID = "99999"  # тестовый merchant_id
CALLBACK_URL = "https://YOUR_DOMAIN/click/callback"  # ❗ поменяешь на боевой

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# =====================================================
# /start
# =====================================================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
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

# =====================================================
# ПРИЁМ ЗАКАЗА ИЗ WEB APP
# =====================================================
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def get_order(message: types.Message):
    data = json.loads(message.web_app_data.data)

    order = data.get("order", {})
    phone = data.get("phone", "—")
    comment = data.get("comment", "—")
    total = int(data.get("total", 0))
    lang = data.get("lang", "ru")
    delivery = data.get("delivery", "—")
    address = data.get("address", "—")
    payment = data.get("payment", "cash")

    order_id = str(uuid.uuid4())[:8]  # 🔹 ШАГ 4

    payment_text = {
        "cash": "💵 Наличные",
        "click": "💳 CLICK"
    }.get(payment, "—")

    user = message.from_user
    username = f"@{user.username}" if user.username else "—"

    items_text = "\n".join(
        f"• {name} × {qty}"
        for name, qty in order.items()
        if qty > 0
    ) or "—"

    admin_message = (
        "📥 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"🆔 Заказ: <code>{order_id}</code>\n"
        f"👤 ID: <code>{user.id}</code>\n"
        f"👤 Ник: {username}\n"
        f"📞 Телефон: {phone}\n"
        f"🚚 Тип: {delivery}\n"
        f"📍 Адрес: {address}\n"
        f"💳 Оплата: <b>{payment_text}</b>\n"
        f"{items_text}\n\n"
        f"💰 <b>{total} сум</b>"
    )

    await bot.send_message(ADMIN_ID, admin_message)

    # Google Sheets
    requests.post(
        GOOGLE_SCRIPT_URL,
        json={
            "order_id": order_id,
            "user_id": user.id,
            "phone": phone,
            "payment": payment_text,
            "items": items_text,
            "total": total
        }
    )

    # =====================================================
    # 🔹 ШАГ 5 — КНОПКА ОПЛАТЫ CLICK
    # =====================================================
    if payment == "click":
        click_url = (
            f"{CLICK_TEST_URL}?"
            f"service_id={CLICK_SERVICE_ID}&"
            f"merchant_id={CLICK_MERCHANT_ID}&"
            f"amount={total}&"
            f"transaction_param={order_id}&"
            f"return_url=https://t.me/RadjShashlikbot"
        )

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text="💳 Оплатить через CLICK",
                url=click_url
            )
        )

        await message.answer(
            "🕒 Заказ принят!\nНажмите кнопку ниже для оплаты через CLICK 👇",
            reply_markup=keyboard
        )
    else:
        await message.answer("✅ Заказ принят! Оплата наличными при получении.")

# =====================================================
# 🔹 ШАГ 6–7 — CALLBACK ОТ CLICKtest
# =====================================================
async def click_callback(request):
    data = await request.post()

    order_id = data.get("transaction_param")
    status = data.get("status", "failed")
    amount = data.get("amount")

    if status == "success":
        text = (
            "✅ <b>CLICK ОПЛАТА УСПЕШНА</b>\n"
            f"🆔 Заказ: {order_id}\n"
            f"💰 {amount} сум"
        )
    else:
        text = (
            "❌ <b>CLICK ОПЛАТА НЕ ПРОШЛА</b>\n"
            f"🆔 Заказ: {order_id}"
        )

    await bot.send_message(ADMIN_ID, text)
    return web.Response(text="OK")

# =====================================================
# WEB SERVER
# =====================================================
async def on_startup(dp):
    app = web.Application()
    app.router.add_post("/click/callback", click_callback)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    logging.info("✅ CLICK callback server started on port 8080")

# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup
    )
















