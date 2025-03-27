import os
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Глобальные переменные
DATA = None  # DataFrame с данными из Excel
PARKING_MAPPING = None  # DataFrame с данными о парковках
CARRIER_MAPPING = None  # DataFrame с данными о перевозчиках

# Укажите реальный токен вашего бота
TELEGRAM_BOT_TOKEN = "7485656740:AAFZKdSJ44I-2c72wcsu0Cc1nainIgGA9I8"  # Замените на ваш реальный токен

# Проверка токена
if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
    raise ValueError("TELEGRAM_BOT_TOKEN не настроен. Пожалуйста, укажите реальный токен.")

# Путь к папке для скачанных файлов
DOWNLOAD_FOLDER = r"C:\Users\Administrator\Desktop\BOToWARnyPRIMEIT\BOTANAL(auto)\data"

# Размер страницы для навигации
PAGE_SIZE = 5

# Функция для поиска последнего скачанного файла
def get_latest_downloaded_file(download_folder):
    """
    Находит последний скачанный файл в указанной папке.
    """
    files = [f for f in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, f))]
    if not files:
        raise FileNotFoundError("В папке нет скачанных файлов.")
    # Исключаем частично загруженные файлы (например, .crdownload)
    files = [f for f in files if not f.endswith(".crdownload")]
    # Находим файл с самым последним временем изменения
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(download_folder, f)))
    return os.path.join(download_folder, latest_file)

# Загрузка данных из Excel
def load_excel_data(file_path):
    try:
        if not file_path.endswith(('.xlsx', '.xls')):
            return "Ошибка: файл не является Excel-файлом. Пожалуйста, скачайте правильный файл."
        global DATA
        DATA = pd.read_excel(file_path)
        print(f"Загруженные данные:\n{DATA.head()}")
        # Проверяем наличие необходимых столбцов
        required_columns = [
            'Лог. маршрут', '№', 'ФИО Водителя', 'Дата открытия',
            'Сумма путевого листа', 'Сумма штрафов', 'Кол-во шк.',
            'Возвраты: всего/доставлено', 'Коробки : всего / доставлено'
        ]
        missing_columns = [col for col in required_columns if col not in DATA.columns]
        if missing_columns:
            return f"❌ В файле отсутствуют следующие столбцы: {', '.join(missing_columns)}."
        # Разделение значений в столбце "Возвраты: всего/доставлено"
        split_returns = DATA['Возвраты: всего/доставлено'].str.split('/', expand=True)
        DATA['Всего_возвратов'] = pd.to_numeric(split_returns[0], errors='coerce')
        DATA['Доставлено_возвратов'] = pd.to_numeric(split_returns[1], errors='coerce')
        DATA['Процент доставки возвратов'] = (DATA['Доставлено_возвратов'] / DATA['Всего_возвратов']) * 100
        # Разделение значений в столбце "Коробки : всего / доставлено"
        split_boxes = DATA['Коробки : всего / доставлено'].str.split('/', expand=True)
        DATA['Всего_коробок'] = pd.to_numeric(split_boxes[0], errors='coerce')
        DATA['Доставлено_коробок'] = pd.to_numeric(split_boxes[1], errors='coerce')
        DATA['Процент доставки коробок'] = (DATA['Доставлено_коробок'] / DATA['Всего_коробок']) * 100
        return "✅ Данные успешно загружены!"
    except Exception as e:
        return f"❌ Ошибка при загрузке данных: {e}"

# Загрузка данных о парковках (CSV)
def load_parking_mapping(file_path):
    try:
        global PARKING_MAPPING
        PARKING_MAPPING = pd.read_csv(file_path)
        return "✅ Данные о парковках успешно загружены!"
    except Exception as e:
        return f"❌ Ошибка при загрузке данных о парковках: {e}"

