import pytest
from ..controllers.probability_generator import generate_probability_points, calculate_drift
from qgis.core import QgsPointXY
import math

def test_drift_calculation():
    new_lat, new_lon = calculate_drift(60, 30, 6, 45, 2)
    assert pytest.approx(new_lat, 0.001) == 60.008
    assert pytest.approx(new_lon, 0.001) == 30.016

def test_point_generation_with_drift():
    center = QgsPointXY(30, 60)
    points = generate_probability_points(center, 1.0, 10, wind_speed_ms=6, wind_dir_deg=45, time_hours=2)
    assert len(points) == 10
    drifted_center = calculate_drift(60, 30, 6, 45, 2)
    for f in points:
        pt = f.geometry().asPoint()
        dx = pt.x() - drifted_center[1]
        dy = pt.y() - drifted_center[0]
        assert math.sqrt(dx**2 + dy**2) <= 1.0 + 0.01