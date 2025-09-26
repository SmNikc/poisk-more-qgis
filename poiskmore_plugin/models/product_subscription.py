class ProductSubscription:
def __init__(self):
self.product_id = 0
self.forecast_period = 0
self.forecast_step = 0
self.objects = []
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