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


    def get_data(self):
        """
        Получить данные из формы
        
        Returns:
            dict: Словарь с данными формы
        """
        # Автоматически добавленный метод
        # TODO: Реализовать сбор данных из полей формы
        try:
            return self.collect_data()
        except AttributeError:
            # Если collect_data не реализован, возвращаем пустой словарь
            data = {}
            
            # Попытка собрать данные из стандартных виджетов
            for attr_name in dir(self):
                if attr_name.startswith("txt_") or attr_name.startswith("spin_") or attr_name.startswith("cmb_"):
                    try:
                        widget = getattr(self, attr_name)
                        if hasattr(widget, "text"):
                            data[attr_name] = widget.text()
                        elif hasattr(widget, "value"):
                            data[attr_name] = widget.value()
                        elif hasattr(widget, "currentText"):
                            data[attr_name] = widget.currentText()
                        elif hasattr(widget, "toPlainText"):
                            data[attr_name] = widget.toPlainText()
                    except:
                        pass
            
            return data

    def collect_data(self):
        """
        Собрать данные из полей формы
        
        Returns:
            dict: Словарь с данными формы
        """
        data = {}
        
        # TODO: Реализовать сбор данных из конкретных полей
        # Пример:
        # if hasattr(self, "txt_name"):
        #     data["name"] = self.txt_name.text()
        
        return data