# Анализ данных и формирование сообщения
def analyze_data():
    if DATA is None:
        return "❌ Данные не загружены. Сначала скачайте файл."
    total_sum = DATA['Сумма путевого листа'].sum()
    total_fines = DATA['Сумма штрафов'].sum()
    avg_items = DATA['Кол-во шк.'].mean()
    total_routes = len(DATA)
    routes_without_returns = len(DATA[
        (DATA['Возвраты: всего/доставлено'] == '0/0') |  
        (DATA['Процент доставки возвратов'] == 0) |      
        (DATA['Возвраты: всего/доставлено'].isnull())    
    ])
    total_returns = DATA['Всего_возвратов'].sum()
    delivered_returns = DATA['Доставлено_возвратов'].sum()
    delivery_rate_returns = (delivered_returns / total_returns) * 100 if total_returns > 0 else 0
    delivery_rate_boxes = DATA['Процент доставки коробок'].mean() if 'Процент доставки коробок' in DATA.columns else None
    avg_route_sum = DATA['Сумма путевого листа'].mean()
    net_profit = total_sum - total_fines
    message = (
        "📊 <b>Общий анализ путевых листов:</b>\n"
        "------------------------------------\n"
        "💰 <b>Сумма путевых:</b> {:.2f}\n"
        "⚠️ <b>Сумма штрафов:</b> {:.2f}\n"
        "📦 <b>Среднее кол-во ШК:</b> {:.2f}\n"
        "🚗 <b>Кол-во путевых:</b> {}\n"
        "🔄 <b>Кол-во путевых без возвратов:</b> {}\n"
        "\n"
        "🚚 <b>Возвраты:</b>\n"
        "   • Всего: {}\n"
        "   • Доставлено: {}\n"
        "   • Процент доставки: {:.2f}%\n"
        "\n"
        "📦 <b>Коробки:</b>\n"
        "   • Процент доставки: {:.2f}%\n"
        "\n"
        "📈 <b>Средняя сумма путевого листа:</b> {:.2f}\n"
        "💵 <b>Чистая прибыль (Общая сумма - Штрафы):</b> {:.2f}\n"
    ).format(
        total_sum, total_fines, avg_items, total_routes, routes_without_returns,
        total_returns, delivered_returns, delivery_rate_returns,
        delivery_rate_boxes, avg_route_sum, net_profit
    )
    return message

