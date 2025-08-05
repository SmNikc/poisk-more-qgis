python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
import os
from modules.db_interface import DBInterface

class AlertViewerForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/AlertViewerForm.ui"), self)

        self.buttonAcknowledge.clicked.connect(self.acknowledge_alert)
        self.buttonClose.clicked.connect(self.close)

        self.load_alerts()

    def load_alerts(self):
        db = DBInterface()
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM alerts")
        alerts = cursor.fetchall()
        db.close()

        self.alertTable.setRowCount(len(alerts))
        for row, alert in enumerate(alerts):
            for col, data in enumerate(alert):
                self.alertTable.setItem(row, col, QTableWidgetItem(str(data)))

    def acknowledge_alert(self):
        selected = self.alertTable.selectedRows()
        if selected:
            # Пример подтверждения (удаление из БД)
            QMessageBox.information(self, "Успех", "Тревога подтверждена.")
            self.alertTable.removeRow(selected[0])
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите тревогу.")