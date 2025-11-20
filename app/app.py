from PyQt6 import QtGui, uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow

from app.buttons import export_result, run_checker, select_entrance_table, select_login_table
from app.utils import get_rel_path


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = None
        self.scan_result = None
        self.load_ui()

    def load_ui(self):
        self.ui = uic.loadUi(get_rel_path("main.ui"), self)
        self.ui.setWindowTitle("Поиск утекших паролей")

        # Картинки

        self.ui.setWindowIcon(QIcon(get_rel_path('icon.ico')))
        self.ui.pushButton_entrance.setIcon(QtGui.QIcon(get_rel_path('file.png')))
        self.ui.pushButton_login.setIcon(QtGui.QIcon(get_rel_path('file.png')))
        self.ui.pushButton_run.setIcon(QtGui.QIcon(get_rel_path('start.png')))
        self.ui.pushButton_export.setIcon(QtGui.QIcon(get_rel_path('excel.png')))

        # Кнопки

        self.ui.pushButton_entrance.clicked.connect(lambda: select_entrance_table(self))
        self.ui.pushButton_login.clicked.connect(lambda: select_login_table(self))
        self.ui.pushButton_run.clicked.connect(lambda: run_checker(self))
        self.ui.pushButton_export.clicked.connect(lambda: export_result(self))

        ###

        self.ui.show()
