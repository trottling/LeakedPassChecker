import os
import sys

from PyQt6.QtWidgets import QMessageBox


def get_rel_path(data_path, slash_replace=True):
    if getattr(sys, 'frozen', False):
        try:
            base_path = sys._MEIPASS
        except Exception:
            return ""
    else:
        data_path = f"..\\assets\\{data_path}"
        base_path = os.path.dirname(os.path.abspath(__file__))


    result = os.path.join(base_path, data_path)

    if slash_replace:
        result = result.replace("\\", "/")

    return str(result)

def warn_user(title, text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.resize(500, 300)
    msg.exec()


def _build_combined_headers(result):
    """
    Формируем заголовки:
    [логины_без_User Display Name] + ["User Display Name | ФИО"] + [поля проходной без ФИО и пустых]
    """
    login_headers = result.login_headers or []
    entrance_headers = result.entrance_headers or []

    login_headers_no_display = [h for h in login_headers if h != "User Display Name"]
    entrance_headers_filtered = [h for h in entrance_headers if h not in ("ФИО", None)]

    combined = login_headers_no_display + ["User Display Name | ФИО"] + entrance_headers_filtered
    return login_headers, entrance_headers, combined


def _iter_joined_rows(entry, login_headers, entrance_headers, combined_headers):
    """
    На вход: один элемент из compromised / matched / no_matches.
    На выход: одна или несколько плоских строк под combined_headers.
    """

    logins_rows = entry.get("logins_rows") or []
    entrance_rows = entry.get("entrance_rows") or []

    # Если с одной стороны пусто, всё равно отдаём хотя бы одну строку
    if not logins_rows and not entrance_rows:
        logins_rows = [{ }]
        entrance_rows = [{ }]
    elif not logins_rows:
        logins_rows = [{ }]
    elif not entrance_rows:
        entrance_rows = [{ }]

    n = max(len(logins_rows), len(entrance_rows))

    for i in range(n):
        lrec = logins_rows[i] if i < len(logins_rows) else { }
        erec = entrance_rows[i] if i < len(entrance_rows) else { }

        row = []
        # логины без User Display Name
        for h in login_headers:
            if h == "User Display Name":
                continue
            row.append(lrec.get(h))

        # склейка имени
        display = lrec.get("User Display Name")
        fio = erec.get("ФИО")
        row.append(display or fio or entry.get("user"))

        # поля проходной без ФИО и None
        for h in entrance_headers:
            if h in ("ФИО", None):
                continue
            row.append(erec.get(h))

        # защита от рассинхрона: длина должна совпасть с combined_headers
        if len(row) < len(combined_headers):
            row += [None] * (len(combined_headers) - len(row))
        elif len(row) > len(combined_headers):
            row = row[:len(combined_headers)]

        yield row
