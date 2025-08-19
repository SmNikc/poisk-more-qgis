from dataclasses import dataclass
from typing import List
@dataclass
class ProductSubscriptionItem:
    product_id: int = 0
    forecast_period: int = 0
    forecast_step: int = 0
    objects: List[object] = field(default_factory=list)  # ProductObjectItem[]
    product_name: str = ""
    product_description: str = ""
    @property
    def selected_layers(self) -> str:
        if self.objects:
            selected = len([o for o in self.objects if o.selected])
            return f"Selected Layers: {selected}/{len(self.objects)}"
        return "No objects"
    @property
    def load_size(self) -> float:
        if not self.objects:
            return 0.0
        selected_sizes = [o.download_size for o in self.objects if o.selected]
        return sum(selected_sizes) * self.forecast_period * (24 / self.forecast_step)