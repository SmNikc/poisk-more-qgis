python from PyQt5.QtWidgets import QDialog, QMessageBox from PyQt5 import uic import os from .alg.alg_zone import create_search_zone
class SearchAreaDialog(QDialog): def init(self, parent=None): super().init(parent) uic.loadUi(os.path.join(os.path.dirname(file), '../forms/SearchAreaForm.ui'), self)
self.buttonGenerate.clicked.connect(self.generate_area)
def generate_area(self): type = self.comboType.currentText() center = self.editCenter.text() if not center: QMessageBox.warning(self, "Ошибка", "Центр обязателен") return
# zone = create_search_zone(type, center) QMessageBox.information(self, "Успех", f"Район поиска {type} сгенерирован")
