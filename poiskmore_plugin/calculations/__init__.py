# -*- coding: utf-8 -*-
"""
Пакет расчётов Поиск‑Море (QGIS).
Собирает ключевые калькуляторы в единый экспорт.
"""
try:
    from .drift_calculator import DriftCalculator as DriftCalculatorPM
except Exception:
    # Оставляем проект работоспособным даже при временном отсутствии файла
    DriftCalculatorPM = None
