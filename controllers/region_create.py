# Создание регионов с интеграцией ESB. Улучшен: Отправка данных региона через ESB после создания.

from qgis.core import QgsVectorLayer
from qgis.core import QgsFeature
from qgis.core import QgsGeometry
from qgis.core import QgsField
from qgis.core import QgsProject
from PyQt5.QtCore import QVariant
from ..esb.esb_integration import send_message_via_esb

def create_region(name, start_time, daylight_duration):
    layer = QgsVectorLayer("Polygon?crs=EPSG:4326", name, "memory")
    pr = layer.dataProvider()
    pr.addAttributes([
        QgsField("name", QVariant.String),
        QgsField("start_time", QVariant.String),
        QgsField("daylight", QVariant.Double)
    ])
    layer.updateFields()

    feature = QgsFeature()
    geom = QgsGeometry.fromRect(QgsProject.instance().mapSettings().extent())
    feature.setGeometry(geom)
    feature.setAttributes([name, start_time, daylight_duration])
    pr.addFeature(feature)
    layer.updateExtents()
    QgsProject.instance().addMapLayer(layer)

    # Отправка через ESB
    data = {"name": name, "start_time": start_time, "daylight": daylight_duration}
    send_message_via_esb({"type": "REGION_CREATED", "data": data})

    return layer