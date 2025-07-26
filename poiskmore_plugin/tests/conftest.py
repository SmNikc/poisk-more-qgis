--- FILE: poiskmore_plugin/tests/conftest.py ---
import os
import sys
from qgis.core import QgsApplication

# Инициализация QGIS
qgs = QgsApplication([], False)
qgs.initQgis()

# Добавление пути к QGIS библиотекам (если нужно)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))