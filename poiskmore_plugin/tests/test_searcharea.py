python

Свернуть

Перенос

Исполнить

Копировать
import pytest
from PyQt5.QtWidgets import QApplication
from dialogs.dialog_searcharea import SearchAreaForm, SearchAreaTask

@pytest.fixture
def app():
    return QApplication([])

def test_search_area(app):
    form = SearchAreaForm()
    task = SearchAreaTask("Тест", "Test Area", "T", "Expanding Square", "2025-06-12 10:00:00", 6, "Manual", form)
    assert task.run() is True
    assert task.layer is not None
    assert task.layer.featureCount() == 1