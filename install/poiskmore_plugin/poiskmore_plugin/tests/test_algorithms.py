python import pytest from alg.alg_drift import calculate_drift
def test_drift_calculation(): result = calculate_drift(60, 30, 10, 45, 2, 90, 3) assert result[0] > 60 # Проверка на положительный сдвиг