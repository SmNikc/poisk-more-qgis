from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
import os
from ..reports.log_summary_generator import generate_log_summary
class LogSummaryDialog(QDialog):
def init(self, parent=None):
super().init(parent)
uic.loadUi(os.path.join(os.path.dirname(file), '../forms/LogSummaryForm.ui'), self)  # Assuming form exists
self.buttonGenerate.clicked.connect(self.generate_summary)
def generate_summary(self):
generate_log_summary()