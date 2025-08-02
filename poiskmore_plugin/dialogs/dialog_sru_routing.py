from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
import os
class SruRoutingDialog(QDialog):
def init(self, parent=None):
super().init(parent)
uic.loadUi(os.path.join(os.path.dirname(file), '../forms/SruRoutingForm.ui'), self)  # Assuming form