# Кнопка "Все путевые листы"
async def show_all_routes(update: Update, context: ContextTypes.DEFAULT_TYPE, page=0):
    if DATA is None:
        await update.callback_query.message.reply_text("❌ Данные не загружены. Сначала скачайте файл.")
        return
    total_routes = len(DATA)
    total_pages = (total_routes // PAGE_SIZE) + (1 if total_routes % PAGE_SIZE != 0 else 0)
    if page < 0 or page >= total_pages:
        page = 0
    start_index = page * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    paginated_data = DATA.iloc[start_index:end_index]
    keyboard = []
    for _, row in paginated_data.iterrows():
        route_info = (
            f"🚗 Парковка {row['Лог. маршрут'][:5]}, "
            f"№{row['№']}, "
            f"{row['ФИО Водителя']}, "
            f"📅 {row['Дата открытия']}"
        )
        callback_data = f"route_{row['№']}"
        keyboard.append([InlineKeyboardButton(route_info, callback_data=callback_data)])
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"all_routes_page_{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("➡️ Вперёд", callback_data=f"all_routes_page_{page + 1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("📋 <b>Список путевых листов:</b>", reply_markup=reply_markup, parse_mode="HTML")

# Обработка выбора путевого листа
async def handle_route_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    route_number = query.data.split('_')[1]
    route_data = DATA[DATA['№'] == int(route_number)]
    if route_data.empty:
        await query.message.reply_text("❌ Путевой лист не найден.")
        return
    row = route_data.iloc[0]
    matching_parking = PARKING_MAPPING[PARKING_MAPPING['route_id'] == row['Лог. маршрут'][:5]]
    parking_number = matching_parking['parking_number'].values[0] if not matching_parking.empty else "Неизвестная парковка"
    message = (
        "📋 <b>Информация о путевом листе №{}</b>\n"
        "------------------------------------\n"
        "🚗 <b>Парковка:</b> {}\n"
        "👨‍✈️ <b>Водитель:</b> {}\n"
        "📅 <b>Дата открытия:</b> {}\n"
        "\n"
        "💰 <b>Сумма путевого листа:</b> {:.2f}\n"
        "⚠️ <b>Сумма штрафов:</b> {:.2f}\n"
        "📦 <b>Кол-во ШК:</b> {}\n"
        "\n"
        "🔄 <b>Возвраты:</b> {}\n"
        "📦 <b>Коробки:</b> {}\n"
    ).format(
        row['№'], parking_number, row['ФИО Водителя'], row['Дата открытия'],
        row['Сумма путевого листа'], row['Сумма штрафов'], row['Кол-во шк.'],
        row['Возвраты: всего/доставлено'], row['Коробки : всего / доставлено']
    )
    await query.message.reply_text(message, parse_mode="HTML")

# Кнопка "Список водителей"
async def show_drivers_list(update: Update, context: ContextTypes.DEFAULT_TYPE, page=0):
    if DATA is None:
        await update.callback_query.message.reply_text("❌ Данные не загружены. Сначала скачайте файл.")
        return
    try:
        # Получаем уникальных водителей
        drivers = DATA['ФИО Водителя'].unique()
        total_drivers = len(drivers)
        total_pages = (total_drivers // PAGE_SIZE) + (1 if total_drivers % PAGE_SIZE != 0 else 0)

        # Проверяем корректность номера страницы
        if page < 0 or page >= total_pages:
            page = 0

        # Разбиваем водителей на страницы
        start_index = page * PAGE_SIZE
        end_index = start_index + PAGE_SIZE
        paginated_drivers = drivers[start_index:end_index]

        # Создаем кнопки для текущей страницы
        keyboard = [[InlineKeyboardButton(driver, callback_data=f"driver_{driver}")] for driver in paginated_drivers]

        # Добавляем кнопки навигации
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"drivers_page_{page - 1}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("➡️ Вперёд", callback_data=f"drivers_page_{page + 1}"))
        if nav_buttons:
            keyboard.append(nav_buttons)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(
            f"👥 <b>Список водителей (Страница {page + 1}/{total_pages}):</b>",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Ошибка при формировании списка водителей: {e}")
        await update.callback_query.message.reply_text("❌ Произошла ошибка при формировании списка водителей.")

# Обработка выбора водителя
async def handle_driver_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    driver_name = query.data.split('_')[1]
    driver_data = DATA[DATA['ФИО Водителя'] == driver_name]
    if driver_data.empty:
        await query.message.reply_text("❌ Водитель не найден.")
        return
    message = f"👨‍✈️ <b>Путевые листы водителя {driver_name}:</b>\n"
    for _, row in driver_data.iterrows():
        message += (
            "-\n"
            "📋 <b>Путевой лист №{}</b>\n"
            "🚗 Парковка: {}\n"
            "📅 Дата открытия: {}\n"
            "💰 Сумма путевого листа: {:.2f}\n"
            "⚠️ Сумма штрафов: {:.2f}\n"
            "📦 Кол-во ШК: {}\n"
            "🔄 Возвраты: {}\n"
            "📦 Коробки: {}\n"
        ).format(
            row['№'], row['Лог. маршрут'][:5], row['Дата открытия'],
            row['Сумма путевого листа'], row['Сумма штрафов'], row['Кол-во шк.'],
            row['Возвраты: всего/доставлено'], row['Коробки : всего / доставлено']
        )
    await query.message.reply_text(message, parse_mode="HTML")

# Выбор парковки
async def choose_parking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PARKING_MAPPING is None or DATA is None:
        await update.callback_query.message.reply_text("❌ Данные о парковках или основные данные не загружены.")
        return
    try:
        # Получаем уникальные значения первых 5 символов из столбца "Лог. маршрут"
        unique_routes = DATA['Лог. маршрут'].str[:5].unique()
        unique_routes = pd.Series(unique_routes).astype(str).str.strip()
        PARKING_MAPPING['route_id'] = PARKING_MAPPING['route_id'].astype(str).str.strip()
        filtered_parking = PARKING_MAPPING[PARKING_MAPPING['route_id'].isin(unique_routes)]
        if filtered_parking.empty:
            await update.callback_query.message.reply_text("❌ Нет доступных парковок для текущих данных.")
            return
        parking_numbers = filtered_parking['parking_number'].unique()
        keyboard = [[InlineKeyboardButton(f"📍 Парковка {num}", callback_data=f"parking_{num}")] for num in parking_numbers]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text("Выберите парковку:", reply_markup=reply_markup)
    except Exception as e:
        print(f"Ошибка при выборе парковки: {e}")
        await update.callback_query.message.reply_text("❌ Произошла ошибка при выборе парковки.")

# Обработка выбора парковки
async def handle_parking_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parking_number = int(query.data.split('_')[1])
    analysis_message = analyze_parking(parking_number)
    await query.message.reply_text(analysis_message, parse_mode="HTML")

# Анализ данных для выбранной парковки
def analyze_parking(parking_number):
    if PARKING_MAPPING is None or DATA is None:
        return "❌ Данные о парковках или основные данные не загружены."
    parking_info = PARKING_MAPPING[PARKING_MAPPING['parking_number'] == parking_number]
    if parking_info.empty:
        return f"❌ Парковка {parking_number} не найдена."
    route_id = parking_info.iloc[0]['route_id']
    filtered_data = DATA[DATA['Лог. маршрут'].str[:5] == str(route_id)]
    if filtered_data.empty:
        return f"❌ Для парковки {parking_number} (Маршрут {route_id}) нет данных."
    # Вычисляем метрики
    total_sum = filtered_data['Сумма путевого листа'].sum()
    total_fines = filtered_data['Сумма штрафов'].sum()
    avg_items = filtered_data['Кол-во шк.'].mean()
    total_routes = len(filtered_data)
    routes_without_returns = len(filtered_data[
        (filtered_data['Возвраты: всего/доставлено'] == '0/0') |  
        (filtered_data['Процент доставки возвратов'] == 0) |      
        (filtered_data['Возвраты: всего/доставлено'].isnull())    
    ])
    total_returns = filtered_data['Всего_возвратов'].sum()
    delivered_returns = filtered_data['Доставлено_возвратов'].sum()
    delivery_rate_returns = (delivered_returns / total_returns) * 100 if total_returns > 0 else 0
    delivery_rate_boxes = filtered_data['Процент доставки коробок'].mean() if 'Процент доставки коробок' in filtered_data.columns else None
    avg_route_sum = filtered_data['Сумма путевого листа'].mean()
    net_profit = total_sum - total_fines
    message = (
        "📊 <b>Анализ данных для парковки {}:</b>\n"
        "------------------------------------\n"
        "💰 <b>Сумма путевых:</b> {:.2f}\n"
        "⚠️ <b>Сумма штрафов:</b> {:.2f}\n"
        "📦 <b>Среднее кол-во ШК:</b> {:.2f}\n"
        "🚗 <b>Кол-во путевых:</b> {}\n"
        "🔄 <b>Кол-во путевых без возвратов:</b> {}\n"
        "\n"
        "🚚 <b>Возвраты:</b>\n"
        "   • Всего: {}\n"
        "   • Доставлено: {}\n"
        "   • Процент доставки: {:.2f}%\n"
        "\n"
        "📦 <b>Коробки:</b>\n"
        "   • Процент доставки: {:.2f}%\n"
        "\n"
        "📈 <b>Средняя сумма путевого листа:</b> {:.2f}\n"
        "💵 <b>Чистая прибыль (Общая сумма - Штрафы):</b> {:.2f}\n"
    ).format(
        parking_number, total_sum, total_fines, avg_items, total_routes, routes_without_returns,
        total_returns, delivered_returns, delivery_rate_returns,
        delivery_rate_boxes, avg_route_sum, net_profit
    )
    return message

# Команда "Выгрузить Путевые листы за предыдущий день"
async def download_and_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message
    await message.reply_text("⏳ Начинаю скачивание файла...")
    try:
        # Скачиваем файл с помощью скрипта
        from scripts.download_script import main as download_file
        download_file()
        # Находим последний скачанный файл
        file_path = get_latest_downloaded_file(DOWNLOAD_FOLDER)
        if not file_path or not os.path.exists(file_path):
            await message.reply_text("❌ Не удалось скачать файл. Попробуйте еще раз.")
            return
        # Загружаем данные из файла
        load_message = load_excel_data(file_path)
        await message.reply_text(load_message)
        # Загружаем данные о парковках
        parking_file_path = os.path.join(DOWNLOAD_FOLDER, "parking_mapping.csv")
        parking_load_message = load_parking_mapping(parking_file_path)
        await message.reply_text(parking_load_message)
        # Анализируем данные и отправляем результат
        analysis_message = analyze_data()
        await message.reply_text(analysis_message, parse_mode="HTML")
        # После отправки статистики добавляем кнопки
        keyboard = [
            [InlineKeyboardButton("Все путевые листы", callback_data="show_all_routes")],
            [InlineKeyboardButton("Список водителей", callback_data="show_drivers_list")],
            [InlineKeyboardButton("Выбрать парковку", callback_data="choose_parking")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("Выберите действие:", reply_markup=reply_markup)
    except Exception as e:
        print(f"Ошибка при скачивании или обработке файла: {e}")
        await message.reply_text("❌ Произошла ошибка при обработке файла.")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# Обработка инлайн кнопок
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "download_previous_day":
        await download_and_analyze(query, context)
    elif query.data == "show_all_routes":
        await show_all_routes(update, context)
    elif query.data.startswith("route_"):
        await handle_route_choice(update, context)
    elif query.data.startswith("driver_"):
        await handle_driver_choice(update, context)
    elif query.data.startswith("parking_"):
        await handle_parking_choice(update, context)
    elif query.data.startswith("all_routes_page_"):
        page = int(query.data.split('_')[-1])
        await show_all_routes(update, context, page=page)
    elif query.data.startswith("drivers_page_"):
        page = int(query.data.split('_')[-1])
        await show_drivers_list(update, context, page=page)

# Основная функция
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^download_previous_day$"))
    app.add_handler(CallbackQueryHandler(show_all_routes, pattern="^show_all_routes$"))
    app.add_handler(CallbackQueryHandler(show_drivers_list, pattern="^show_drivers_list$"))
    app.add_handler(CallbackQueryHandler(handle_route_choice, pattern="^route_"))
    app.add_handler(CallbackQueryHandler(handle_driver_choice, pattern="^driver_"))
    app.add_handler(CallbackQueryHandler(choose_parking, pattern="^choose_parking$"))
    app.add_handler(CallbackQueryHandler(handle_parking_choice, pattern="^parking_"))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^all_routes_page_|^drivers_page_"))

    print("Бот запущен...")
    app.run_polling()
