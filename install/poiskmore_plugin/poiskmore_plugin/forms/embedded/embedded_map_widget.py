# --- FILE: forms/embedded/embedded_map_widget.py ---
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from qgis.core import (
    QgsRasterLayer,
    QgsProject,
    QgsRectangle,
    QgsPointXY,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
)
from qgis.gui import QgsMapCanvas


class EmbeddedMapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.canvas = QgsMapCanvas(self)
        self.canvas.setCanvasColor(Qt.white)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self._init_map()

    def _init_map(self):
        """Добавление слоя OpenSeaMap и установка обзора"""
        url = "type=xyz&url=https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"
        layer = QgsRasterLayer(url, "OpenSeaMap", "wms")

        if not layer.isValid():
            print("❌ Ошибка: слой OpenSeaMap невалиден.")
            return

        QgsProject.instance().addMapLayer(layer)
        self.canvas.setLayers([layer])

        crs = QgsCoordinateReferenceSystem("EPSG:4326")
        self.canvas.setDestinationCrs(crs)

        extent = QgsRectangle(32.5, 43.5, 34.5, 45.5)  # Севастополь
        transform = QgsCoordinateTransform(
            crs,
            self.canvas.mapSettings().destinationCrs(),
            QgsProject.instance()
        )
        self.canvas.setExtent(transform.transformBoundingBox(extent))
        self.canvas.refresh()
