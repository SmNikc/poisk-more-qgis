from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QLabel, QMessageBox
class DialogSyncAddressBook(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Синхронизировать адресную книгу?"))
btn_yes = QPushButton("Да")
btn_yes.clicked.connect(self.sync)
layout.addWidget(btn_yes)
btn_no = QPushButton("Нет")
btn_no.clicked.connect(self.close)
layout.addWidget(btn_no)
def sync(self):
self.accept()