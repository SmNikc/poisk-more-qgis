from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from dialogs.dialog_windinput import WindInputForm  # Импорт форм (расширьте)
from dialogs.dialog_currentinput import CurrentInputForm

class WindCurrentInputForm(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms/WindCurrentInputForm.ui", self)
        self.buttonWind.clicked.connect(self.open_wind_form)
        self.buttonCurrent.clicked.connect(self.open_current_form)

    def open_wind_form(self):
        wind_form = WindInputForm()
        wind_form.exec_()  # Модальное открытие (цепочка по CS.html)

    def open_current_form(self):
        current_form = CurrentInputForm()
        current_form.exec_()  # Модальное открытие