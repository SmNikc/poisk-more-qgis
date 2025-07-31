python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os
import resources  # Скомпилированный resources.py

class SplashDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()
        label = QLabel(self)
        pixmap = QPixmap(":/images/splash.png")  # Из resources.qrc
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

        # Автозакрытие через 3 сек
        QTimer.singleShot(3000, self.close)