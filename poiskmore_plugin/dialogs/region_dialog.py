"""Диалог выбора района поиска."""

import os
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from qgis.core import QgsMapCanvas


class RegionDialog(QDialog):
    """Простой диалог выбора района поиска."""

    def __init__(self, iface=None, canvas: QgsMapCanvas | None = None, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), "../forms/RegionForm.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)

        self.iface = iface
        self.canvas = canvas

