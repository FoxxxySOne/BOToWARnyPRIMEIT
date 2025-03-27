# scripts/download_script.py
import pyautogui
import pygetwindow as gw
import time
import keyboard
import random
import os
from config import DOWNLOADED_FILE_PATH

# Пути к изображениям кнопок
button1_path = r"C:\Users\Administrator\Desktop\BOToWARnyPRIMEIT\BOTANAL(auto)\scripts\1.png"
button2_path = r"C:\Users\Administrator\Desktop\BOToWARnyPRIMEIT\BOTANAL(auto)\scripts\PROM.png"
button3_path = r"C:\Users\Administrator\Desktop\BOToWARnyPRIMEIT\BOTANAL(auto)\scripts\3.png"
button4_path = r"C:\Users\Administrator\Desktop\BOToWARnyPRIMEIT\BOTANAL(auto)\scripts\4.png"

# Название окна Chrome
browser_window_title = "Google Chrome"

def main():
    try:
        # Находим окно Chrome
        browser_windows = gw.getWindowsWithTitle(browser_window_title)
        
        if not browser_windows:
            print("Окно Chrome не найдено.")
            return None
        
        # Берем первое найденное окно Chrome
        browser_window = browser_windows[0]
        
        # Если окно свернуто, разворачиваем его
        if browser_window.isMinimized:
            browser_window.restore()
        
        # Активируем окно Chrome
        browser_window.activate()
        time.sleep(5)  # Подождем, пока окно станет активным

        # Переключаемся на первую вкладку (CTRL + 1)
        pyautogui.hotkey('ctrl', '1')
        time.sleep(5)  # Ждем, пока переключение завершится

        # Обновляем страницу (F5)
        pyautogui.press('f5')
        print("Страница обновляется...")

        # Ждем 5-8 секунд для загрузки страницы (случайное значение для имитации реальной загрузки)
        wait_time = random.uniform(5, 10)
        time.sleep(wait_time)
        print(f"Страница загружена за {wait_time:.1f} секунд.")

        # Ищем первую кнопку по скрину
        button1_location = pyautogui.locateCenterOnScreen(button1_path, confidence=0.9)
        if button1_location:
            print(f"Найдена первая кнопка: {button1_location}")
            pyautogui.click(button1_location)
            time.sleep(3)  # Ждем, пока поле станет активным

            # Вводим текст "промышленная" с помощью библиотеки keyboard
            keyboard.write("Промышленная", delay=0.1)
            time.sleep(3)  # Ждем немного

            # Ищем вторую кнопку по скрину
            button2_location = pyautogui.locateCenterOnScreen(button2_path, confidence=0.9)
            if button2_location:
                print(f"Найдена вторая кнопка: {button2_location}")
                pyautogui.click(button2_location)
                time.sleep(3)  # Ждем 3 секунды

                # Ищем третью кнопку по скрину
                button3_location = pyautogui.locateCenterOnScreen(button3_path, confidence=0.9)
                if button3_location:
                    print(f"Найдена третья кнопка: {button3_location}")
                    pyautogui.click(button3_location)
                    time.sleep(5)  # Ждем 3 секунды

                    # Ищем четвертую кнопку по скрину
                    button4_location = pyautogui.locateCenterOnScreen(button4_path, confidence=0.9)
                    if button4_location:
                        print(f"Найдена четвертая кнопка: {button4_location}")
                        pyautogui.click(button4_location)

                        # Ждем 10 секунд после нажатия на четвертую кнопку
                        print("Ждем 10 секунд после нажатия на четвертую кнопку...")
                        time.sleep(10)

                        # Сохраняем файл в указанном пути
                        return DOWNLOADED_FILE_PATH

                    else:
                        print("Четвертая кнопка не найдена.")
                else:
                    print("Третья кнопка не найдена.")
            else:
                print("Вторая кнопка не найдена.")
        else:
            print("Первая кнопка не найдена.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None
