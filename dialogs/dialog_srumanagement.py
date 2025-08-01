python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QInputDialog, QMessageBox
import os
from qgis.core import QgsMessageLog, Qgis

class SRUManagementForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/SRUManagementForm.ui"), self)

        self.buttonAdd.clicked.connect(self.add_sru)
        self.buttonRemove.clicked.connect(self.remove_sru)
        self.load_sru()

    def load_sru(self):
        # Пример загрузки из БД или файла
        sru_list = [("SRU1", "Судно", "60.0, 30.0", "Активен"), ("SRU2", "Вертолёт", "61.0, 31.0", "Неактивен")]
        self.tableSRUs.setRowCount(len(sru_list))
        for row, sru in enumerate(sru_list):
            for col, data in enumerate(sru):
                self.tableSRUs.setItem(row, col, QTableWidgetItem(data))

    def add_sru(self):
        name, ok = QInputDialog.getText(self, "Добавление SRU", "Имя SRU:")
        if ok:
            # Добавление в таблицу/БД
            row = self.tableSRUs.rowCount()
            self.tableSRUs.insertRow(row)
            self.tableSRUs.setItem(row, 0, QTableWidgetItem(name))
            self.tableSRUs.setItem(row, 1, QTableWidgetItem("Тип"))
            self.tableSRUs.setItem(row, 2, QTableWidgetItem("Координаты"))
            self.tableSRUs.setItem(row, 3, QTableWidgetItem("Статус"))
            QgsMessageLog.logMessage(f"Добавлен SRU: {name}", "Поиск-Море", Qgis.Info)

    def remove_sru(self):
        selected = self.tableSRUs.selectedRows()
        if selected:
            row = selected[0]
            name = self.tableSRUs.item(row, 0).text()
            self.tableSRUs.removeRow(row)
            QgsMessageLog.logMessage(f"Удалён SRU: {name}", "Поиск-Море", Qgis.Info)
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите SRU для удаления.")