import os

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QFileDialog
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from app.checker import Checker, Checker_config
from app.utils import _build_combined_headers, _iter_joined_rows, clean_str, get_rel_path, warn_user


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
        file_path, _ = QFileDialog.getOpenFileName(None, "Выбери Excel файл", "", "Excel Files (*.xlsx *.xls)")

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
    entrances_table_path = self.ui.lineEdit_entrances.text()
    logins_table_path = self.ui.lineEdit_logins.text()
    exceptions_table_path = self.ui.lineEdit_exceptions.text()
    fired_list_path = self.ui.lineEdit_fireds.text()

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

    if not os.path.isfile(exceptions_table_path):
        warn_user("Файл не найден", "Неправильный путь к таблице исключений")
        return

    if not os.path.isfile(fired_list_path):
        warn_user("Файл не найден", "Неправильный путь к списку уволенных")
        return

    inactive_ui(self)

    checker = Checker(
        Checker_config(
            logins_table_path=logins_table_path,
            entrance_table_path=entrances_table_path,
            )
        )

    checker.signals.result.connect(lambda result: on_result(self, result))
    checker.signals.finished.connect(lambda: on_finished(self))
    checker.signals.error.connect(lambda e: on_error(self, e))
    QtCore.QThreadPool.globalInstance().start(checker)


def on_result(self, result):
    self.scan_result = result

    self.ui.label_stats_leak.setText(f"Утечек: {self.scan_result.compromised_count}")
    self.ui.label_stats_leak.setStyleSheet("color: #cc0000; font-weight:600")

    self.ui.label_stats_exclude.setText(f"Исключения: {self.scan_result.compromised_count}")
    self.ui.label_stats_exclude.setStyleSheet("font-weight:600")

    self.ui.label_stats_no_login.setText(f"Нет входа: {self.scan_result.no_login_count}")
    self.ui.label_stats_no_login.setStyleSheet("color: #ffaa00; font-weight:600")

    self.ui.label_stats_matched.setText(f"Сопоставлено: {self.scan_result.matched_count}")
    self.ui.label_stats_matched.setStyleSheet("color: #00c500; font-weight:600")

    self.ui.label_stats_all.setText(f"Всего: {self.scan_result.total_count}")
    self.ui.label_stats_all.setStyleSheet("font-weight:600")


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
    login_headers, entrance_headers, combined_headers = _build_combined_headers(result)

    wb = Workbook()

    # убираем дефолтный лист
    wb.remove(wb.active)

    def fill_sheet(title, entries):
        ws = wb.create_sheet(title)
        ws.append(combined_headers)

        # ставим ширину столбцов
        for col_idx, header in enumerate(combined_headers, start=1):
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = max(15, len(str(header)) + 2)

        for entry in entries:
            for row in _iter_joined_rows(entry, login_headers, entrance_headers, combined_headers):
                ws.append(row)

    fill_sheet("Утечки", result.compromised)
    fill_sheet("Нет входа", result.no_login)
    fill_sheet("Сопоставлено", result.matched)

    wb.save(path)
