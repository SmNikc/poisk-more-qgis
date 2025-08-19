from dataclasses import dataclass
from typing import List, Optional
from qgis.core import QgsPointXY
@dataclass
class SIT185Message:
    mmsi: Optional[str] = None
    imo: Optional[str] = None
    call_sign: str = ""
    vessel_name: str = ""
    markers: List[QgsPointXY] = field(default_factory=list)