# PyQt5, проверка размера.
from qgis.gui import QgsMapCanvas
from PyQt5.QtGui import QImage, QPainter
def save_canvas_as_image(canvas: QgsMapCanvas, path="snapshot.png"):
# size = canvas.size()
# if size.isEmpty():
# print("Ошибка: размер канваса пустой")
# return False
# image = QImage(size, QImage.Format_ARGB32)
# painter = QPainter(image)
# canvas.render(painter)
# painter.end()
# return image.save(path)