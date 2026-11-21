import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client, Client

# Получаем ключи из настроек Railway
TOKEN = os.environ.get("8765841092:AAFchpaGUdMeQYS2je3HZQ6vajQaItd13Co")
APP_URL = os.environ.get("APP_URL", "https://google.com")
SUPABASE_URL = os.environ.get("https://iundgnfebsmcohzmmqln.supabase.co")
SUPABASE_KEY = os.environ.get("sb_secret_spp9t34mxF4FlffonJ2ZbA_vfY0dplh")

# Проверка на всякий случай
if not TOKEN or not SUPABASE_URL or not SUPABASE_KEY:
    print("ОШИБКА: Не заданы переменные окружения (BOT_TOKEN, SUPABASE_URL, SUPABASE_KEY)")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветствие, кнопку запуска игры и сохраняет игрока в БД."""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    username = update.message.from_user.username or "Игрок"

    # --- 1. РАБОТА С БАЗОЙ ДАННЫХ ---
    try:
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
        print(f"❌ Ошибка базы данных: {e}")
        await update.message.reply_text(f"⚠️ Ошибка базы: {e}")

    # --- 2. СОЗДАНИЕ И ОТПРАВКА КНОПКИ ---
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

    await update.message.reply_text(
        f"Привет, {user_name}!\nТвой профиль готов. Нажимай кнопку ниже, чтобы начать!",
        reply_markup=reply_markup
    )

def main():
    """Запуск бота."""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
