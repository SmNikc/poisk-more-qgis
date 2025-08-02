python

Свернуть

Перенос

Исполнить

Копировать
import pytest
from PyQt5.QtWidgets import QApplication
from dialogs.dialog_sitrep import SitrepForm, SendSitrepTask

@pytest.fixture
def app():
    return QApplication([])

def test_sitrep_send(app):
    form = SitrepForm()
    task = SendSitrepTask("Тест", {"test": "data"}, form)
    assert task.run() is True  # Предполагая успешную отправку