from dataclasses import dataclass
from qgis.core import QgsPointXY, QgsCoordinateReferenceSystem
@dataclass
class SarUnitInfo:
    sar_unit: object  # SarUnit из модели
    sub_region: object  # SubRegion
    iamsar_sub_region: object  # Iamsar.SubRegion
    sub_region_name: str = ""
    remaining_day_light: float = 0.0
    operation_time: float = 0.0
    possible_duration: float = 0.0
    @property
    def sub_region_corners(self) -> str:
        crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
        if self.sub_region.geometry:
            geom = self.sub_region.geometry.asPolygon()[0]  # Внешнее кольцо
            pts = [QgsPointXY(p.x(), p.y()) for p in geom]  # Упрощено
            return "\n".join([f"{pt.y():.6f}, {pt.x():.6f}" for pt in pts])
        return "---"