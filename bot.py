import os
from telegram.ext import ApplicationBuilder
from handlers.start_handler import start_handler
from handlers.upload_handler import upload_handler
from handlers.analysis_handler import analysis_handler

def main():
    # Инициализация бота
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    # Добавляем обработчики
    app.add_handler(start_handler)
    app.add_handler(upload_handler)
    app.add_handler(analysis_handler)
    
    # Запуск бота
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()