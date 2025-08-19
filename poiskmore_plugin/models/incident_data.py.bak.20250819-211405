from dataclasses import dataclass
from typing import Optional, List
from qgis.core import QgsFeature
@dataclass
class IncidentData:
    id: str = ""
    operation_id: str = ""
    name: str = ""
    description: str = ""
    def to_qgs_feature(self) -> QgsFeature:
        feature = QgsFeature()
        feature.setAttribute("name", self.name)
        return feature