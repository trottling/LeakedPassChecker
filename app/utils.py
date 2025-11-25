import os
import re
import sys

from PyQt6.QtWidgets import QMessageBox


def clean_str(text: str) -> str:
    # Ё -> Е
    text = text.replace("Ё", "Е")

    # оставляем только А-Я, остальное -> пробел
    text = re.sub(r'[^А-Я]', ' ', text)

    # сжимаем пробелы
    text = re.sub(r'\s+', ' ', text).strip()

    # всё в lower()
    text = text.lower()

    # каждое слово с заглавной
    text = ' '.join(word.capitalize() for word in text.split())

    # пробелы по бокам
    text = text.strip()

    return text

def match_pattern(pattern: str, text: str) -> bool:
    """
    Сопоставляет текст с паттерном, поддерживая wildcards:
    * - любое количество любых символов
    ? - один любой символ
    """

    if not pattern:
        return False
    if not text:
        text = ""
    
    # Преобразуем паттерн в регулярное выражение
    # Экранируем специальные символы regex, кроме * и ?
    pattern_re = re.escape(pattern)
    # Заменяем экранированные \* и \? на соответствующие regex паттерны
    pattern_re = pattern_re.replace(r'\*', '.*').replace(r'\?', '.')
    # Добавляем якоря для полного совпадения
    pattern_re = f'^{pattern_re}$'
    
    try:
        return bool(re.match(pattern_re, str(text), re.IGNORECASE))
    except:
        return False


def get_rel_path(data_path, slash_replace = True):
    if getattr(sys, 'frozen', False):
        try:
            base_path = sys._MEIPASS
        except Exception:
            return ""
    else:
        data_path = f"..\\assets\\{data_path}"
        base_path = os.path.dirname(os.path.abspath(__file__))

    result = os.path.join(base_path, data_path)

    if slash_replace:
        result = result.replace("\\", "/")

    return str(result)


def warn_user(title, text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.resize(500, 300)
    msg.exec()