import sys

from PyQt6.QtWidgets import QApplication

from app.app import App
from app.utils import warn_user


def main():
    try:
        app = QApplication(sys.argv)
        main_window = App()
        sys.exit(app.exec())
    except Exception as e:
        warn_user("Глобальная ошибка", str(e))

if __name__ == '__main__':
    main()