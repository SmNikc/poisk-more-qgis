"""Dialog window for creating SITREP reports.

The original file accidentally contained the text ``CopyEdit`` as executable
code on the first line which caused a ``NameError`` during plugin import.  QGIS
attempts to load this module when the plugin is initialised, so the stray text
prevented the whole plugin from starting.  The line has been removed and a
short module level docstring added instead."""

from PyQt5.QtWidgets import QDialog, QMessageBox
from ..forms.SitrepForm_ui import Ui_SitrepForm
from ..utils.report_generator import generate_sitrep_docx
from ..utils.sru_aircraft import SRUAircraftManager
class SitrepDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SitrepForm()
        self.ui.setupUi(self)
        self.ui.buttonSend.clicked.connect(self.on_send)
    def on_send(self):
        data = {
            "category": self.ui.comboCategory.currentText(),
            "datetime": self.ui.dateTimeUtc.dateTime().toString(),
            "from": self.ui.editFrom.text(),
            "to": self.ui.editTo.text(),
            "object": self.ui.editObject.text(),
            "location": self.ui.editLocation.text(),
            "lat": self.ui.editLat.text(),
            "lon": self.ui.editLon.text(),
            "situation": self.ui.textSituation.toPlainText(),
            "weather": self.ui.textWeather.toPlainText(),
            "search_area": self.ui.textSearchArea.toPlainText(),
            "mmsi": self.ui.editMMSI.text(),
            "size": self.ui.editSize.text(),
        }
        sru_manager = SRUAircraftManager()
        out_docx = "SITREP.docx"
        generate_sitrep_docx(data, out_docx, sru_manager=sru_manager)
#         QMessageBox.information(self, "SITREP", f"SITREP сгенерирован: {out_docx}")
        self.accept()
