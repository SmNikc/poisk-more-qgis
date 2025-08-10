python

Свернуть

Перенос

Исполнить

Копировать
import pytest
from PyQt5.QtWidgets import QApplication
from ..dialogs.dialog_reportgeneration import ReportGenerationForm, ReportPDFTask, ReportGeoJSONTask
import os

@pytest.fixture
def app():
    return QApplication([])

def test_report_pdf(app):
    form = ReportGenerationForm()
    task = ReportPDFTask("Тест", "Test Op", "2025-06-12", "2025-06-13", "SRU1", "Results", "Conclusion", form)
    assert task.run() is True
    assert task.pdf_path is not None
    assert os.path.exists(task.pdf_path)

def test_report_geojson(app):
    form = ReportGenerationForm()
    task = ReportGeoJSONTask("Тест", form)
    assert task.run() is True
    assert task.geojson_path is not None
    assert os.path.exists(task.geojson_path)