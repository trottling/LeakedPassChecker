import sys

from PyQt6.QtWidgets import QApplication

from app.app import App
from app.utils import warn_user

VERSION = "0.4.0"


def main():
    app = QApplication(sys.argv)
    main_window = App(VERSION)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
