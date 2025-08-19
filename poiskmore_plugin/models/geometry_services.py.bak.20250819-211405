from qgis.core import QgsCoordinateReferenceSystem, QgsGeometry
class GeometryServices:
    def __init__(self):
        self.crs = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS84 по умолчанию
    def create_crs(self, init_str: str) -> QgsCoordinateReferenceSystem:
        crs = QgsCoordinateReferenceSystem()
        crs.createFromString(init_str)
        return crs if crs.isValid() else None