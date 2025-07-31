# dialogs/dialog_sitrep.py
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
import os
import json
import stomp

class SitrepForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), "../forms/SitrepForm.ui")
        uic.loadUi(ui_path, self)

        self.buttonCancel.clicked.connect(self.reject)
        self.buttonToPdf.clicked.connect(self.on_to_pdf)
        self.buttonSend.clicked.connect(self.on_send)

    def collect_data(self):
        data = {
            "header": {
                "category": self.comboCategory.currentText(),
                "timestamp": self.dateTimeUtc.dateTime().toString("yyyy-MM-ddTHH:mm:ss"),
                "from": self.editFrom.text(),
                "profile": self.comboProfile.currentText(),
                "to": [self.listRecipients.item(i).text() for i in range(self.listRecipients.count())]
            },
            "main": {
                "object": self.editObject.text(),
                "callsign": self.editCallsign.text(),
                "location": self.editLocation.text(),
                "latitude": self.spinLat.value(),
                "lat_dir": self.comboLatDir.currentText(),
                "longitude": self.spinLon.value(),
                "lon_dir": self.comboLonDir.currentText(),
                "situation": self.textSituation.toPlainText(),
                "source_info": self.editSourceInfo.text(),
                "event_time": self.dateEventTime.dateTime().toString("yyyy-MM-ddTHH:mm:ss"),
                "persons": self.spinPersons.value(),
                "assistance": self.textAssistance.toPlainText(),
            },
            "additional": {
                "G": {},
                "H": {},
                "J": {},
                "KLMN": {}
            }
        }
        return data

    def on_to_pdf(self):
        data = self.collect_data()
        save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить PDF", "sitrep.pdf", "PDF Files (*.pdf)")
        if not save_path:
            return
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        doc = SimpleDocTemplate(save_path)
        styles = getSampleStyleSheet()
        elems = [Paragraph(json.dumps(data, indent=2, ensure_ascii=False), styles["Normal"])]
        doc.build(elems)
        QMessageBox.information(self, "Успех", f"PDF сохранён:\n{save_path}")

    def on_send(self):
        data = self.collect_data()
        body = json.dumps(data, ensure_ascii=False)
        conn = stomp.Connection([('localhost', 61613)])
        conn.connect(wait=True)
        conn.send(destination="/queue/sitrep", body=body)
        conn.disconnect()
        QMessageBox.information(self, "Отправлено", "SITREP отправлен.")