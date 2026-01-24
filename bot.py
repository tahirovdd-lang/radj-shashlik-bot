from aiogram import Bot, Dispatcher, executor, types
import json

API_TOKEN = "TOKEN"
ADMIN_ID = 123456789

bot = Bot(API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def webapp(msg: types.Message):
    data = json.loads(msg.web_app_data.data)

    text = "🛒 НОВЫЙ ЗАКАЗ\n\n"
    text += f"Тип: {data['type']}\n"
    text += f"Адрес: {data['address']}\n\n"

    for k,v in data["items"].items():
        if v > 0:
            text += f"{k} × {v}\n"

    await bot.send_message(ADMIN_ID, text)
    await msg.answer("✅ Ваш заказ принят!")

if __name__ == "__main__":
    executor.start_polling(dp)








