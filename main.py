import sys

from PySide6.QtWidgets import QApplication

from src.app import App


def main():
    app = QApplication(sys.argv)
    main_window = App()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
