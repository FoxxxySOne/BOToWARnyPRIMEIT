from telegram.ext import CallbackQueryHandler
from utils.data_loader import analyze_data
from utils.error_handler import handle_error

async def analyze_callback(update, context):
    try:
        query = update.callback_query
        if query.data == "analyze_all":
            result = analyze_data()
            await query.message.reply_text(result)
        else:
            await query.message.reply_text("❌ Неизвестный запрос.")
    except Exception as e:
        await handle_error(update, e)

analysis_handler = CallbackQueryHandler(analyze_callback)
