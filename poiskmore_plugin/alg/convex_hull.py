from typing import List
from qgis.core import QgsGeometry, QgsPointXY, QgsPolygon, QgsLineString, QgsPoint, QgsGeometryCollection
from qgis.PyQt.QtCore import QPointF  # Для совместимости
class ConvexHull:
    def __init__(self, pts: List[QgsPointXY], geom_factory):
        self.input_pts = self._unique_points(pts)
        self.geom_factory = geom_factory
    def _unique_points(self, pts):
        return list(set(pts))  # Удаление дубликатов
    def get_convex_hull(self) -> QgsGeometry:
        if not self.input_pts:
            return self.geom_factory.createGeometryCollection()
        if len(self.input_pts) == 1:
            return self.geom_factory.createPoint(self.input_pts[0])
        if len(self.input_pts) == 2:
            return self.geom_factory.createLineString([self.input_pts[0], self.input_pts[1]])
        sorted_pts = sorted(self.input_pts, key=lambda p: (p.x(), p.y()))
        hull = self._graham_scan(sorted_pts)
        return self._line_or_polygon(hull)
    def _graham_scan(self, pts):
        if len(pts) < 3:
            return pts
        hull = [pts[0], pts[1]]
        for pt in pts[2:]:
            while len(hull) >= 2 and self._cross_product(hull[-2], hull[-1], pt) <= 0:
                hull.pop()
            hull.append(pt)
        return hull
    def _cross_product(self, o, a, b):
        return (a.x() - o.x()) * (b.y() - o.y()) - (a.y() - o.y()) * (b.x() - o.x())
    def _line_or_polygon(self, hull):
        if len(hull) > 2:
            poly = QgsPolygon()
            poly.setExteriorRing(QgsLineString(hull + [hull[0]]))
            return QgsGeometry(poly)
        elif len(hull) == 2:
            return QgsGeometry(QgsLineString(hull))
        else:
            return QgsGeometry(QgsPoint(hull[0]))