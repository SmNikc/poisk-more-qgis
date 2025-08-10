python

Свернуть

Перенос

Исполнить

Копировать
import pytest
from PyQt5.QtWidgets import QApplication
from ..dialogs.dialog_operatorlog import OperatorLogForm

@pytest.fixture
def app():
    return QApplication([])

def test_log_load(app):
    form = OperatorLogForm()
    assert form.operatorLogTable.rowCount() > 0  # Предполагая логи загружены