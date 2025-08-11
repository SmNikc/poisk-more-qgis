import pytest
from ..alg.alg_drift import calculate_drift
from qgis.core import QgsPointXY


def test_drift_calculation():
    start = QgsPointXY(0, 0)
    result = calculate_drift(start, 30, 10, 45, 2, 3)
    # Проверка на положительный сдвиг по оси X
    assert result.x() > start.x()
