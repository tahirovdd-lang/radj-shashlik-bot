import os
import json
import logging
import requests
import asyncio
from aiogram import Bot, Dispatcher, executor, types

from aiohttp import web  # 🔴 ДОБАВЛЕНО

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
    payment = data.get("payment", "cash")

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
        f"👤 ID: <code>{user.id}</code>\n"
        f"👤 Ник: {username}\n"
        f"📞 Телефон: {phone}\n"
        f"🚚 Тип: {delivery}\n"
        f"📍 Адрес: {address}\n"
        f"💳 Оплата: <b>{payment_text}</b>\n"
        f"💬 Комментарий: {comment}\n\n"
        f"{items_text}\n\n"
        f"💰 <b>{total} сум</b>"
    )

    await bot.send_message(ADMIN_ID, admin_message)

    requests.post(
        GOOGLE_SCRIPT_URL,
        json={
            "user_id": user.id,
            "username": username,
            "phone": phone,
            "delivery": delivery,
            "address": address,
            "payment": payment_text,
            "comment": comment,
            "items": items_text,
            "total": total
        },
        timeout=10
    )

    replies = {
        "ru": {
            "cash": "✅ Заказ принят! Оплата наличными при получении.",
            "click": "🕒 Заказ принят! Ожидаем оплату через CLICK."
        }
    }

    await message.answer(replies["ru"].get(payment))


# =====================================================
# 🔴 ШАГ 5 — CALLBACK ОТ CLICKtest
# =====================================================

async def click_callback(request):
    data = await request.json()

    order_id = data.get("order_id")
    status = data.get("status")
    amount = data.get("amount")

    if status == "success":
        text = (
            "✅ <b>CLICK ОПЛАТА УСПЕШНА</b>\n\n"
            f"🆔 Заказ: {order_id}\n"
            f"💰 Сумма: {amount} сум"
        )
    else:
        text = (
            "❌ <b>CLICK ОПЛАТА НЕ ПРОШЛА</b>\n\n"
            f"🆔 Заказ: {order_id}"
        )

    await bot.send_message(ADMIN_ID, text)

    return web.json_response({"ok": True})


# === ЗАПУСК WEB СЕРВЕРА ===
async def start_web():
    app = web.Application()
    app.router.add_post("/click/callback", click_callback)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()


# === СТАРТ ВСЕГО ===
async def main():
    await start_web()
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())














