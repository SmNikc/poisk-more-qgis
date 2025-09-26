import os
from xml.etree import ElementTree as ET
class SentRequest:
def __init__(self):
self.requests = []
@property
def requests(self):
return self._requests
@requests.setter
def requests(self, value):
self._requests = value