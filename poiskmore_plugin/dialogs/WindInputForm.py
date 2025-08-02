from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
import math

class WindInputForm(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms/WindInputForm.ui", self)
        self.buttonCalc.clicked.connect(self.calculate_asw)
        # Список периодов (расширьте для таблицы ввода нескольких периодов)
        self.wind_data = []  # Список tuples (dir_deg, speed_ms)

    def calculate_asw(self):
        # Сбор данных с формы (пример для одного периода; для нескольких — цикл по таблице)
        dir_deg = self.spinDir.value()
        speed_ms = self.spinSpeed.value()
        self.wind_data.append((dir_deg, speed_ms))
        
        # Расчёт ASW по IAMSAR: векторное среднее (sum V * cos(dir) / n для x, sum V * sin(dir) / n для y)
        sum_x = 0
        sum_y = 0
        n = len(self.wind_data)
        for d, v in self.wind_data:
            rad = math.radians(d)  # Градусы в радианы
            sum_x += v * math.cos(rad)
            sum_y += v * math.sin(rad)
        
        if n > 0:
            avg_x = sum_x / n
            avg_y = sum_y / n
            asw_speed_knots = math.sqrt(avg_x**2 + avg_y**2) * 1.94384  # м/с в узлы
            asw_dir = (math.degrees(math.atan2(avg_y, avg_x)) + 360) % 360
            self.spinASWSpeed.setValue(asw_speed_knots)
            self.spinASWDir.setValue(asw_dir)
            self.spinASWDe.setValue(0.3)  # Пример значения из скриншота
            self.tabWidget.setCurrentIndex(1)  # Переход к состоянию №2
        else:
            print("Нет данных для расчёта")