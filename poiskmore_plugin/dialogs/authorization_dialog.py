from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QComboBox,
)


class AuthorizationDialog(QDialog):
    """Простое диалоговое окно авторизации."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")

        self._login_edit = QLineEdit(self)
        self._profile_combo = QComboBox(self)
        self._profile_combo.addItems(["Оператор", "Администратор"])

        layout = QFormLayout(self)
        layout.addRow("Логин:", self._login_edit)
        layout.addRow("Профиль:", self._profile_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_user_data(self):
        """Возвращает введенные данные пользователя или None."""
        login = self._login_edit.text().strip()
        profile = self._profile_combo.currentText().strip()
        if login and profile:
            return {"login": login, "profile": profile}
        return None

