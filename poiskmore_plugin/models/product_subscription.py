from dataclasses import dataclass
from typing import List
@dataclass
class ProductSubscription:
    product_id: int = 0
    forecast_period: int = 0
    forecast_step: int = 0
    objects: List[int] = field(default_factory=list)  # byte[] -> List[int]