from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
import math

class CurrentInputForm(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms/CurrentInputForm.ui", self)
        self.buttonCalc.clicked.connect(self.calculate_twc)
        # Список периодов (расширьте для таблицы ввода нескольких периодов)
        self.current_data = []  # Список tuples (dir_deg, speed_knots)

    def calculate_twc(self):
        # Сбор данных с формы (пример для одного периода; для нескольких — цикл по таблице)
        dir_deg = self.spinDir.value()
        speed_knots = self.spinSpeed.value()
        self.current_data.append((dir_deg, speed_knots))
        
        # Расчёт TWC по IAMSAR: векторное среднее, аналогично ASW
        sum_x = 0
        sum_y = 0
        n = len(self.current_data)
        for d, v in self.current_data:
            rad = math.radians(d)  # Градусы в радианы
            sum_x += v * math.cos(rad)
            sum_y += v * math.sin(rad)
        
        if n > 0:
            avg_x = sum_x / n
            avg_y = sum_y / n
            twc_speed_knots = math.sqrt(avg_x**2 + avg_y**2)
            twc_dir = (math.degrees(math.atan2(avg_y, avg_x)) + 360) % 360
            self.spinTWCSpeed.setValue(twc_speed_knots)
            self.spinTWCDir.setValue(twc_dir)
            self.spinHoriz.setValue(0.42)  # Пример значения из скриншота
            self.tabWidget.setCurrentIndex(1)  # Переход к состоянию №2
        else:
            print("Нет данных для расчёта")