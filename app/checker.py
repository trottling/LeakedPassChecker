import os.path
import re
from dataclasses import dataclass

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from openpyxl import load_workbook


@dataclass
class Entrance:
    department: str
    fio: str
    tab_number: str


@dataclass
class Login:
    user_name: str
    client_host_name: str
    logon_time: str
    event_type_text: str
    failure_reason_text: str
    message: str
    user_display_name: str
    user_distinguish_name: str


@dataclass
class Worker:
    department: str
    name: str
    tab_number: str
    logins: list[Login]


@dataclass
class CheckerConfig:
    logins_table_path: str
    entrances_table_path: str
    exceptions_list_path: str
    fired_list_path: str


@dataclass
class CheckerResult:
    compromised: list[Worker]
    matched: list[Worker]
    no_login: list[Worker]
    exceptions: list[Worker]


class CheckerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)

    def __init__(self):
        super().__init__()


class Checker(QRunnable):
    def __init__(self, config: CheckerConfig):
        super().__init__()
        self.config = config
        self.exception_patterns: list[re.Pattern[str]] = []
        self.fired: set[str] = set()
        self.signals = CheckerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.execute()
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

    def execute(self) -> CheckerResult:
        self.load_lists()

        entrances = self.load_entrances()
        logins = self.load_logins()

        entrances_by_fio: dict[str, list[Entrance]] = { }
        for e in entrances:
            entrances_by_fio.setdefault(e.fio, []).append(e)

        logins_by_fio: dict[str, list[Login]] = { }
        for login in logins:
            fio = login.user_display_name
            logins_by_fio.setdefault(fio, []).append(login)

        compromised: list[Worker] = []
        exceptions: list[Worker] = []
        matched: list[Worker] = []
        no_login: list[Worker] = []

        all_fios = set(entrances_by_fio.keys()) | set(logins_by_fio.keys())

        for fio in all_fios:
            if len(fio) <= 1:
                fio = "ОСТАЛЬНЫЕ"

            fio_entrances = entrances_by_fio.get(fio, [])
            fio_logins = logins_by_fio.get(fio, [])

            department = fio_entrances[0].department if fio_entrances else "-"
            tab_number = fio_entrances[0].tab_number if fio_entrances else "-"

            worker = Worker(department=department, name=fio, tab_number=tab_number, logins=fio_logins)
            (worker)
            # быстрый чек "уволен" через set
            if fio in self.fired:
                exceptions.append(worker)
                continue

            has_entrance = bool(fio_entrances)
            has_login = bool(fio_logins)

            if has_login and has_entrance:
                matched.append(worker)
            elif has_login and not has_entrance:
                # Собираем поля один раз
                fields_to_check: list[str] = [worker.name, worker.department, worker.tab_number, ]
                for login in worker.logins:
                    fields_to_check.extend([login.user_name, login.client_host_name, login.user_display_name, login.user_distinguish_name, ])

                is_exception = False
                for pattern in self.exception_patterns:
                    if any(pattern.match(value) for value in fields_to_check if value):
                        is_exception = True
                        break

                if is_exception:
                    exceptions.append(worker)
                else:
                    compromised.append(worker)
            elif has_entrance and not has_login:
                no_login.append(worker)

        return CheckerResult(compromised=compromised, matched=matched, no_login=no_login, exceptions=exceptions, )

    def load_logins(self) -> list[Login]:
        wb = load_workbook(self.config.logins_table_path, data_only=True, read_only=True, )
        ws = wb.active

        expected_headers = [
            "user name",
            "client host name",
            "logon time",
            "event type text",
            "failure reason",
            "message",
            "user display name",
            "user distinguish name",
            ]

        header_row_idx = 11
        data_start_row_idx = 12

        actual_headers: list[str] = []
        for col_idx in range(1, 9):
            cell_value = ws.cell(row=header_row_idx, column=col_idx).value
            header = normalize(cell_value).lower()
            actual_headers.append(header)

        if actual_headers != expected_headers:
            raise ValueError(f"Неправильная таблица проходной\n\nExpected headers: {expected_headers}\nActual headers: {actual_headers}")

        logins: list[Login] = []

        for row in ws.iter_rows(min_row=data_start_row_idx, values_only=True):
            values = list(row[:9])

            login = Login(
                user_name=normalize(values[0]),
                client_host_name=normalize(values[1]),
                logon_time=normalize(values[2]),
                event_type_text=normalize(values[3]),
                failure_reason_text=normalize(values[4]),
                message=normalize(values[5]),
                user_display_name=clean_fio(normalize(values[6])),
                user_distinguish_name=normalize(values[7]),
                )

            # Если ФИО пустое, берём из столбца "user_distinguish_name", до первой запятой
            if login.user_display_name == "" and login.user_distinguish_name != "":
                login.user_display_name = login.user_distinguish_name.split(",", 1)[0]

            (login)
            logins.append(login)

        return logins

    def load_entrances(self) -> list[Entrance]:
        wb = load_workbook(self.config.entrances_table_path, data_only=True, read_only=True, )
        ws = wb.active

        expected_headers = [
            "дата",
            "отдел",
            "фио",
            "таб. №",
            "события",
            "события"
            ]

        header_row_idx = 7
        data_start_row_idx = 9

        actual_headers: list[str] = []
        for col_idx in range(1, 7):
            cell_value = ws.cell(row=header_row_idx, column=col_idx).value
            header = normalize(cell_value).lower()
            actual_headers.append(header)

        if actual_headers != expected_headers:
            raise ValueError(f"Неправильная таблица проходной\n\nExpected headers: {expected_headers}\nActual headers: {actual_headers}")

        entrances: list[Entrance] = []

        for row in ws.iter_rows(min_row=data_start_row_idx, values_only=True):
            department = normalize(row[1])
            fio = clean_fio(normalize(row[2]))
            tab_number = normalize(row[3])

            # пропускаем полностью пустые строки
            if not department and not fio and not tab_number:
                continue

            entrances.append(Entrance(department=department, fio=fio, tab_number=tab_number, ))

        return entrances

    def load_lists(self) -> None:
        # ФИО уволенных
        try:
            with open(self.config.fired_list_path, "r", encoding="utf-8", errors="ignore", ) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        fio = clean_fio(line)
                        self.fired.add(fio)

        except FileNotFoundError:
            pass
        except Exception as e:
            raise ValueError(f"Ошибка чтения файла с ФИО уволенных: {str(e)}")

        # Паттерны исключений
        try:
            with open(self.config.exceptions_list_path, "r", encoding="utf-8", errors="ignore", ) as f:
                self.exception_patterns = []
                for line in f:
                    raw = line.strip()
                    if not raw:
                        continue
                    try:
                        pattern = re.compile(create_pattern(raw), re.IGNORECASE)
                    except re.error as e:
                        raise ValueError(f"Ошибка в паттерне исключения '{raw}': {e}")
                    self.exception_patterns.append(pattern)
        except FileNotFoundError:
            pass
        except Exception as e:
            raise ValueError(f"Ошибка чтения файла с исключениями: {str(e)}")


def normalize(value) -> str:
    return str(value).strip() if value is not None else "-"


def clean_fio(text: str) -> str:
    # Если есть английские символы / цифры - служебный акк, не ФИО
    if re.match(r"^[a-zA-Z0-9]+$", text):
        return text

    # Ё -> Е
    text = text.replace("Ё", "Е")
    text = text.replace("ё", "е")

    # оставляем только А-Я, остальное -> пробел
    text = re.sub(r"[^А-Яа-я]", " ", text)

    # сжимаем пробелы
    text = re.sub(r"\s+", " ", text).strip()

    # всё в lower()
    text = text.lower()

    # каждое слово с заглавной
    text = " ".join(word.capitalize() for word in text.split())

    # пробелы по бокам
    text = text.strip()

    return text


def create_pattern(raw: str) -> str:
    # Преобразуем паттерн в регулярное выражение и экранируем специальные символы regex, кроме * и ?
    pattern_re = re.escape(raw)
    # Заменяем экранированные \* и \? на соответствующие regex паттерны
    pattern_re = pattern_re.replace(r"\*", ".*").replace(r"\?", ".")
    # Добавляем якоря для полного совпадения
    return f"^{pattern_re}$"
