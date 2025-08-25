from qgis.PyQt.QtWidgets import QDialog, QLabel, QDialogButtonBox, QVBoxLayout


class EmergencyTypesDialog(QDialog):
    """Stub dialog for managing emergency types."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Типы аварийных ситуаций")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Управление типами аварий пока не реализовано."))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok, parent=self)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
