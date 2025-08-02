from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from qgis.core import QgsGeometry, QgsProject, QgsVectorLayer, QgsFeature

class SearchAreaForm(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms/SearchAreaForm.ui", self)
        self.buttonBuild.clicked.connect(self.build_search_area)

    def build_search_area(self):
        # Пример логики: создание простой зоны поиска (buffer вокруг точки; расширьте по IAMSAR)
        # Предполагаем LKP (Last Known Position) как (0,0) для теста
        lkp = QgsGeometry.fromPointXY(QgsPointXY(0, 0))
        radius = 1.0  # Пример радиуса в км (используйте данные формы)
        zone_geom = lkp.buffer(radius, 12)  # Буфер по IAMSAR (сегменты для сглаживания)
        
        # Создание слоя в QGIS
        layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "Search Area", "memory")
        pr = layer.dataProvider()
        feat = QgsFeature()
        feat.setGeometry(zone_geom)
        pr.addFeatures([feat])
        QgsProject.instance().addMapLayer(layer)
        
        print("Район поиска построен и добавлен как слой в QGIS.")
        self.accept()  # Закрытие формы после построения