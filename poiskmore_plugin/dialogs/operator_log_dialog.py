from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
import os

class OperatorLogDialog(QDialog):
    def __init__(self, path="operator_log.txt"):
        super().__init__()
        self.setWindowTitle("Журнал действий оператора")
        self.layout = QVBoxLayout()
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.layout.addWidget(self.text)
        self.reload_button = QPushButton("Обновить")
        self.reload_button.clicked.connect(self.load_log)
        self.layout.addWidget(self.reload_button)
        self.setLayout(self.layout)
        self.path = path
        self.load_log()

    def load_log(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.text.setText(f.read())
        else:
            self.text.setText("Лог-файл не найден.")