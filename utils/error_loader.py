from telegram import Update

async def handle_error(update, error):
    print(f"Ошибка: {error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ Произошла ошибка.")