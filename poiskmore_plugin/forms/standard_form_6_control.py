from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QLabel
class StandardForm6Control(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel("Standard Form 6 Control")
        layout.addWidget(self.label)
    def set_standard_form_6_binding_source(self, source):
        self.label.setText(str(source))