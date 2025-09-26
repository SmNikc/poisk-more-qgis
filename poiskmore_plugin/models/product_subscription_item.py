from model.product_object_item import ProductObjectItem
class ProductSubscriptionItem:
def __init__(self):
self.product_id = 0
self.forecast_period = 0
self.forecast_step = 0
self.objects = []
self.product_name = ""
self.product_description = ""
@property
def selected_layers(self):
selected = sum(1 for obj in self.objects if obj.selected)
total = len(self.objects)
return Resources.selected_layers_count(selected, total)
@property
def load_size(self):
if not self.objects:
return 0.0
sum_size = sum(obj.download_size for obj in self.objects if obj.selected)
return sum_size * self.forecast_period * (24 / self.forecast_step)
@property
def product_id(self):
return self._product_id
@product_id.setter
def product_id(self, value):
self._product_id = value
@property
def forecast_period(self):
return self._forecast_period
@forecast_period.setter
def forecast_period(self, value):
self._forecast_period = value
@property
def forecast_step(self):
return self._forecast_step
@forecast_step.setter
def forecast_step(self, value):
self._forecast_step = value
@property
def objects(self):
return self._objects
@objects.setter
def objects(self, value):
self._objects = value
@property
def product_name(self):
return self._product_name
@product_name.setter
def product_name(self, value):
self._product_name = value
@property
def product_description(self):
return self._product_description
@product_description.setter
def product_description(self, value):
self._product_description = value