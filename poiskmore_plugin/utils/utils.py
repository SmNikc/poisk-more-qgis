from PyQt5.QtWidgets import QMessageBox
from math import sqrt


def show_message(title: str, message: str, icon: QMessageBox.Icon = QMessageBox.Information) -> None:
    """Show a simple message box."""
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()


def calculate_distance(point1, point2) -> float:
    """Calculate Euclidean distance between two QGIS points."""
    dx = point1.x() - point2.x()
    dy = point1.y() - point2.y()
    return sqrt(dx ** 2 + dy ** 2)


def validate_coords(coords_str: str) -> bool:
    """Validate coordinate string formatted as 'lat, lon'."""
    try:
        lat, lon = map(float, coords_str.split(','))
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except Exception:
        return False