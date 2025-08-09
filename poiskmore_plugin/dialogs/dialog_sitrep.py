from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
from PyQt5 import uic
import os
from reportlab.pdfgen import canvas
class SitrepDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        ui_path = os.path.join(os.path.dirname(__file__), 'dialog_sitrep.ui')
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            self.setup_ui()
        self.connect_buttons()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        lbl_date_time = QLabel("Дата / Время (UTC)*")
        self.txt_date = QLineEdit("28 июня 2025 г.")
        self.txt_time = QLineEdit("18:04")
        hbox_date = QHBoxLayout()
        hbox_date.addWidget(lbl_date_time)
        hbox_date.addWidget(self.txt_date)
        hbox_date.addWidget(self.txt_time)
        layout.addLayout(hbox_date)
        lbl_channel = QLabel("Канал координатор")
        self.cmb_channel = QComboBox()
        self.cmb_channel.addItems(["МСКЦ local", "Другое"])
        layout.addWidget(lbl_channel)
        layout.addWidget(self.cmb_channel)
        lbl_from = QLabel("От кого:")
        self.txt_from = QLineEdit("МСКЦ local")
        layout.addWidget(lbl_from)
        layout.addWidget(self.txt_from)
        lbl_to = QLabel("Кому:")
        self.txt_to = QTextEdit("ОД МСКЦ (odmsrcc@morflot.ru, od_smrcc@mors pa")
        layout.addWidget(lbl_to)
        layout.addWidget(self.txt_to)
        lbl_priority = QLabel("Приоритет:")
        self.cmb_priority = QComboBox()
        self.cmb_priority.addItems(["Срочный", "Нормальный"])
        layout.addWidget(lbl_priority)
        layout.addWidget(self.cmb_priority)
        lbl_additional = QLabel("Дополнительно:")
        self.txt_additional = QTextEdit()
        layout.addWidget(lbl_additional)
        layout.addWidget(self.txt_additional)
        self.btn_cancel = QPushButton("Отмена")
        self.btn_save_pdf = QPushButton("Сохранить PDF")
        self.btn_send = QPushButton("Отправить")
        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(self.btn_cancel)
        hbox_buttons.addWidget(self.btn_save_pdf)
        hbox_buttons.addWidget(self.btn_send)
        layout.addLayout(hbox_buttons)
        self.setLayout(layout)
    def connect_buttons(self):
        self.btn_cancel.clicked.connect(self.close)
        self.btn_save_pdf.clicked.connect(self.save_pdf)
        self.btn_send.clicked.connect(self.send_sitrep)
    def save_pdf(self):
        c = canvas.Canvas("sitrep.pdf")
        c.drawString(100, 750, f"Дата/Время: {self.txt_date.text()} {self.txt_time.text()}")
        c.save()
        QMessageBox.information(self, "Сохранено", "SITREP сохранен как sitre")
    def send_sitrep(self):
        QMessageBox.information(self, "Отправлено", "SITREP отправлен")