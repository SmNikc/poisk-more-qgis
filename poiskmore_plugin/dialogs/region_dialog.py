from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
import os
from qgis.core import QgsMapCanvas
class RegionDialog(QDialog):
def init(self, iface, canvas: QgsMapCanvas):
super().init()
uic.loadUi(os.path.join(os.path.dirname(file), '../forms/RegionForm.ui'), self)  # Assuming form
self.canvas = canvas