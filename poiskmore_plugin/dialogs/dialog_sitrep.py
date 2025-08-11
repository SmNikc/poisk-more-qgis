from PyQt5.QtWidgets import QDialog, QTextEdit, QPushButton, QVBoxLayout, QMessageBox
class SitrepDialog(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
self.report = QTextEdit()
layout.addWidget(self.report)
btn = QPushButton("Send")
btn.clicked.connect(self.send)
layout.addWidget(btn)
def send(self):
if self.report.toPlainText().strip():
self.accept()
else:
QMessageBox.warning(self, "Ошибка", "Отчет пуст")
def get_data(self):
return {'report': self.report.toPlainText()}