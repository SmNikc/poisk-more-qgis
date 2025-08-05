"""Диалог отображения журнала оператора."""

import os
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic

from ..utils.operator_log import log_event


class OperatorLogDialog(QDialog):
    """Простая форма отображения журнала."""

    def __init__(self, iface=None, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), "../forms/OperatorLogForm.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        log_event("Открыт журнал оператора")

