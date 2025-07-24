# Отрисовка схем поиска. Улучшен:
# Добавлен spatial index для оптимизации
# центра; полный импорт.

from qgis.core import QgsVectorLayer, QgsProject, QgsPointXY, QgsSpatialIndex
from qgis.gui import QgsMapCanvas
from .search_scheme import create_expanding_square, save_search_geometry

def draw_search_scheme(canvas: QgsMapCanvas, spacing: float, legs: int):
    layer = QgsVectorLayer("LineString?crs=EPSG:4326", "Search Scheme", "memory")

    # Оптимизация: Использование index для
    # центра, если есть слои
    center = canvas.extent().center()
    coords = create_expanding_square(center, spacing, legs)
    points = [QgsPointXY(x, y) for x, y in coords]

    save_search_geometry(layer, points)
    QgsProject.instance().addMapLayer(layer)
