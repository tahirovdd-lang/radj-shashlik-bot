import os
import json
import logging
import requests
import asyncio
import uuid  # 🔴 ДОБАВЛЕНО

from aiogram import Bot, Dispatcher, executor, types
from aiohttp import web

# === НАСТРОЙКИ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6013591658

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxSG6M86JhMZr34RI1ajn3xZhEJDXsbX44tiXGiW-YtXLGY9X2T59HBpHs2CrRuuy49/exec"

CLICK_TEST_URL = "https://my.click.uz/services/pay"  # 🔴 TEST CLICK

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


# === /start ===
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


# === ПРИЁМ ЗАКАЗА ИЗ WEB APP ===
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def get_order(message: types.Message):
    data = json.loads(message.web_app_data.data)

    order = data.get("order", {})
    phone = data.get("phone", "—")
    comment = data.get("comment", "—")
    total = data.get("total", "0")
    lang = data.get("lang", "ru")
    delivery = data.get("delivery", "—")
    address = data.get("address", "—")
    payment = data.get("payment", "cash")

    order_id = str(uuid.uuid4())[:8]  # 🔴 ORDER ID

    payment_text = {
        "cash": "💵 Наличные",
        "click": "💳 CLICK"
    }.get(payment)

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
        f"📞 Телефон: {phone}\n"
        f"💳 Оплата: <b>{payment_text}</b>\n\n"
        f"{items_text}\n\n"
        f"💰 <b>{total} сум</b>"
    )

    await bot.send_message(ADMIN_ID, admin_message)

    # === GOOGLE SHEETS ===
    requests.post(
        GOOGLE_SCRIPT_URL,
        json={
            "order_id": order_id,
            "user_id": user.id,
            "username": username,
            "phone": phone,
            "payment": payment_text,
            "items": items_text,
            "total": total
        },
        timeout=10
    )

    # === CLICK PAYMENT LINK ===
    if payment == "click":
        click_link = (
            f"{CLICK_TEST_URL}"
            f"?service_id=TEST"
            f"&merchant_trans_id={order_id}"
            f"&amount={total}"
        )

        pay_keyboard = types.InlineKeyboardMarkup()
        pay_keyboard.add(
            types.InlineKeyboardButton(
                text="💳 Оплатить через CLICK",
                url=click_link
            )
        )

        await message.answer(
            "🧾 Заказ создан.\nНажмите кнопку ниже для оплаты:",
            reply_markup=pay_keyboard
        )
    else:
        await message.answer(
            "✅ Заказ принят! Оплата наличными при получении."
        )


# =====================================================
# 🔴 CALLBACK CLICKtest
# =====================================================

async def click_callback(request):
    data = await request.json()

    order_id = data.get("order_id")
    status = data.get("status")
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
    return web.json_response({"ok": True})


# === WEB SERVER ===
async def start_web():
    app = web.Application()
    app.router.add_post("/click/callback", click_callback)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()


async def main():
    await start_web()
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())














