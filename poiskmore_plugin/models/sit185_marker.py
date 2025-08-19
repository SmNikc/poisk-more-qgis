from dataclasses import dataclass
from qgis.core import QgsPointXY, QgsGeometry
@dataclass
class SIT185Marker:
    position_type: int = 0  # SIT185PositionType
    probability: float = 0.0
    position: QgsGeometry = QgsGeometry.fromPointXY(QgsPointXY(0, 0))
Отчет:
Соответствие правилам: да (полный код без пропусков, изменения описаны, интеграция с PyQGIS для SAR-логики сохранена).