"""Диалог выбора района поиска с отображением OpenSeaMap."""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QMessageBox, QWidget, QPushButton
from PyQt5 import uic
import os
from qgis.core import QgsProject, QgsRasterLayer
from qgis.gui import QgsMapCanvas
class RegionDialog(QDialog):
    """Простой диалог выбора района поиска.
    Открывает окно с картой OpenSeaMap, позволяя пользователю визуально оценить район поиска.
    """
    def __init__(self, iface=None, parent=None):
        super().__init__(parent)
        self.iface = iface
        # Используем существующую форму GeoMapViewerForm.ui как базовую
        ui_path = os.path.join(os.path.dirname(__file__), "../forms/GeoMapViewerForm.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            # Если UI-файл не найден, создаем базовый макет
            self.setWindowTitle("Выбор района поиска")
            self.setGeometry(100, 100, 800, 600)
            main_layout = QVBoxLayout(self)
            self.mapWidget = QWidget() # Создаем заглушку для mapWidget
            main_layout.addWidget(self.mapWidget)
            self.buttonClose = QPushButton("Закрыть")
            main_layout.addWidget(self.buttonClose)
        # Создаём новый canvas
        self.canvas = QgsMapCanvas(self)
        # Размещаем canvas на виджете формы (mapWidget должен быть в .ui)
        if hasattr(self, "mapWidget") and self.mapWidget.layout() is None:
            self.mapWidget.setLayout(QVBoxLayout())
            self.mapWidget.layout().addWidget(self.canvas)
        elif hasattr(self, "mapWidget"): # Если layout уже есть, просто добавляем
            self.mapWidget.layout().addWidget(self.canvas)
        else:
            # Если виджета нет, добавляем в главный layout
            layout = QVBoxLayout(self)
            layout.addWidget(self.canvas)
        # Подключаем кнопку закрытия, если есть
        if hasattr(self, "buttonClose"):
            self.buttonClose.clicked.connect(self.accept)
        # Загружаем базовую карту
        self._load_basemap()
    def _load_basemap(self) -> None:
        """Загружает слой OpenSeaMap в canvas."""
        seamark_url = "type=xyz&url=https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"
        seamark = QgsRasterLayer(seamark_url, "OpenSeaMap", "wms")
        if seamark.isValid():
            # Добавляем слой только в локальный canvas, не в основной проект
            self.canvas.setLayers([seamark])
            self.canvas.setExtent(seamark.extent())
            self.canvas.zoomToFullExtent()
            self.canvas.refresh()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить слой OpenSeaMap")
    def get_data(self):
        """
        Получить данные из формы
        
        Returns:
            dict: Словарь с данными формы
        """
        # Автоматически добавленный метод
        # TODO: Реализовать сбор данных из полей формы
        try:
            return self.collect_data()
        except AttributeError:
            # Если collect_data не реализован, возвращаем пустой словарь
            data = {}
            
            # Попытка собрать данные из стандартных виджетов
            for attr_name in dir(self):
                if attr_name.startswith("txt_") or attr_name.startswith("spin_") or attr_name.startswith("cmb_"):
                    try:
                        widget = getattr(self, attr_name)
                        if hasattr(widget, "text"):
                            data[attr_name] = widget.text()
                        elif hasattr(widget, "value"):
                            data[attr_name] = widget.value()
                        elif hasattr(widget, "currentText"):
                            data[attr_name] = widget.currentText()
                        elif hasattr(widget, "toPlainText"):
                            data[attr_name] = widget.toPlainText()
                    except:
                        pass
            
            return data

    def collect_data(self):
        """
        Собрать данные из полей формы
        
        Returns:
            dict: Словарь с данными формы
        """
        data = {}
        
        # TODO: Реализовать сбор данных из конкретных полей
        # Пример:
        # if hasattr(self, "txt_name"):
        #     data["name"] = self.txt_name.text()
        
        return data
