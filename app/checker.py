from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from openpyxl import load_workbook

from app.utils import clean_str, match_pattern


class CheckerConfig:
    def __init__(self, logins_table_path: str, entrances_table_path: str, exceptions_table_path: str, fired_list_path: str):
        self.logins_table_path = logins_table_path
        self.entrances_table_path = entrances_table_path
        self.exceptions_table_path = exceptions_table_path
        self.fired_list_path = fired_list_path

class CheckerResult:
    def __init__(self, compromised, matched, no_login, exceptions):
        self.compromised = compromised
        self.matched = matched
        self.no_login = no_login
        self.exceptions = exceptions

        self.compromised_count = len(compromised)
        self.matched_count = len(matched)
        self.no_login_count = len(no_login)
        self.exceptions_count = len(exceptions)
        self.total_count = (self.compromised_count + self.no_login_count + self.matched_count + self.exceptions_count)


class CheckerSignals(QObject):
    finished = pyqtSignal()
    stats = pyqtSignal(int, int) # Проверенный, всего
    error = pyqtSignal(str)
    result = pyqtSignal(object)

    def __init__(self):
        super().__init__()


class Checker(QRunnable):
    def __init__(self, config: CheckerConfig):
        super().__init__()
        self.config = config
        self.signals = CheckerSignals()

    @pyqtSlot()
    def run(self):
        pass