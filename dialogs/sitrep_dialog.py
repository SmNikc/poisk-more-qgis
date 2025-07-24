добавлена валидация.
from PyQt5.QtWidgets import (
QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
QLineEdit, QTextEdit, QPushButton, QFileDialog, QDateTimeEdit
)
from PyQt5.QtCore import QDateTime
from ..reports.sitrep_generator import generate_sitrep_pdf
from ..reports.sitrep_generator_docx import generate_sitrep_docx
from PyQt5.QtWidgets import QMessageBox
class SitrepDialog(QDialog):
def init(self, iface):
super().init()
self.setWindowTitle("Донесение SITREP")
self.iface = iface
layout = QVBoxLayout()
self.type_combo = QComboBox()
self.type_combo.addItems(["INITIAL", "AMPLIFYING", "FINAL"])
self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
self.sru_edit = QLineEdit()
self.coords_edit = QLineEdit()
self.weather_edit = QTextEdit()
self.situation_edit = QTextEdit()
self.actions_edit = QTextEdit()
self.attachment_path = QLineEdit()
self.attach_button = QPushButton("Выбрать вложение")
self.attach_button.clicked.connect(self.choose_attachment)
layout.addWidget(QLabel("Тип:")); layout.addWidget(self.type_combo)
layout.addWidget(QLabel("Дата и время:")); layout.addWidget(self.datetime_edit)
layout.addWidget(QLabel("SRU:")); layout.addWidget(self.sru_edit)
layout.addWidget(QLabel("Координаты:")); layout.addWidget(self.coords_edit)
layout.addWidget(QLabel("Погода:")); layout.addWidget(self.weather_edit)
layout.addWidget(QLabel("Ситуация:")); layout.addWidget(self.situation_edit)
layout.addWidget(QLabel("Действия:")); layout.addWidget(self.actions_edit)
layout.addWidget(QLabel("Вложение:")); layout.addWidget(self.attachment_path)
layout.addWidget(self.attach_button)
self.btn_pdf = QPushButton("PDF")
self.btn_docx = QPushButton("DOCX")
self.btn_pdf.clicked.connect(self.generate_pdf)
self.btn_docx.clicked.connect(self.generate_docx)
btns = QHBoxLayout()
btns.addWidget(self.btn_pdf)
btns.addWidget(self.btn_docx)
layout.addLayout(btns)
self.setLayout(layout)
def choose_attachment(self):
path = QFileDialog.getOpenFileName(self, "Файл")[0]
if path:
self.attachment_path.setText(path)
def collect_data(self):
data = {
"type": self.type_combo.currentText(),
"datetime": self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
"sru": self.sru_edit.text(),
"coords": self.coords_edit.text(),
"attachment": self.attachment_path.text()
}
if not data["type"] or not data["datetime"] or not data["sru"]:
QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля!")
return None
return data
def generate_pdf(self):
data = self.collect_data()
if data:
generate_sitrep_pdf(data)
def generate_docx(self):
data = self.collect_data()
if data:
generate_sitrep_docx(data)
