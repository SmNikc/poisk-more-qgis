from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
class OperationEditDialog(QDialog):
def __init__(self, data, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
self.edit = QLineEdit(str(data))
layout.addWidget(self.edit)
btn = QPushButton("Save")
btn.clicked.connect(self.save)
layout.addWidget(btn)
def save(self):
if self.edit.text().strip():
self.accept()
else:
QMessageBox.warning(self, "Ошибка", "Данные не могут быть пустыми")
def get_data(self):
return self.edit.text()