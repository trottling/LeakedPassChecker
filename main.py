import ctypes
import sys

from PySide6.QtWidgets import QApplication

from src.app import App


def main():
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("LeakedPassChecker.App")

    app = QApplication(sys.argv)
    main_window = App()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
