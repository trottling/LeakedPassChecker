import sys

from PyQt6.QtWidgets import QApplication

from src.app import App
from src.utils import warn_user


def main():
    app = QApplication(sys.argv)
    main_window = App()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
