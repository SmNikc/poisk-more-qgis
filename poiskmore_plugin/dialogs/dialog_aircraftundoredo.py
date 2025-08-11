from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout
class DialogAircraftUndoRedo(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
btn_undo = QPushButton("Undo")
btn_redo = QPushButton("Redo")
layout.addWidget(btn_undo)
layout.addWidget(btn_redo)