# dialogs/dialog_searcharea.py
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsPointXY, QgsVectorFileWriter, QgsCoordinateTransformContext
)
import os
from services.logic import build_expanding_spiral, build_sector_search

class SearchAreaForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "../forms/SearchAreaForm.ui"), self)

        # Привязка кнопок
        self.buttonCreate.clicked.connect(self.on_create)
        self.buttonExport.clicked.connect(self.on_export)

        # Заполняем типы поиска
        methods = ["Expanding Spiral", "Sector", "Parallel Sweep"]
        for m in methods:
            self.searchType.addItem(m)

        self.canvas = None  # будет передан из main plugin

        # Накопленные результаты (список списков точек)
        self.current_geoms = None

    def on_create(self):
        """Построить район поиска и отрисовать его на карте."""
        try:
            name = self.areaName.text().strip()
            prefix = self.prefix.text().strip()
            method = self.searchType.currentText()
            start_dt = self.startTime.dateTime().toPyDateTime()
            duration_hours = self.duration.value()
            sru_method = self.sruMethod.currentText()

            if not name:
                QMessageBox.warning(self, "Ошибка", "Укажите наименование района.")
                return

            # Вычисляем геометрию
            if method == "Expanding Spiral":
                geom = build_expanding_spiral(start_dt, duration_hours, sru_method)
            elif method == "Sector":
                geom = build_sector_search(start_dt, duration_hours, sru_method)
            else:
                QMessageBox.critical(self, "Ошибка", f"Метод {method} ещё не реализован.")
                return

            # Очищаем предыдущий слой (по желанию)
            QgsProject.instance().removeMapLayers([l.id() for l in QgsProject.instance().mapLayers().values()
                                                   if l.name().startswith(prefix)])

            # Создаём в памяти слой линий
            layer = QgsVectorLayer("LineString?crs=EPSG:4326", f"{prefix}_{name}", "memory")
            prov = layer.dataProvider()
            feat = QgsFeature()
            # geom — список QgsPointXY
            feat.setGeometry(QgsGeometry.fromPolylineXY(geom))
            prov.addFeatures([feat])
            layer.updateExtents()
            QgsProject.instance().addMapLayer(layer)

            # Масштабируем Canvas (если передали)
            if self.canvas:
                self.canvas.setLayers([layer])
                self.canvas.zoomToFullExtent()

            # Сохраняем текущую геометрию для экспорта
            self.current_geoms = (layer, prefix, name)

            QMessageBox.information(self, "Готово", "Район поиска построен и отрисован.")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"При построении района поиска:\n{str(e)}")

    def on_export(self):
        """Экспорт текущего района в GeoJSON."""
        if not self.current_geoms:
            QMessageBox.warning(self, "Ошибка", "Сначала постройте район поиска.")
            return

        layer, prefix, name = self.current_geoms
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить GeoJSON", f"{prefix}_{name}.geojson", "GeoJSON (*.geojson)"
        )
        if not save_path:
            return

        try:
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "GeoJSON"
            QgsVectorFileWriter.writeAsVectorFormatV2(
                layer, save_path, QgsCoordinateTransformContext(), options
            )
            QMessageBox.information(self, "Успех", f"GeoJSON сохранён в:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте:\n{str(e)}")