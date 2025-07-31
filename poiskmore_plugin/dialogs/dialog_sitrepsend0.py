# dialogs/dialog_sitrepsend.py
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
import os, json
from datetime import datetime
import stomp  # stomp.py

class SitrepSendForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__),
                  "../forms/SitrepSendForm.ui"), self)

        # Кнопки вкладок
        self.buttonCancel.clicked.connect(self.reject)
        self.buttonToPdf.clicked.connect(self.on_to_pdf)
        self.buttonSend.clicked.connect(self.on_send)

    def collect_data(self):
        """Собираем все поля из вкладок в словарь."""
        data = {"header": {}, "main": {}, "additional": {}}
        # — Вкладка Заголовок —
        data["header"]["category"] = self.comboCategory.currentText()
        data["header"]["timestamp"] = self.dateTimeUtc.dateTime().toString(Qt.ISODate)
        data["header"]["from"] = self.editFrom.text()
        data["header"]["profile"] = self.comboProfile.currentText()
        data["header"]["to"] = [self.listRecipients.item(i).text()
                                 for i in range(self.listRecipients.count())
                                 if self.listRecipients.item(i).checkState()]

        # — Вкладка Основная информация —
        data["main"]["object"] = self.editObject.text()
        data["main"]["callsign"] = self.editCallsign.text()
        data["main"]["location"] = self.editLocation.text()
        data["main"]["lat"] = self.spinLat.value()
        data["main"]["lat_dir"] = self.comboLatDir.currentText()
        data["main"]["lon"] = self.spinLon.value()
        data["main"]["lon_dir"] = self.comboLonDir.currentText()
        data["main"]["situation"] = self.textSituation.toPlainText()
        data["main"]["source"] = self.editSourceInfo.text()
        data["main"]["event_time"] = self.dateEventTime.dateTime().toString(Qt.ISODate)
        data["main"]["persons"] = self.spinPersons.value()
        data["main"]["assistance"] = self.textAssistance.toPlainText()

        # — Вкладки G, H/J, K/L/M/N —
        data["additional"]["G"] = {}  # заполните по аналогии
        data["additional"]["H"] = {}
        data["additional"]["J"] = {}
        klmn = {}
        klmn["K"] = self.textK.toPlainText()
        klmn["L"] = self.textL.toPlainText()
        klmn["M"] = self.textM.toPlainText()
        klmn["N"] = self.textN.toPlainText()
        data["additional"]["KLMN"] = klmn

        return data

    def on_to_pdf(self):
        """Генерация PDF отчёта."""
        try:
            data = self.collect_data()
            # TODO: используйте ReportLab или QTextDocument для PDF
            save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить PDF", "sitrep.pdf", "PDF (*.pdf)")
            if save_path:
                from reportlab.platypus import SimpleDocTemplate, Paragraph
                from reportlab.lib.styles import getSampleStyleSheet
                doc = SimpleDocTemplate(save_path)
                styles = getSampleStyleSheet()
                elems = [Paragraph(f"H:{data['header']}", styles["Normal"])]
                doc.build(elems)
                QMessageBox.information(self, "Успех", f"PDF сохранён в:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка PDF", str(e))

    def on_send(self):
        """Отправка SITREP в ActiveMQ."""
        try:
            message = self.collect_data()
            body = json.dumps(message, ensure_ascii=False)
            conn = stomp.Connection([('localhost', 61613)])
            conn.connect(wait=True)
            conn.send(destination="/queue/sitrep", body=body)
            conn.disconnect()
            QMessageBox.information(self, "Отправлено", "SITREP успешно отправлен.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка отправки", str(e))