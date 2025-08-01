from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
import os
from ..reports.log_summary_generator import generate_log_summary

class LogSummaryDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сводка по логам оператора")
        layout = QVBoxLayout()
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)
        self.button = QPushButton("Обновить сводку")
        self.button.clicked.connect(self.update)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.update()

    def update(self):
        generate_log_summary()
        summary_path = "log_summary.txt"
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                self.text.setText(f.read())
        else:
            self.text.setText("Сводка не найдена. Проверьте генератор.")