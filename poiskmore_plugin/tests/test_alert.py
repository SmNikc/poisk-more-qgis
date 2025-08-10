python

Свернуть

Перенос

Исполнить

Копировать
import pytest
from PyQt5.QtWidgets import QApplication
from ..dialogs.dialog_incomingalert import IncomingAlertForm, EmailFetchTask

@pytest.fixture
def app():
    return QApplication([])

def test_alert_save(app):
    form = IncomingAlertForm()
    # Тест сохранения (mock БД)
    assert True  # Замените на реальный тест