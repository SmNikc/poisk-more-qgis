python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
from modules.db_interface import DBInterface
from qgis.core import QgsMessageLog, Qgis

class DatabaseConnectionForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/DatabaseConnectionForm.ui"), self)

        self.buttonConnect.clicked.connect(self.connect_db)

    def connect_db(self):
        try:
            host = self.dbHost.text()
            port = self.dbPort.value()
            user = self.dbUser.text()
            password = self.dbPassword.text()
            db_name = self.dbName.text()

            conn_string = f"host={host} port={port} user={user} password={password} dbname={db_name}"
            db = DBInterface(db_type='postgres', conn_string=conn_string)
            if db.conn:
                QgsMessageLog.logMessage("Подключение к PostgreSQL успешно", "Поиск-Море", Qgis.Info)
                QMessageBox.information(self, "Успех", "Подключено к БД.")
            else:
                raise Exception("Ошибка подключения")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения: {str(e)}")