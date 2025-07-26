pythonimport pytest
from ..controllers.assign_sru_by_distance import calculate_distance
from qgis.core import QgsPointXY

@pytest.fixture
def points():
    return QgsPointXY(0, 0), QgsPointXY(3, 4), QgsPointXY(0, 5)

def test_distance_calculation(points):
    a, b, c = points
    assert calculate_distance(a, b) == pytest.approx(5.0, 0.001)
    assert calculate_distance(a, c) == pytest.approx(5.0, 0.001)
    assert calculate_distance(b, c) == pytest.approx(3.162, 0.001)