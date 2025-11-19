import os
import sys

from PyQt6.QtWidgets import QMessageBox


def get_rel_path(data_path, slash_replace=True):
    if getattr(sys, 'frozen', False):
        try:
            base_path = sys._MEIPASS
        except Exception as e:
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