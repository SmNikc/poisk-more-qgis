from qgis.PyQt.QtWidgets import QDialog, QPushButton, QVBoxLayout
class OperationCreateForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.create_operation_button = QPushButton("Create Operation")
        self.button_create_case_sitrep = QPushButton("Create Case Sitrep")
        layout.addWidget(self.create_operation_button)
        layout.addWidget(self.button_create_case_sitrep)