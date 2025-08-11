class ProductObjectItem:
def __init__(self):
self.selected = False
self.object_id = 0
self.name = ""
self.description = ""
self.download_size = 0.0
@property
def selected(self):
return self._selected
@selected.setter
def selected(self, value):
self._selected = value
@property
def object_id(self):
return self._object_id
@object_id.setter
def object_id(self, value):
self._object_id = value
@property
def name(self):
return self._name
@name.setter
def name(self, value):
self._name = value
@property
def description(self):
return self._description
@description.setter
def description(self, value):
self._description = value
@property
def download_size(self):
return self._download_size
@download_size.setter
def download_size(self, value):
self._download_size = value