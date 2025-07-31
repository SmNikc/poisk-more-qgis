# dialogs/splash_dialog.py
from PyQt5.QtWidgets import QDialog, QLabel
from PyQt5.QtCore import Qt, QTimer
from qgis.PyQt import uic
import os

class SplashDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.SplashScreen | Qt.FramelessWindowHint)
        # Подгружаем UI, если сделали .ui форму, иначе создаём QLabel
        lbl = QLabel(self)
        pix = QPixmap(os.path.join(os.path.dirname(__file__), "../resources/splash.png"))
        lbl.setPixmap(pix)
        lbl.setAlignment(Qt.AlignCenter)
        self.setFixedSize(pix.size())
        # Закрываем через 3 секунды
        QTimer.singleShot(3000, self.accept)