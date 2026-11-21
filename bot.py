import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client, Client

TOKEN = os.environ.get("8765841092:AAFchpaGUdMeQYS2je3HZQ6vajQaItd13Co")
APP_URL = os.environ.get("APP_URL", "https://google.com")
SUPABASE_URL = os.environ.get("https://iundgnfebsmcohzmmqln.supabase.co")
SUPABASE_KEY = os.environ.get("sb_secret_spp9t34mxF4FlffonJ2ZbA_vfY0dplh")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    username = update.message.from_user.username or "Игрок"

    # Сохраняем в базу БЕЗ блока try (если будет ошибка, мы увидим её в логах)
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

    # Кнопка
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
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
