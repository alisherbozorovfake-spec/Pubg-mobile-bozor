from aiogram import Bot, Dispatcher, types, executor
from config import *
from db import *
from keyboards import *

bot = Bot(8359391710:AAE7BVmEIjwcbNdtCnilsFNc1qVveP4-r98)
dp = Dispatcher(bot)

prices_sell = {
    "60": 7000,
    "120": 14000,
    "240": 28000,
    "325": 38000,
    "660": 77000
}

prices_buy = {
    "60": 10000,
    "120": 20000,
    "240": 40000,
    "325": 52000,
    "660": 110000
}

# START
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (msg.from_user.id,))
    await msg.answer("Menu:", reply_markup=main_menu())

# =========================
# 📤 UC SOTISH (MARKETPLACE)
# =========================
@dp.message_handler(lambda m: m.text == "📤 Sotish")
async def sell(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for k in prices_sell:
        kb.add(f"{k} UC")
    await msg.answer("UC tanlang:", reply_markup=kb)

@dp.message_handler(lambda m: "UC" in m.text)
async def select_uc(msg: types.Message):
    uc = msg.text.split()[0]
    await msg.answer("Promo kodni yuboring:")

    @dp.message_handler()
    async def promo_handler(m: types.Message):
        cursor.execute("INSERT INTO promos (user_id, uc_amount, promo, status) VALUES (?,?,?,?)",
                       (m.from_user.id, uc, m.text, "pending"))
        db.commit()

        await bot.send_message(CHANNEL_ID,
            f"🆕 Promo\nUC: {uc}\nKod: {m.text}"
        )

        await bot.send_message(ADMIN_ID,
            f"Tasdiqlash:\nID:{m.from_user.id}\n{uc} UC\n{m.text}\n/accept_{m.message_id}"
        )

        await m.answer("Adminga yuborildi!")
        dp.message_handlers.unregister(promo_handler)

# =========================
# 📥 SOTIB OLISH
# =========================
@dp.message_handler(lambda m: m.text == "📥 Sotib olish")
async def buy(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for k in prices_buy:
        kb.add(f"{k} UC")
    await msg.answer("Tanlang:", reply_markup=kb)

@dp.message_handler(lambda m: "UC" in m.text)
async def buy_uc(msg: types.Message):
    uc = msg.text.split()[0]
    price = prices_buy[uc]

    if get_balance(msg.from_user.id) < price:
        await msg.answer("❌ Mablag‘ yetarli emas")
        return

    await msg.answer("ID yuboring:")

    @dp.message_handler()
    async def id_handler(m: types.Message):
        minus_balance(m.from_user.id, price)

        await bot.send_message(ADMIN_ID,
            f"Sotib olish:\nUser:{m.from_user.id}\nUC:{uc}\nID:{m.text}"
        )

        await m.answer("Adminga yuborildi")
        dp.message_handlers.unregister(id_handler)

# =========================
# 💰 HISOB
# =========================
@dp.message_handler(lambda m: m.text == "💰 Hisob")
async def account(msg: types.Message):
    bal = get_balance(msg.from_user.id)
    await msg.answer(f"Balans: {bal} so'm\nKarta: {CARD_NUMBER}")

# =========================
# ➕ AUTO BALANS (ADMIN)
# =========================
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def payment(msg: types.Message):
    await bot.send_photo(ADMIN_ID, msg.photo[-1].file_id,
        caption=f"To‘lov:\nUser:{msg.from_user.id}"
    )
    await msg.answer("Kutilmoqda...")

@dp.message_handler(lambda m: m.text.startswith("/add"))
async def add_money(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    _, user_id, amount = msg.text.split()
    add_balance(int(user_id), int(amount))

    await bot.send_message(user_id, f"✅ Balans to‘ldirildi: {amount}")

# =========================
# ➖ YECHISH
# =========================
@dp.message_handler(lambda m: "yechish" in m.text.lower())
async def withdraw(msg: types.Message):
    await msg.answer("Karta yuboring:")

    @dp.message_handler()
    async def w_handler(m: types.Message):
        await bot.send_message(ADMIN_ID,
            f"Yechish:\nUser:{m.from_user.id}\nKarta:{m.text}"
        )
        await m.answer("Yuborildi")
        dp.message_handlers.unregister(w_handler)

# =========================
# 🆘 YORDAM
# =========================
@dp.message_handler(lambda m: m.text == "🆘 Yordam")
async def help(msg: types.Message):
    await msg.answer("Yozing:")

    @dp.message_handler()
    async def help_send(m: types.Message):
        await bot.send_message(ADMIN_ID,
            f"Yordam:\n{m.from_user.id}\n{m.text}"
        )
        await m.answer("Yuborildi")
        dp.message_handlers.unregister(help_send)

# RUN
executor.start_polling(dp)
