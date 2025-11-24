from PyQt6 import QtGui, uic
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow

from app.buttons import *
from app.utils import get_rel_path


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = None
        self.scan_result = None
        self.settings = QSettings("LeakedPassChecker", "App")
        self.load_ui()

    def load_ui(self):
        self.ui = uic.loadUi(get_rel_path("main.ui"), self)
        self.ui.setWindowTitle("Поиск утекших паролей")
        self.ui.setWindowIcon(QIcon(get_rel_path('icon.ico')))

        # Картинки

        self.ui.pushButton_entrances.setIcon(QtGui.QIcon(get_rel_path('file.png')))
        self.ui.pushButton_logins.setIcon(QtGui.QIcon(get_rel_path('file.png')))
        self.ui.pushButton_exceptions.setIcon(QtGui.QIcon(get_rel_path('file.png')))
        self.ui.pushButton_fireds.setIcon(QtGui.QIcon(get_rel_path('file.png')))

        self.ui.pushButton_check.setIcon(QtGui.QIcon(get_rel_path('start.png')))
        self.ui.pushButton_save.setIcon(QtGui.QIcon(get_rel_path('excel.png')))

        # Кнопки

        self.ui.pushButton_entrances.clicked.connect(lambda: select_entrance_table(self))
        self.ui.pushButton_logins.clicked.connect(lambda: select_login_table(self))
        self.ui.pushButton_exceptions.clicked.connect(lambda: select_exception_table(self))
        self.ui.pushButton_fireds.clicked.connect(lambda: select_fired_list(self))

        self.ui.pushButton_check.clicked.connect(lambda: run_checker(self))
        self.ui.pushButton_save.clicked.connect(lambda: export_result(self))

        ###

        self.setup_last_values()
        self.ui.show()

    def setup_last_values(self):
        fields = {
            "lineEdit_exceptions": "paths/exceptions",
            "lineEdit_fireds": "paths/fireds",
            }

        for widget_name, settings_key in fields.items():
            line_edit = getattr(self.ui, widget_name, None)

            if line_edit is None:
                continue

            last_value = self.settings.value(settings_key, "", str) or ""

            if last_value:
                line_edit.setText(last_value)

            line_edit.textChanged.connect(lambda text, key = settings_key: self.settings.setValue(key, text))
