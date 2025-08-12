"""Tools for manual construction of a search area."""

from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsGeometry, QgsPointXY, QgsWkbTypes
from qgis.PyQt.QtGui import QColor

from .alg_zone import add_search_layer


class ManualAreaTool(QgsMapTool):
    """Map tool that allows the user to digitise a polygon manually.

    The previous implementation relied solely on ``QgsMapToolEmitPoint`` and
    called the callback as soon as three points were collected.  This meant the
    user never saw the shape being drawn and the resulting geometry wasn't
    explicitly closed which led to confusing behaviour.  The updated tool uses a
    ``QgsRubberBand`` to provide visual feedback and only finalises the polygon
    when the user double‑clicks.
    """

    def __init__(self, canvas, callback):
        super().__init__(canvas)
        self.canvas = canvas
        self.callback = callback
        self.points = []
        self.rubber_band = QgsRubberBand(canvas, QgsWkbTypes.PolygonGeometry)
        self.rubber_band.setColor(QColor(255, 0, 0, 150))
        self.rubber_band.setFillColor(QColor(255, 0, 0, 40))
        self.rubber_band.setWidth(2)

    def canvasPressEvent(self, event):
        point = self.toMapCoordinates(event.pos())
        self.points.append(point)
        self.rubber_band.addPoint(point, True)
        self.rubber_band.show()

    def canvasDoubleClickEvent(self, event):
        """Finish polygon on double click."""
        if len(self.points) >= 3:
            # close ring by repeating the first point
            ring = self.points + [self.points[0]]
            polygon = QgsGeometry.fromPolygonXY([ring])
            self.callback(polygon)
        self.deactivate()

    def deactivate(self):
        """Reset temporary graphics and state."""
        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
        self.points = []
        super().deactivate()


def manual_area(iface):
    """Activate manual area drawing tool."""

    tool = ManualAreaTool(iface.mapCanvas(), add_search_layer)
    iface.mapCanvas().setMapTool(tool)
