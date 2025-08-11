from PyQt5.QtWidgets import QDialog, QComboBox, QPushButton, QVBoxLayout, QLabel
class DialogStandardForms(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Стандартные формы:"))
self.form_type = QComboBox()
self.form_type.addItems(["Form1", "Form2"])
layout.addWidget(self.form_type)
btn = QPushButton("Открыть")
btn.clicked.connect(self.open_form)
layout.addWidget(btn)
def open_form(self):
self.accept()