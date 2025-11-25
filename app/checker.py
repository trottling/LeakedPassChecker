from collections import defaultdict

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
        try:
            result = self._execute()
            self.signals.result.emit(result)
        except Exception as exc:
            self.signals.error.emit(str(exc))
        finally:
            self.signals.finished.emit()

    def _execute(self) -> CheckerResult:
        entrances_sheet_idx = 0
        logins_sheet_idx = 1 if self.config.entrances_table_path == self.config.logins_table_path else 0

        entrances_rows = self._read_excel(
            self.config.entrances_table_path,
            entrances_sheet_idx,
            header_hints=["дата", "отдел", "фио", "таб", "табельный"]
        )
        logins_rows = self._read_excel(
            self.config.logins_table_path,
            logins_sheet_idx,
            header_hints=["user name", "user display name"]
        )
        fired_names = self._load_clean_list(self.config.fired_list_path)
        exception_patterns = self._load_pattern_list(self.config.exceptions_table_path)

        entrances = self._group_entrances(entrances_rows)
        logins = self._group_logins(logins_rows)

        all_keys = sorted(set(entrances.keys()) | set(logins.keys()))

        compromised = []
        matched = []
        no_login = []
        exceptions = []

        total = len(all_keys)
        if total == 0:
            self.signals.stats.emit(0, 0)
            return CheckerResult(compromised, matched, no_login, exceptions)

        for idx, key in enumerate(all_keys, start=1):
            login_entries = logins.get(key, [])
            entrance_entries = entrances.get(key, [])
            payload = self._build_user_payload(key, login_entries, entrance_entries)

            if login_entries and entrance_entries:
                matched.append(payload)
            elif login_entries:
                if self._is_exception(key, payload, exception_patterns, fired_names):
                    exceptions.append(payload)
                else:
                    compromised.append(payload)
            else:
                no_login.append(payload)

            self.signals.stats.emit(idx, total)

        return CheckerResult(compromised, matched, no_login, exceptions)

    def _read_excel(self, path: str, sheet_index: int, header_hints=None):
        if not path:
            return []

        workbook = load_workbook(path, data_only=True)

        if sheet_index >= len(workbook.worksheets):
            workbook.close()
            raise ValueError("Недостаточно листов в Excel файле")

        sheet = workbook.worksheets[sheet_index]
        rows_iter = sheet.iter_rows(values_only=True)

        headers = self._locate_headers(rows_iter, header_hints or [])
        if headers is None:
            workbook.close()
            return []

        data = []
        for row in rows_iter:
            row_dict = {}
            for idx, header in enumerate(headers):
                if not header:
                    continue
                row_dict[header] = row[idx]
            data.append(row_dict)

        workbook.close()
        return data

    def _locate_headers(self, rows_iter, header_hints):
        header_hints = [hint.lower() for hint in header_hints]
        for row in rows_iter:
            normalized = []
            lowercased = []
            for cell in row:
                if cell is None:
                    normalized.append("")
                    lowercased.append("")
                    continue
                text = str(cell).strip()
                normalized.append(text)
                lowercased.append(text.lower())

            non_empty = [val for val in lowercased if val]

            if not non_empty:
                continue

            if header_hints:
                if not any(
                    any(hint in value for value in non_empty)
                    for hint in header_hints
                ):
                    continue
            else:
                if len(non_empty) < 2:
                    continue

            return [value for value in lowercased]
        return None

    def _load_clean_list(self, path: str):
        items = set()
        if not path:
            return items

        with open(path, "r", encoding="utf-8-sig") as handler:
            for line in handler:
                cleaned_line = clean_str(line) if line else ""
                if cleaned_line:
                    items.add(cleaned_line)
        return items

    def _load_pattern_list(self, path: str):
        patterns = []
        if not path:
            return patterns

        with open(path, "r", encoding="utf-8-sig") as handler:
            for line in handler:
                pattern = (line or "").strip()
                if pattern:
                    patterns.append(pattern)
        return patterns

    def _normalize_name(self, *candidates):
        for candidate in candidates:
            if candidate is None:
                continue
            text = str(candidate).strip()
            if not text:
                continue
            cleaned = clean_str(text)
            if cleaned:
                return cleaned, text
        return "", ""

    def _sanitize_dn(self, value):
        if value is None:
            return ""
        text = str(value).strip()
        if "=" in text:
            text = text.split("=", 1)[1]
        if "," in text:
            text = text.split(",", 1)[0]
        return text.strip()

    def _group_logins(self, rows):
        grouped = defaultdict(list)
        for row in rows:
            dn_value = self._sanitize_dn(row.get("user distinguish name"))
            key, original = self._normalize_name(
                row.get("user display name"),
                dn_value,
                row.get("фио"),
                row.get("user name")
            )
            if not key:
                continue

            entry = {
                "user_name": row.get("user name"),
                "client_host_name": row.get("client host name"),
                "logon_time": row.get("logon time"),
                "event_type_text": row.get("event type text"),
                "failure_reason": row.get("failure reason"),
                "message": row.get("message"),
                "user_display_name": row.get("user display name") or original,
                "department": self._get_first_value(row, "отдел", "department", "подразделение"),
                "tab_number": self._get_first_value(row, "таб. №", "табельный номер", "tabnumber", "tab number")
            }
            grouped[key].append(entry)
        return grouped

    def _group_entrances(self, rows):
        grouped = defaultdict(list)
        dept_cache = {}
        tab_cache = {}
        
        for row in rows:
            key, original = self._normalize_name(
                row.get("фио"),
                row.get("user display name")
            )
            if not key:
                continue

            department = self._get_first_value(row, "отдел", "department", "подразделение")
            tab_number = self._get_first_value(row, "таб. №", "табельный номер", "таб", "tabnumber", "tab number")
            
            if key not in dept_cache and department:
                dept_cache[key] = department
            if key not in tab_cache and tab_number:
                tab_cache[key] = tab_number

            entry = {
                "fio": original,
                "date": row.get("дата") or row.get("date"),
                "time_in": row.get("приход") or row.get("время входа") or row.get("время") or row.get("time in"),
                "time_out": row.get("уход") or row.get("время выхода") or row.get("time out"),
                "status": row.get("статус") or row.get("status"),
                "department": department or dept_cache.get(key),
                "tab_number": tab_number or tab_cache.get(key)
            }
            grouped[key].append(entry)
        return grouped

    def _build_user_payload(self, key, logins, entrances):
        fio = ""
        if entrances:
            fio = entrances[0].get("fio") or ""
        elif logins:
            fio = logins[0].get("user_display_name") or ""
        if not fio:
            fio = key

        display_name = logins[0].get("user_display_name") if logins else fio
        department = self._take_attr(logins, entrances, "department")
        tab_number = self._take_attr(logins, entrances, "tab_number")

        return {
            "key": key,
            "fio": fio,
            "user_display_name": display_name,
             "department": department,
             "tab_number": tab_number,
            "logins": logins,
            "entrances": entrances
        }

    def _is_exception(self, key, payload, patterns, fired_names):
        if self._is_fired(key, payload, fired_names):
            return True

        fio = payload.get("fio")
        display = payload.get("user_display_name")
        for pattern in patterns:
            if (fio and match_pattern(pattern, fio)) or (display and match_pattern(pattern, display)):
                return True
        return False

    def _is_fired(self, key, payload, fired_names):
        if not fired_names:
            return False
        if key in fired_names:
            return True

        fio_clean = clean_str(payload.get("fio")) if payload.get("fio") else ""
        display_clean = clean_str(payload.get("user_display_name")) if payload.get("user_display_name") else ""
        key_tokens = set(key.split()) if key else set()

        token_sets = [key_tokens]
        if fio_clean:
            token_sets.append(set(fio_clean.split()))
        if display_clean:
            token_sets.append(set(display_clean.split()))

        for fired in fired_names:
            if not fired:
                continue
            for tokens in token_sets:
                if fired in tokens:
                    return True
        return False

    def _get_first_value(self, row, *keys):
        for key in keys:
            key_lower = key.lower()
            for header, value in row.items():
                if header and key_lower in header.lower() and value:
                    return value
        return None

    def _take_attr(self, logins, entrances, attr):
        if logins:
            value = logins[0].get(attr)
            if value:
                return value
        if entrances:
            value = entrances[0].get(attr)
            if value:
                return value
        return None