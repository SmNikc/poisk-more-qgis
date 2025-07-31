# dialogs/dialog_sitrepsend.py

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
import os
import json
import stomp

class SitrepSendForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Полный путь до .ui
        ui_path = os.path.join(os.path.dirname(__file__), "../forms/SitrepSendForm.ui")
        uic.loadUi(ui_path, self)

        # Кнопки
        self.buttonCancel.clicked.connect(self.reject)
        self.buttonToPdf.clicked.connect(self.on_to_pdf)
        self.buttonSend.clicked.connect(self.on_send)

    def collect_data(self):
        """Собираем все поля из 5 вкладок формы."""
        data = {"header": {}, "main": {}, "additional": {}}
        # Заголовок
        data["header"]["category"]  = self.comboCategory.currentText()
        data["header"]["timestamp"] = self.dateTimeUtc.dateTime().toString(Qt.ISODate)
        data["header"]["from"]      = self.editFrom.text()
        data["header"]["profile"]   = self.comboProfile.currentText()
        # Список получателей: отмеченные элементы
        to_list = []
        for i in range(self.listRecipients.count()):
            item = self.listRecipients.item(i)
            if item.checkState():
                to_list.append(item.text())
        data["header"]["to"] = to_list

        # Основная информация
        data["main"]["object"]      = self.editObject.text()
        data["main"]["callsign"]    = self.editCallsign.text()
        data["main"]["location"]    = self.editLocation.text()
        data["main"]["latitude"]    = self.spinLat.value()
        data["main"]["lat_dir"]     = self.comboLatDir.currentText()
        data["main"]["longitude"]   = self.spinLon.value()
        data["main"]["lon_dir"]     = self.comboLonDir.currentText()
        data["main"]["situation"]   = self.textSituation.toPlainText()
        data["main"]["source"]      = self.editSourceInfo.text()
        data["main"]["event_time"]  = self.dateEventTime.dateTime().toString(Qt.ISODate)
        data["main"]["persons"]     = self.spinPersons.value()
        data["main"]["assistance"]  = self.textAssistance.toPlainText()

        # Дополнительные вкладки G
        g = {}
        g["dim"]    = self.editDim.text()
        g["mmsi"]   = self.editMMSI.text()
        g["imo"]    = self.editIMO.text()
        g["hull"]   = self.editHullColor.text()
        g["super"]  = self.editSuperstructureColor.text()
        g["fuel"]   = self.editFuel.text()
        g["crew"]   = self.editCrewCount.text()
        g["contacts"]= self.editContacts.text()
        g["port"]   = self.editPort.text()
        g["onboard"]= self.editOnboardNo.text()
        g["equip"]  = [self.listEquipment.item(i).text() for i in range(self.listEquipment.count())]
        g["notes"]  = self.textGNotes.toPlainText()
        data["additional"]["G"] = g

        # H/J
        h = {}
        h["weather_source"] = self.editWeatherSource.text()
        # ... все поля H ...
        data["additional"]["H"] = h
        j = {"actions": self.textActionsJ.toPlainText()}
        data["additional"]["J"] = j

        # K/L/M/N
        klmn = {
            "K": self.textK.toPlainText(),
            "L": self.textL.toPlainText(),
            "M": self.textM.toPlainText(),
            "N": self.textN.toPlainText()
        }
        data["additional"]["KLMN"] = klmn

        return data

    def on_to_pdf(self):
        """Генерация PDF отчёта SITREP."""
        data = self.collect_data()
        save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить PDF", "sitrep.pdf", "PDF Files (*.pdf)")
        if not save_path:
            return
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            doc = SimpleDocTemplate(save_path)
            styles = getSampleStyleSheet()
            elems = []
            elems.append(Paragraph("SITREP Report", styles["Heading1"]))
            elems.append(Paragraph(json.dumps(data, ensure_ascii=False, indent=2), styles["Code"]))
            doc.build(elems)
            QMessageBox.information(self, "Успех", f"PDF сохранён:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка PDF", str(e))

    def on_send(self):
        """Отправка SITREP по ActiveMQ (STOMP)."""
        message = self.collect_data()
        body = json.dumps(message, ensure_ascii=False)
        try:
            conn = stomp.Connection([('localhost', 61613)])
            conn.connect(wait=True)
            conn.send(destination="/queue/sitrep", body=body)
            conn.disconnect()
            QMessageBox.information(self, "Отправлено", "SITREP успешно отправлен.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка отправки", str(e))