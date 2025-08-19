# --- FILE: tools/dialog_drift.py ---
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

class DriftCalculationDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms/DriftCalculationForm.ui", self)