import pandas as pd

DATA = None

def load_excel_data(file_path):
    global DATA
    try:
        DATA = pd.read_excel(file_path)
        return "✅ Данные успешно загружены!"
    except Exception as e:
        return f"❌ Ошибка при загрузке данных: {e}"

def analyze_data():
    global DATA
    if DATA is None:
        return "❌ Данные не загружены."
    total_sum = DATA['Сумма путевого листа'].sum()
    total_fines = DATA['Сумма штрафов'].sum()
    avg_items = DATA['Кол-во шк.'].mean()
    message = (
        "📊 <b>Общий анализ:</b>\n"
        f"💰 Сумма путевых: {total_sum:.2f}\n"
        f"⚠️ Сумма штрафов: {total_fines:.2f}\n"
        f"📦 Среднее кол-во ШК: {avg_items:.2f}"
    )
    return message