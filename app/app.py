from PyQt6 import QtGui, uic
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow

from app.core import (
    get_rel_path,
    select_entrance_table,
    select_login_table,
    select_exception_list,
    select_fired_list,
    run_checker,
    export_result,
    )


class App(QMainWindow):
    def __init__(self, version: str):
        super().__init__()
        self.version = version
        self.ui = None
        self.scan_result = None
        self.settings = QSettings("LeakedPassChecker", "App")
        self.load_ui()

    def load_ui(self):
        self.ui = uic.loadUi(get_rel_path("main.ui"), self)
        self.ui.setWindowTitle(f"Поиск утекших паролей {self.version}")
        self.ui.setWindowIcon(QIcon(get_rel_path("icon.ico")))

        # Иконки
        file_icon_path = get_rel_path("file.png")
        self.ui.pushButton_entrances.setIcon(QIcon(file_icon_path))
        self.ui.pushButton_logins.setIcon(QIcon(file_icon_path))
        self.ui.pushButton_exceptions.setIcon(QIcon(file_icon_path))
        self.ui.pushButton_fireds.setIcon(QIcon(file_icon_path))

        self.ui.pushButton_check.setIcon(QIcon(get_rel_path("start.png")))
        self.ui.pushButton_save.setIcon(QIcon(get_rel_path("excel.png")))

        # Кнопки
        self.ui.pushButton_entrances.clicked.connect(lambda: select_entrance_table(self))
        self.ui.pushButton_logins.clicked.connect(lambda: select_login_table(self))
        self.ui.pushButton_exceptions.clicked.connect(lambda: select_exception_list(self))
        self.ui.pushButton_fireds.clicked.connect(lambda: select_fired_list(self))

        self.ui.pushButton_check.clicked.connect(lambda: run_checker(self))
        self.ui.pushButton_save.clicked.connect(lambda: export_result(self))

        self.setup_last_values()
        self.ui.show()

    def setup_last_values(self):
        fields = { "lineEdit_exceptions": "paths/exceptions", "lineEdit_fireds": "paths/fireds", }

        for widget_name, settings_key in fields.items():
            line_edit = getattr(self.ui, widget_name, None)

            if line_edit is None:
                continue

            last_value = self.settings.value(settings_key, "", str) or ""

            if last_value:
                line_edit.setText(last_value)

            line_edit.textChanged.connect(lambda text, key = settings_key: self.settings.setValue(key, text))
