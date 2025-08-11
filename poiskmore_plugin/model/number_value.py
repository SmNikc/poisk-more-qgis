class NumberValue:
def __init__(self):
self.value = 0
self.display = ""
@property
def value(self):
return self._value
@value.setter
def value(self, value):
self._value = value
@property
def display(self):
return self._display
@display.setter
def display(self, value):
self._display = value