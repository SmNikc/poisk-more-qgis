python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QFileDialog, QMessageBox
import os

class ComponentListForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/ComponentListForm.ui"), self)

        self.buttonExportList.clicked.connect(self.export_list)

        self.load_components()

    def load_components(self):
        components = [
            ("DriftCalculation", "Расчёт дрейфа"),
            ("SearchArea", "Схемы поиска"),
            ("SITREP", "Отправка отчётов")
        ]
        self.componentTable.setRowCount(len(components))
        for row, (name, desc) in enumerate(components):
            self.componentTable.setItem(row, 0, QTableWidgetItem(name))
            self.componentTable.setItem(row, 1, QTableWidgetItem(desc))

    def export_list(self):
        try:
            path = QFileDialog.getSaveFileName(self, "Экспорт списка", "", "CSV (*.csv)")[0]
            if path:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("Компонент,Описание\n")
                    for row in range(self.componentTable.rowCount()):
                        name = self.componentTable.item(row, 0).text()
                        desc = self.componentTable.item(row, 1).text()
                        f.write(f"{name},{desc}\n")
                QMessageBox.information(self, "Успех", f"Список экспортирован: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")