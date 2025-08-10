python

Свернуть

Перенос

Исполнить

Копировать
import pytest
from PyQt5.QtWidgets import QApplication
from dialogs.dialog_driftcalculation import DriftCalculationForm, DriftCalculationTask

@pytest.fixture
def app():
    return QApplication([])

def test_drift_calculation(app):
    form = DriftCalculationForm()
    task = DriftCalculationTask("Тест", 60, 30, 5, 45, 2, 90, 3, form)
    assert task.run() is True
    assert task.result is not None
    new_lat, new_lon = task.result
    assert isinstance(new_lat, float)
    assert isinstance(new_lon, float)