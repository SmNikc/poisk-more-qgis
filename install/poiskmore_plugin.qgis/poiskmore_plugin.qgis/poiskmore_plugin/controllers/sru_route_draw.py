# Отрисовка маршрутов SRU. Улучшен:
# Проверка на пустой маршрут.

from qgis.core import QgsProject, QgsVectorLayer
from .sru_routing import calculate_sru_route, add_route_to_layer
from PyQt5.QtWidgets import QMessageBox

def draw_route(canvas, start, end):
    route = calculate_sru_route(start, end)
    if not route:
        QMessageBox.warning(canvas.parent(), "Ошибка", "Маршрут пустой!")
        return

    layer = QgsVectorLayer("LineString?crs=EPSG:4326", "SRU Route", "memory")
    add_route_to_layer(layer, route)
    QgsProject.instance().addMapLayer(layer)
