import os

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QFileDialog

from app.checker import Checker, CheckerConfig
from app.utils import get_rel_path, warn_user


def select_entrance_table(self):
    try:
        file_path, _ = QFileDialog.getOpenFileName(None, "Выберите Excel файл", "", "Excel Files (*.xlsx *.xls)")

        if not file_path:
            return
    except:
        return

    self.ui.lineEdit_entrances.setText(file_path)


def select_login_table(self):
    try:
        file_path, _ = QFileDialog.getOpenFileName(None, "Выберите Excel файл", "", "Excel Files (*.xlsx *.xls)")

        if not file_path:
            return
    except:
        return

    self.ui.lineEdit_logins.setText(file_path)


def select_fired_list(self):
    try:
        file_path, _ = QFileDialog.getOpenFileName(None, "Выберите TXT файл", "", "Text Files (*.txt)")

        if not file_path:
            return
    except:
        return

    self.ui.lineEdit_fireds.setText(file_path)


def select_exception_table(self):
    try:
        file_path, _ = QFileDialog.getOpenFileName(None, "Выберите TXT файл с паттернами исключений", "", "Text Files (*.txt);;Все файлы (*.*)")

        if not file_path:
            return
    except:
        return

    self.ui.lineEdit_exceptions.setText(file_path)


def inactive_ui(self):
    self.ui.pushButton_check.setText("Проверка")
    self.ui.pushButton_check.setEnabled(False)
    self.ui.pushButton_check.setIcon(QtGui.QIcon(get_rel_path('loading.png')))
    self.ui.pushButton_check.setIconSize(QtCore.QSize(25, 25))
    self.ui.pushButton_save.setEnabled(False)


def active_ui(self):
    self.ui.pushButton_check.setText("Начать поиск")
    self.ui.pushButton_check.setEnabled(True)
    self.ui.pushButton_check.setIcon(QtGui.QIcon(get_rel_path('start.png')))
    self.ui.pushButton_check.setIconSize(QtCore.QSize(25, 25))
    self.ui.pushButton_save.setEnabled(True)


def run_checker(self):
    entrances_table_path = self.ui.lineEdit_entrances.text().strip()
    logins_table_path = self.ui.lineEdit_logins.text().strip()
    exceptions_table_path = self.ui.lineEdit_exceptions.text().strip()
    fired_list_path = self.ui.lineEdit_fireds.text().strip()

    if entrances_table_path == "":
        warn_user("Заполните все поля", "Путь к журналу проходной пустой")
        return

    if logins_table_path == "":
        warn_user("Заполните все поля", "Путь к журналу входов в систему пустой")
        return

    if entrances_table_path == logins_table_path:
        warn_user("Неправильный таблицы", "Одинаковые пути к журналам")
        return

    if not os.path.isfile(entrances_table_path):
        warn_user("Файл не найден", "Неправильный путь к журналу проходной")
        return

    if not os.path.isfile(logins_table_path):
        warn_user("Файл не найден", "Неправильный путь к журналу входов в систему")
        return

    if exceptions_table_path != "" and not os.path.isfile(exceptions_table_path):
        warn_user("Файл не найден", "Неправильный путь к файлу исключений")
        return

    if fired_list_path != "" and not os.path.isfile(fired_list_path):
        warn_user("Файл не найден", "Неправильный путь к списку уволенных")
        return

    inactive_ui(self)

    checker = Checker(
        CheckerConfig(
            logins_table_path=logins_table_path,
            entrances_table_path=entrances_table_path,
            exceptions_table_path=exceptions_table_path,
            fired_list_path=fired_list_path
            )
        )

    checker.signals.result.connect(lambda result: on_result(self, result))
    checker.signals.finished.connect(lambda: on_finished(self))
    checker.signals.error.connect(lambda e: on_error(self, e))
    QtCore.QThreadPool.globalInstance().start(checker)

def on_stat(self, done, total):
    self.ui.pushButton_check.setText(f"{done} / {total}")

def on_result(self, result):
    self.scan_result = result

    self.ui.label_stats_leaks.setText(f"Утечек: {self.scan_result.compromised_count}")
    self.ui.label_stats_leaks.setStyleSheet("color: #cc0000; font-weight:600")

    self.ui.label_stats_excluded.setText(f"Исключения: {self.scan_result.exceptions_count}")
    self.ui.label_stats_excluded.setStyleSheet("font-weight:600")

    self.ui.label_stats_no_logins.setText(f"Нет входа: {self.scan_result.no_login_count}")
    self.ui.label_stats_no_logins.setStyleSheet("color: #ffaa00; font-weight:600")

    self.ui.label_stats_matches.setText(f"Сопоставлено: {self.scan_result.matched_count}")
    self.ui.label_stats_matches.setStyleSheet("color: #00c500; font-weight:600")

    self.ui.label_stats_total.setText(f"Всего: {self.scan_result.total_count}")
    self.ui.label_stats_total.setStyleSheet("font-weight:600")


def on_finished(self):
    active_ui(self)


def on_error(self, error):
    self.scan_result = None
    warn_user("Ошибка проверки", str(error))


def export_result(self):
    if self.scan_result is None:
        warn_user("Нет результатов", "Нет результатов для выгрузки")
        return

    file_path, _ = QFileDialog.getSaveFileName(None, "Сохранить файл как...", "result.xlsx", "Excel Files (*.xlsx *.xls);;Все файлы (*.*)")

    if not file_path:
        return

    try:
        export_to_excel(self.scan_result, file_path)
    except Exception as e:
        warn_user("Ошибка экспорта", str(e))


def export_to_excel(result, path):
    pass