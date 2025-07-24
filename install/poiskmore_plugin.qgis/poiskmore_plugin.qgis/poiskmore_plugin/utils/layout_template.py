Шаблон лейаута. Исправлено: QgsLayout ->
QgsProject.layoutManager().createLayout(),
добавлен import.
from qgis.core import QgsProject, QgsLayoutItemLabel, QgsLayoutPoint
from qgis.PyQt.QtGui import QColor
def create_layout(canvas, title="Поиск-Море"):
project = QgsProject.instance()
layout = project.layoutManager().addLayout("New Layout")
layout.initializeDefaults()
label = QgsLayoutItemLabel(layout)
label.setText(title)
label.setFontColor(QColor("black"))
label.attemptMove(QgsLayoutPoint(10, 10))
layout.addLayoutItem(label)
return layout
