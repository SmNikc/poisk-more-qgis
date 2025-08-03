"""Диалог выбора района поиска с отображением OpenSeaMap.

Этот модуль реализует простое диалоговое окно, показывающее карту
`OpenSeaMap` в отдельном ``QgsMapCanvas``. Диалог используется из меню
плагина и позволяет пользователю визуально оценить район поиска.
"""

from __future__ import annotations

import os

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QVBoxLayout
from qgis.core import QgsRasterLayer
from qgis.gui import QgsMapCanvas


class RegionDialog(QDialog):
    """Простой диалог выбора района поиска.

    Parameters
    ----------
    iface: Optional[QgsInterface]
        Интерфейс QGIS. Сохраняется только на случай будущего
        расширения функциональности.
    parent: Optional[QWidget]
        Родительское окно.
    """

    def __init__(self, iface=None, parent=None):
        super().__init__(parent)

        # Используем существующую форму GeoMapViewerForm.ui как базовую
        ui_path = os.path.join(
            os.path.dirname(__file__), "..", "forms", "GeoMapViewerForm.ui"
        )
        uic.loadUi(ui_path, self)

        # Создаём новый canvas
        self.canvas = QgsMapCanvas(self)

        # Размещаем canvas на виджете формы (mapWidget должен быть в .ui)
        if hasattr(self, "mapWidget"):
            self.mapWidget.setLayout(QVBoxLayout())
            self.mapWidget.layout().addWidget(self.canvas)
        else:
            # Если виджета нет, добавляем в главный layout
            layout = QVBoxLayout(self)
            layout.addWidget(self.canvas)

        self.iface = iface

        # Подключаем кнопку закрытия, если есть
        if hasattr(self, "buttonClose"):
            self.buttonClose.clicked.connect(self.accept)

        # Загружаем базовую карту
        self._load_basemap()

    def _load_basemap(self) -> None:
        """Загружает слой OpenSeaMap в ``QgsMapCanvas``."""

        seamark_url = (
            "type=xyz&url=https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"
        )
        seamark = QgsRasterLayer(seamark_url, "OpenSeaMap", "wms")
        if seamark.isValid():
            # Добавляем слой только в локальный canvas, не в основной проект
            self.canvas.setLayers([seamark])
            self.canvas.setExtent(seamark.extent())
            self.canvas.zoomToFullExtent()
            self.canvas.refresh()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить слой OpenSeaMap")

