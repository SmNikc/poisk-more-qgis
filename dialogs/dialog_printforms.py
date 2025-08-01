python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QMessageBox
import os
from modules.data_export import DataExport

class PrintFormsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/PrintFormsDialog.ui"), self)

        # Заполнение списка форм (пример)
        forms = ["SITREP", "Отчёт ПСО", "Журнал действий"]
        for form in forms:
            self.formsList.addItem(QListWidgetItem(form))

        self.buttonExportPDF.clicked.connect(self.export_pdf)
        self.buttonExportDOCX.clicked.connect(self.export_docx)
        self.buttonPrint.clicked.connect(self.print_form)

    def export_pdf(self):
        selected = self.formsList.currentItem().text()
        exporter = DataExport(os.path.expanduser("~/Desktop"))
        report_data = {"Форма": selected, "Дата": datetime.datetime.now().strftime("%Y-%m-%d")}
        exporter.export_pdf(report_data)
        QMessageBox.information(self, "Успех", f"PDF для {selected} экспортирован.")

    def export_docx(self):
        selected = self.formsList.currentItem().text()
        # Пример экспорта DOCX (используйте docx)
        from docx import Document
        doc = Document()
        doc.add_paragraph(f"Форма: {selected}")
        doc.save(os.path.expanduser("~/Desktop/form.docx"))
        QMessageBox.information(self, "Успех", f"DOCX для {selected} экспортирован.")

    def print_form(self):
        selected = self.formsList.currentItem().text()
        QMessageBox.information(self, "Печать", f"Отправка {selected} на принтер (реализуйте QPrinter).")