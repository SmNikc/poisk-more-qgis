from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsGeometry, QgsPointXY


class ManualAreaTool(QgsMapToolEmitPoint):
    """Map tool for drawing a manual search area."""

    def __init__(self, canvas, callback):
        super().__init__(canvas)
        self.points = []
        self.callback = callback

    def canvasPressEvent(self, e):
        point = self.toMapCoordinates(e.pos())
        self.points.append(point)
        if len(self.points) >= 3:
            polygon = QgsGeometry.fromPolygonXY([self.points])
            self.callback(polygon)
            self.deactivate()


def manual_area(iface):
    """Activate manual area drawing tool."""
    tool = ManualAreaTool(iface.mapCanvas(), lambda geom: add_search_layer(geom))
    iface.mapCanvas().setMapTool(tool)
