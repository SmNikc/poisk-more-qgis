import os
import sys

try:
    from qgis.core import QgsApplication

    qgs = QgsApplication([], False)
    qgs.initQgis()
except ImportError:
    qgs = None

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
