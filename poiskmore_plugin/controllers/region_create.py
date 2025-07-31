# Создание регионов с интеграцией ESB. Улучшен: Отправка данных региона через ESB после создания.

from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsProject
from PyQt5.QtCore import QVariant
from qgis.utils import iface
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
    geom = QgsGeometry.fromRect(iface.mapCanvas().extent())
    feature.setGeometry(geom)
    feature.setAttributes([name, start_time, daylight_duration])
    pr.addFeature(feature)
    layer.updateExtents()
    QgsProject.instance().addMapLayer(layer)

    # Отправка через ESB
    data = {"name": name, "start_time": start_time, "daylight": daylight_duration}
    send_message_via_esb({"type": "REGION_CREATED", "data": data})

    return layer

class RegionCreateController:
    """Wrapper around :func:`create_region` used by dialogs."""
    def __init__(self, iface, layer_manager):
        self.iface = iface
        self.layer_manager = layer_manager

    def create_region(self, name, start_time, daylight_duration):
        """Delegate to :func:`create_region`."""
        return create_region(name, start_time, daylight_duration)