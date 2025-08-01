python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime

class GMSKCCenterReportForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/GMSKCCenterReportForm.ui"), self)

        self.buttonGenerate.clicked.connect(self.generate_report)

    def generate_report(self):
        try:
            period = self.reportPeriod.currentText()
            content = self.reportContent.toPlainText()

            pdf_path = QFileDialog.getSaveFileName(self, "Сохранить отчёт", "", "PDF (*.pdf)")[0]
            if not pdf_path:
                return

            c = canvas.Canvas(pdf_path, pagesize=letter)
            y = 750
            c.drawString(100, y, f"Отчёт для ГМСКЦ: {period}")
            y -= 20
            c.drawString(100, y, f"Дата: {datetime.datetime.now().strftime('%Y-%m-%d')}")
            y -= 20
            c.drawString(100, y, f"Содержание: {content}")
            c.save()

            QMessageBox.information(self, "Успех", f"Отчёт сохранён: {pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации: {str(e)}")