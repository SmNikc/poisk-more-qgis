from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
import os
class OperatorLogDialog(QDialog):
def init(self, iface=None):
super().init()
uic.loadUi(os.path.join(os.path.dirname(file), '../forms/OperatorLogForm.ui'), self)