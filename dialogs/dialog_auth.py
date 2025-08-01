"""Диалог авторизации пользователя."""

from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic
import os

from ..utils.db_manager import DBManager


class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), "../forms/AuthForm.ui")
        uic.loadUi(ui_path, self)
        self.buttonLogin.clicked.connect(self.login)

    def login(self):
        user = self.editUser.text()
        password = self.editPassword.text()
        db = DBManager()
        if db.authenticate(user, password):
            QMessageBox.information(self, "Успех", "Авторизация прошла")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин/пароль")
