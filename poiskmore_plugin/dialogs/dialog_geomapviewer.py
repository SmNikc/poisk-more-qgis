python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5.QtWidgets import QDialog, QMessageBox, QVBoxLayout
from PyQt5 import uic
from qgis.gui import QgsMapCanvas
from qgis.core import QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem, QgsRasterLayer
import os

class GeoMapViewerForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/GeoMapViewerForm.ui"), self)

        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor("white")
        self.canvas.setCrsTransformEnabled(True)
        self.canvas.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

        self.mapLayout = QVBoxLayout()
        self.mapLayout.addWidget(self.canvas)
        self.mainLayout.insertLayout(1, self.mapLayout)

        self.buttonViewMap.clicked.connect(self.load_layer)
        self.layerSelector.addItem("Выберите слой...")
        self.layerSelector.addItem("Пример (harbors.geojson)")
        self.layerSelector.addItem("OpenStreetMap WMS")
        self.layerSelector.addItem("OpenSeaMap WMS")

    def load_layer(self):
        layer_name = self.layerSelector.currentText()
        if "harbors" in layer_name:
            path = os.path.join(os.path.dirname(__file__), "../samples/harbors.geojson")
            layer = QgsVectorLayer(path, "Гавани", "ogr")
            if not layer.isValid():
                QMessageBox.critical(self, "Ошибка", "Не удалось загрузить GeoJSON.")
                return
            QgsProject.instance().addMapLayer(layer)
            self.canvas.setLayers([layer])
            self.canvas.zoomToFullExtent()
        elif "OpenStreetMap WMS" in layer_name:
            uri = "url=https://ows.terrestris.de/osm/service?layers=OSM-WMS&format=image/png&crs=EPSG:3857"
            layer = QgsRasterLayer(uri, "OSM WMS", "wms")
            if not layer.isValid():
                QMessageBox.critical(self, "Ошибка", "Ошибка подключения OSM WMS.")
                return
            QgsProject.instance().addMapLayer(layer)
            self.canvas.setLayers([layer])
            self.canvas.zoomToFullExtent()
        elif "OpenSeaMap WMS" in layer_name:
            url = "type=xyz&url=https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"
            layer = QgsRasterLayer(url, "OpenSeaMap", "wms")
            if not layer.isValid():
                QMessageBox.critical(self, "Ошибка", "Ошибка подключения OpenSeaMap.")
                return
            QgsProject.instance().addMapLayer(layer)
            self.canvas.setLayers([layer])
            self.canvas.zoomToFullExtent()
        else:
            QMessageBox.warning(self, "Слой не выбран", "Выберите слой из списка.")