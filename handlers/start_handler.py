from telegram.ext import CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("📥 Автоматическая выгрузка", callback_data="download_previous_day")],
        [InlineKeyboardButton("📤 Загрузить файл вручную", callback_data="upload_manual_file")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 <b>Привет!</b> Я бот для анализа путевых листов.\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

start_handler = CommandHandler("start", start)