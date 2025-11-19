from PyQt6 import QtGui, uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow

from buttons import export_csv, export_excel, export_json, run_checker, select_entrance_table, select_login_table
from utils import get_rel_path


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
        self.ui.pushButton_export_excel.setIcon(QtGui.QIcon(get_rel_path('excel.png')))
        self.ui.pushButton_export_csv.setIcon(QtGui.QIcon(get_rel_path('csv.png')))
        self.ui.pushButton_export_json.setIcon(QtGui.QIcon(get_rel_path('json.png')))

        # Кнопки

        self.ui.pushButton_entrance.clicked.connect(lambda: select_entrance_table(self))
        self.ui.pushButton_login.clicked.connect(lambda: select_login_table(self))
        self.ui.pushButton_run.clicked.connect(lambda: run_checker(self))
        self.ui.pushButton_export_excel.clicked.connect(lambda: export_excel(self))
        self.ui.pushButton_export_csv.clicked.connect(lambda: export_csv(self))
        self.ui.pushButton_export_json.clicked.connect(lambda: export_json(self))

        ###

        self.ui.show()
