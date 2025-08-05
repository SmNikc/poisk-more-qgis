from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
import os
class LogSummaryDialog(QDialog):
def init(self, parent=None):
super().init(parent)
uic.loadUi(os.path.join(os.path.dirname(file), '../forms/LogSummaryForm.ui'), self)  # Assuming form