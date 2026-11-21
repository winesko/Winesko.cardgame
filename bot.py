import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client, Client

# ==========================================
# НАСТРОЙКИ (ВСТАВЬТЕ СВОИ ДАННЫЕ)
# ==========================================
# 1. Токен вашего бота (получите у @BotFather)
TOKEN = "8765841092:AAFchpaGUdMeQYS2je3HZQ6vajQaItd13Co"

# 2. Ссылка на игру (пока оставьте пустой, вставим позже, когда выложим на Vercel)
# Пример: "https://my-game.vercel.app"
APP_URL = "https://google.com" 

# 3. Ключи от Supabase (URL и СЕКРЕТНЫЙ ключ Secret key)
SUPABASE_URL = "https://iundgnfebsmcohzmmqln.supabase.co"
SUPABASE_KEY = "sb_secret_spp9t34mxF4FlffonJ2ZbA_vfY0dplh"
# ==========================================

# Подключаемся к базе данных
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветствие, кнопку запуска игры и сохраняет игрока в БД."""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    username = update.message.from_user.username or "Игрок"

    # --- 1. РАБОТА С БАЗОЙ ДАННЫХ ---
    try:
    # Проверяем, есть ли игрок в базе
    response = supabase.table("profiles").select("telegram_id").eq("telegram_id", user_id).execute()
    
    if not response.data:
        supabase.table("profiles").insert({
            "telegram_id": user_id,
            "username": username
        }).execute()
        
        supabase.table("game_saves").insert({
            "telegram_id": user_id,
            "save_data": {} 
        }).execute()
        
        print(f"✅ Новый игрок {username} создан в базе!")
    else:
        print(f"ℹ️ Игрок {username} уже есть в базе.")
        
except Exception as e:
    # Вот здесь важны отступы! Эти две строки должны быть строго под except
    print(f"❌ Ошибка базы данных: {e}")
    await update.message.reply_text(f"⚠️ Ошибка базы: {e}")

    # --- 2. СОЗДАНИЕ И ОТПРАВКА КНОПКИ ---
    # Добавляем user_id в ссылку, чтобы игра знала, кто именно играет
    game_url_with_id = f"{APP_URL}?user_id={user_id}"
    
    keyboard = [
        [
            InlineKeyboardButton(
                "🎮 Играть в карточную игру!",
                web_app={"url": game_url_with_id}
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с кнопкой
    await update.message.reply_text(
        f"Привет, {user_name}!\nТвой профиль готов. Нажимай кнопку ниже, чтобы начать!",
        reply_markup=reply_markup
    )

def main():
    """Запуск бота."""
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
