Общие утилиты для плагина. Включает
функции показа сообщений, расчеты
расстояний и валидацию.
Порядок исполнения: Импортируется по
мере нужды; например, show_message()
используется для алертов в диалогах.
from PyQt5.QtWidgets import QMessageBox
from math import sqrt
def show_message(title, message, icon=QMessageBox.Information):
msg = QMessageBox()
msg.setIcon(icon)
msg.setWindowTitle(title)
msg.setText(message)
msg.exec_()
def calculate_distance(point1, point2):
dx = point1.x() - point2.x()
dy = point1.y() - point2.y()
return sqrt(dx**2 + dy**2)
def validate_coords(coords_str):
try:
lat, lon = map(float, coords_str.split(','))
return -90 <= lat <= 90 and -180 <= lon <= 180
except:
return False
