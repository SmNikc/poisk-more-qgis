# Отрисовка тепловой карты. Заменена
# заглушка на реальную: использование
# QgsHeatmapRenderer.

from qgis.core import QgsHeatmapRenderer, QgsStyle, QgsVectorLayer, QgsProject

def draw_heatmap(layer: QgsVectorLayer):
    renderer = QgsHeatmapRenderer()
    renderer.setRadius(5)
    renderer.setRenderQuality(3)
    renderer.setColorRamp(QgsStyle.defaultStyle().colorRamp("Reds"))
    layer.setRenderer(renderer)
    layer.triggerRepaint()
    QgsProject.instance().addMapLayer(layer)
