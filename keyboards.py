from aiogram import types

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📤 Sotish", "📥 Sotib olish")
    kb.add("💰 Hisob", "🆘 Yordam")
    return kb

def admin_panel():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📊 Statistika", "💳 Balans qo‘shish")
    return kb
