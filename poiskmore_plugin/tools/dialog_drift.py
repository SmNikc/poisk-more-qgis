# --- FILE: tools/dialog_drift.py ---
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

class DriftCalculationDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms/DriftCalculationForm.ui", self)
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
