import os
import sys
from qgis.core import QgsApplication

# Initialize QGIS for tests
qgs = QgsApplication([], False)
qgs.initQgis()

# Add plugin root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
