import os

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog
from checker.checker import Checker, Checker_config
from export.csv_ import export_to_csv
# from export.excel import export_to_excel
from export.json_ import export_to_json

from app.utils import get_rel_path, warn_user


def select_entrance_table(self):
    try:
        file_path, _ = QFileDialog.getOpenFileName(None, "Выбери Excel файл", "", "Excel Files (*.xlsx *.xls)")

        if not file_path:
            return
    except:
        return

    self.ui.lineEdit_entrance.setText(file_path)


def select_login_table(self):
    try:
        file_path, _ = QFileDialog.getOpenFileName(None, "Выбери Excel файл", "", "Excel Files (*.xlsx *.xls)")

        if not file_path:
            return
    except:
        return

    self.ui.lineEdit_login.setText(file_path)


def inactive_ui(self):
    self.ui.pushButton_run.setText("Проверка")
    self.ui.pushButton_run.setEnabled(False)
    self.ui.pushButton_run.setIcon(QtGui.QIcon(get_rel_path('loading.png')))
    self.ui.pushButton_run.setIconSize(QtCore.QSize(25, 25))
    self.ui.pushButton_export_excel.setEnabled(False)
    self.ui.pushButton_export_csv.setEnabled(False)
    self.ui.pushButton_export_json.setEnabled(False)


def active_ui(self):
    self.ui.pushButton_run.setText("Начать поиск")
    self.ui.pushButton_run.setEnabled(True)
    self.ui.pushButton_run.setIcon(QtGui.QIcon(get_rel_path('start.png')))
    self.ui.pushButton_run.setIconSize(QtCore.QSize(25, 25))
    self.ui.pushButton_export_excel.setEnabled(True)
    self.ui.pushButton_export_csv.setEnabled(True)
    self.ui.pushButton_export_json.setEnabled(True)


def run_checker(self):
    entrance_table_path = self.ui.lineEdit_entrance.text()
    login_table_path = self.ui.lineEdit_login.text()
    check_then_not_in_territory = self.ui.checkBox_territory.isChecked()

    if entrance_table_path == "":
        warn_user("Заполните все поля", "Путь к журналу проходной пустой")
        return

    if login_table_path == "":
        warn_user("Заполните все поля", "Путь к журналу входов в систему пустой")
        return

    if entrance_table_path == login_table_path:
        warn_user("Неправильный таблицы", "Одинаковые пути к журналам")
        return

    if not os.path.isfile(entrance_table_path):
        warn_user("Файл не найден", "Неправильный путь к журналу проходной")
        return

    if not os.path.isfile(login_table_path):
        warn_user("Файл не найден", "Неправильный путь к журналу входов в систему")
        return

    inactive_ui(self)

    checker = Checker(
        Checker_config(
            login_table_path=login_table_path,
            entrance_table_path=entrance_table_path,
            check_then_not_in_territory=check_then_not_in_territory
            )
        )

    checker.signals.result.connect(lambda result: on_result(self, result))
    checker.signals.finished.connect(lambda: on_finished(self))
    checker.signals.error.connect(lambda e: on_error(e))
    QtCore.QThreadPool.globalInstance().start(checker)


def on_result(self, result):
    self.scan_result = result

    html = f"""
        <p style="font-size:14pt; font-weight:600;">
            <span style="color:#cc0000;">Утечек: {self.scan_result.compromised_count}</span><br>
            <span style="color:#ffaa00;">Нет совпадений: {self.scan_result.no_matches_count}</span><br>
            <span style="color:#00c500;">Сопоставлено: {self.scan_result.matched_count}</span>
        </p>
        """

    self.ui.label_stats.setTextFormat(Qt.TextFormat.RichText)
    self.ui.label_stats.setText(html)


def on_finished(self):
    active_ui(self)


def on_error(error):
    warn_user("Ошибка проверки", str(error))


def get_path(default_name, file_type):
    file_path, _ = QFileDialog.getSaveFileName(None, "Сохранить файл как...", default_name, file_type)
    return file_path if file_path else None


def export_data(self, exporter, path):
    if self.scan_result is None:
        warn_user("Нет результатов", "Нет результатов для выгрузки")
        return

    try:
        exporter(self.scan_result, path)
    except Exception as e:
        warn_user("Ошибка экспорта", str(e))


def export_json(self):
    path = get_path("result.json", "JSON Files (*.json);;Все файлы (*.*)")
    if path is None:
        return

    export_data(self, export_to_json, path)


def export_csv(self):
    path = get_path("result.csv", "CSV Files (*.csv);;Все файлы (*.*)")
    if path is None:
        return

    export_data(self, export_to_csv, path)


def export_excel(self):
    path = get_path("result.xlsx", "Excel Files (*.xlsx *.xls);;Все файлы (*.*)")
    if path is None:
        return

    # export_data(self, export_to_excel, path)
