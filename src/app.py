import os

from PySide6 import QtCore, QtGui
from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QFileDialog, QMainWindow

from src.checker import Checker, CheckerConfig, CheckerResult
from src.utils import export_to_excel, get_rel_path, load_app_version, select_file, warn_user


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = None
        self.scan_result = None
        self.settings = QSettings("LeakedPassChecker", "App")
        self.load_ui()

    def load_ui(self):
        self.ui = QUiLoader().load(get_rel_path("main.ui"))
        version = load_app_version()
        suffix = f" v{version}" if version else ""
        self.ui.setWindowTitle(f"Поиск утекших паролей{suffix}")
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
        self.ui.pushButton_entrances.clicked.connect(self.select_entrance_table)
        self.ui.pushButton_logins.clicked.connect(self.select_login_table)
        self.ui.pushButton_exceptions.clicked.connect(self.select_exception_list)
        self.ui.pushButton_fireds.clicked.connect(self.select_fired_list)

        self.ui.pushButton_check.clicked.connect(self.run_checker)
        self.ui.pushButton_save.clicked.connect(self.export_result)

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

    def select_entrance_table(self):
        file_path = select_file(self, "Выберите Excel файл", "Excel Files (*.xlsx *.xls)")
        if not file_path:
            return
        self.ui.lineEdit_entrances.setText(file_path)

    def select_login_table(self):
        file_path = select_file(self, "Выберите Excel файл", "Excel Files (*.xlsx *.xls)")
        if not file_path:
            return
        self.ui.lineEdit_logins.setText(file_path)

    def select_fired_list(self):
        file_path = select_file(self, "Выберите TXT файл", "Text Files (*.txt)")
        if not file_path:
            return
        self.ui.lineEdit_fireds.setText(file_path)

    def select_exception_list(self):
        file_path = select_file(self, "Выберите TXT файл", "Text Files (*.txt);;Все файлы (*.*)")
        if not file_path:
            return
        self.ui.lineEdit_exceptions.setText(file_path)

    def inactive_ui(self):
        self.setCursor(QtCore.Qt.CursorShape.WaitCursor)
        self.ui.pushButton_check.setText("Проверка")
        self.ui.pushButton_check.setEnabled(False)
        self.ui.pushButton_check.setIcon(QtGui.QIcon(get_rel_path("loading.png")))
        self.ui.pushButton_check.setIconSize(QtCore.QSize(25, 25))
        self.ui.pushButton_save.setEnabled(False)

    def active_ui(self):
        self.unsetCursor()
        self.ui.pushButton_check.setText("Начать поиск")
        self.ui.pushButton_check.setEnabled(True)
        self.ui.pushButton_check.setIcon(QtGui.QIcon(get_rel_path("start.png")))
        self.ui.pushButton_check.setIconSize(QtCore.QSize(25, 25))
        self.ui.pushButton_save.setEnabled(True)

    def run_checker(self):
        entrances_table_path = (self.ui.lineEdit_entrances.text().strip().replace("/", "\\"))
        logins_table_path = self.ui.lineEdit_logins.text().strip().replace("/", "\\")
        exceptions_list_path = (self.ui.lineEdit_exceptions.text().strip().replace("/", "\\"))
        fired_list_path = self.ui.lineEdit_fireds.text().strip().replace("/", "\\")

        if not entrances_table_path:
            warn_user(self, "Заполните все поля", "Путь к журналу проходной пустой")
            return

        if not logins_table_path:
            warn_user(self, "Заполните все поля", "Путь к журналу входов в систему пустой")
            return

        if entrances_table_path == logins_table_path:
            warn_user(self, "Неправильный таблицы", "Одинаковые пути к журналам")
            return

        if not os.path.isfile(entrances_table_path):
            warn_user(self, "Файл не найден", "Неправильный путь к журналу проходной")
            return

        if not os.path.isfile(logins_table_path):
            warn_user(self, "Файл не найден", "Неправильный путь к журналу входов в систему")
            return

        if exceptions_list_path and not os.path.isfile(exceptions_list_path):
            warn_user(self, "Файл не найден", "Неправильный путь к списку исключений")
            return

        if fired_list_path and not os.path.isfile(fired_list_path):
            warn_user(self, "Файл не найден", "Неправильный путь к списку уволенных")
            return

        self.inactive_ui()

        checker = Checker(
            CheckerConfig(
                logins_table_path=logins_table_path,
                entrances_table_path=entrances_table_path,
                exceptions_list_path=exceptions_list_path,
                fired_list_path=fired_list_path,
                )
            )

        checker.signals.result.connect(self.on_result)
        checker.signals.finished.connect(self.on_finished)
        checker.signals.error.connect(self.on_error)
        QtCore.QThreadPool.globalInstance().start(checker)

    def on_result(self, result: CheckerResult):
        self.scan_result = result

        self.ui.label_stats_leaks.setText(f"Утечек: {len(self.scan_result.compromised)}")
        self.ui.label_stats_leaks.setStyleSheet("color: #cc0000; font-weight:600")

        self.ui.label_stats_excluded.setText(f"Исключения: {len(self.scan_result.exceptions)}")
        self.ui.label_stats_excluded.setStyleSheet("font-weight:600")

        self.ui.label_stats_no_logins.setText(f"Нет входа: {len(self.scan_result.no_login)}")
        self.ui.label_stats_no_logins.setStyleSheet("color: #ffaa00; font-weight:600")

        self.ui.label_stats_matches.setText(f"Сопоставлено: {len(self.scan_result.matched)}")
        self.ui.label_stats_matches.setStyleSheet("color: #00c500; font-weight:600")

        total = (len(self.scan_result.compromised) + len(self.scan_result.exceptions) + len(self.scan_result.no_login) + len(self.scan_result.matched))
        self.ui.label_stats_total.setText(f"Всего: {total}")
        self.ui.label_stats_total.setStyleSheet("font-weight:600")

    def on_finished(self):
        self.active_ui()

    def on_error(self, error):
        self.scan_result = None
        warn_user(self, "Ошибка проверки", str(error))

    def export_result(self):
        if self.scan_result is None:
            warn_user(self, "Нет результатов", "Нет результатов для выгрузки")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл как...", "result.xlsx", "Excel Files (*.xlsx *.xls);;Все файлы (*.*)")

        if not file_path:
            return

        try:
            export_to_excel(self.scan_result, file_path)
        except Exception as e:
            warn_user(self, "Ошибка экспорта", str(e))
