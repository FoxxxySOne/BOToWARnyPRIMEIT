from telegram.ext import MessageHandler, filters
from utils.data_loader import load_excel_data
from utils.error_handler import handle_error

async def upload_file(update, context):
    try:
        file = await update.message.document.get_file()
        file_path = f"data/{file.file_name}"
        await file.download_to_drive(file_path)

        # Загрузка данных
        result = load_excel_data(file_path)
        await update.message.reply_text(result)
    except Exception as e:
        await handle_error(update, e)

upload_handler = MessageHandler(filters.Document.ALL, upload_file)