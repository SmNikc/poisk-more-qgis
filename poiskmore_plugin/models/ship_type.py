from dataclasses import dataclass
from typing import Optional
@dataclass
class ShipType:
    ship_type_id: str = ""
    name: str = ""
    angle: Optional[float] = None
    div: Optional[float] = None