import sys

from PyQt6.QtWidgets import QApplication

from app.app import App
from app.core import warn_user

VERSION = "0.3.1"

def main():
    try:
        app = QApplication(sys.argv)
        main_window = App(VERSION)
        sys.exit(app.exec())
    except Exception as e:
        warn_user(None, "Глобальная ошибка", f"{str(e)}\n\n{e.args}")

if __name__ == '__main__':
    main()