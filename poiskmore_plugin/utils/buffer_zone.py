from qgis.core import QgsGeometry

def create_buffer(geom: QgsGeometry, distance=0.05, segments=12):
    if not geom:
        return QgsGeometry()
    return geom.buffer(distance, segments)