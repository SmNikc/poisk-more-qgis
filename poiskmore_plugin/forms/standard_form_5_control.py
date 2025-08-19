from qgis.PyQt.QtWidgets import QWidget, QTableWidget, QVBoxLayout
class StandardForm5Control(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        layout.addWidget(self.table)
    def initialize_component(self):
        self.table.setRowCount(5)
        self.table.setColumnCount(3)