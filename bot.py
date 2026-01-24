import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from menu import MENU
from texts import TEXTS

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

user_lang = {}
user_delivery = {}

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🇷🇺 RU", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇺🇿 UZ", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇬🇧 EN", callback_data="lang_en"),
    )
    await msg.answer("Выберите язык / Tilni tanlang / Choose language", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def set_lang(call: types.CallbackQuery):
    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(TEXTS["delivery"][lang], callback_data="delivery"),
        types.InlineKeyboardButton(TEXTS["pickup"][lang], callback_data="pickup"),
    )
    await call.message.edit_text("Тип заказа:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data in ["delivery", "pickup"])
async def order_type(call: types.CallbackQuery):
    lang = user_lang.get(call.from_user.id, "ru")

    if call.data == "delivery":
        await call.message.answer(TEXTS["enter_address"][lang])
        return

    await show_categories(call.message, lang)

@dp.message_handler()
async def save_address(msg: types.Message):
    user_delivery[msg.from_user.id] = msg.text
    lang = user_lang.get(msg.from_user.id, "ru")
    await show_categories(msg, lang)

async def show_categories(msg, lang):
    kb = types.InlineKeyboardMarkup(row_width=2)
    for key, cat in MENU.items():
        kb.add(types.InlineKeyboardButton(cat[lang], callback_data=f"cat_{key}"))
    await msg.answer("🍽 Меню", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("cat_"))
async def show_items(call: types.CallbackQuery):
    lang = user_lang.get(call.from_user.id, "ru")
    cat = MENU[call.data.replace("cat_", "")]
    text = f"{cat[lang]}\n\n"
    for name, price in cat["items"]:
        text += f"• {name} — {price} сум\n"
    await call.message.answer(text)

if __name__ == "__main__":
    executor.start_polling(dp)







