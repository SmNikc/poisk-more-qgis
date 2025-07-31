python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QFileDialog, QMessageBox
import os
from qgis.core import QgsMessageLog, Qgis

class SystemLogForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/SystemLogForm.ui"), self)

        self.buttonExport.clicked.connect(self.export_log)

        self.load_log()

    def load_log(self):
        # Пример загрузки логов (из QgsMessageLog или файла)
        logs = [
            ("2025-06-12 10:00", "Info", "Плагин запущен"),
            ("2025-06-12 10:05", "Error", "Ошибка расчёта")
        ]
        self.logTable.setRowCount(len(logs))
        for row, (time, level, msg) in enumerate(logs):
            self.logTable.setItem(row, 0, QTableWidgetItem(time))
            self.logTable.setItem(row, 1, QTableWidgetItem(level))
            self.logTable.setItem(row, 2, QTableWidgetItem(msg))

    def export_log(self):
        try:
            path = QFileDialog.getSaveFileName(self, "Экспорт лога", "", "Text (*.txt)")[0]
            if path:
                with open(path, 'w', encoding='utf-8') as f:
                    for row in range(self.logTable.rowCount()):
                        time = self.logTable.item(row, 0).text()
                        level = self.logTable.item(row, 1).text()
                        msg = self.logTable.item(row, 2).text()
                        f.write(f"{time} [{level}] {msg}\n")
                QMessageBox.information(self, "Успех", f"Лог экспортирован: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")