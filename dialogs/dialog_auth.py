python from PyQt5.QtWidgets import QDialog, QMessageBox from PyQt5 import uic import os from .db_manager import DBManager
class AuthDialog(QDialog): def init(self, parent=None): super().init(parent) uic.loadUi(os.path.join(os.path.dirname(file), '../forms/AuthForm.ui'), self) self.buttonLogin.clicked.connect(self.login)
def login(self): user = self.editUser.text() password = self.editPassword.text() db = DBManager() if db.authenticate(user, password): QMessageBox.information(self, "Успех", "Авторизация прошла") self.accept() else: QMessageBox.warning(self, "Ошибка", "Неверный логин/пароль")
