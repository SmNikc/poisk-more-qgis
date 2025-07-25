from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QTextEdit, QPushButton, QFileDialog, QDateTimeEdit, QMessageBox
)
from PyQt5.QtCore import QDateTime
from ..reports.sitrep_generator import generate_sitrep_pdf
from ..reports.sitrep_generator_docx import generate_sitrep_docx

class SitrepDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.setWindowTitle("Донесение SITREP")
        self.iface = iface

        layout = QVBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["INITIAL", "AMPLIFYING", "FINAL"])
        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.sru_edit = QLineEdit()
        self.zone_edit = QLineEdit()
        self.notes_edit = QTextEdit()

        layout.addWidget(QLabel("Тип донесения:"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("Дата и время:"))
        layout.addWidget(self.datetime_edit)
        layout.addWidget(QLabel("SRU:"))
        layout.addWidget(self.sru_edit)
        layout.addWidget(QLabel("Зона поиска:"))
        layout.addWidget(self.zone_edit)
        layout.addWidget(QLabel("Дополнительно:"))
        layout.addWidget(self.notes_edit)

        button_layout = QHBoxLayout()
        generate_pdf_btn = QPushButton("PDF")
        generate_pdf_btn.clicked.connect(self.generate_pdf)
        generate_docx_btn = QPushButton("DOCX")
        generate_docx_btn.clicked.connect(self.generate_docx)
        button_layout.addWidget(generate_pdf_btn)
        button_layout.addWidget(generate_docx_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def generate_pdf(self):
        try:
            data = {
                "type": self.type_combo.currentText(),
                "datetime": self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
                "sru": self.sru_edit.text(),
                "zone": self.zone_edit.text(),
                "notes": self.notes_edit.toPlainText()
            }
            if not all(data.values()):
                raise ValueError("Заполните все обязательные поля!")
            generate_sitrep_pdf(data)
            QMessageBox.information(self, "Готово", "Файл PDF успешно создан.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def generate_docx(self):
        try:
            data = {
                "type": self.type_combo.currentText(),
                "datetime": self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
                "sru": self.sru_edit.text(),
                "zone": self.zone_edit.text(),
                "notes": self.notes_edit.toPlainText()
            }
            if not all(data.values()):
                raise ValueError("Заполните все обязательные поля!")
            generate_sitrep_docx(data)
            QMessageBox.information(self, "Готово", "Файл DOCX успешно создан.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))