#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication, QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QColor, QPainter, QFontDatabase
from datetime import datetime


class Clock(QWidget):
    def __init__(self):
        super().__init__()
        self._drag_pos = None
        self._init_ui()
        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(1000)
        self._tick()

    def _init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(2)

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        time_font = QFont("Monospace", 52, QFont.Bold)
        self.time_label.setFont(time_font)
        self.time_label.setStyleSheet("color: white;")
        time_shadow = QGraphicsDropShadowEffect()
        time_shadow.setBlurRadius(12)
        time_shadow.setOffset(2, 2)
        time_shadow.setColor(QColor(0, 0, 0, 180))
        self.time_label.setGraphicsEffect(time_shadow)

        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignCenter)
        date_font = QFont("Monospace", 16)
        self.date_label.setFont(date_font)
        self.date_label.setStyleSheet("color: rgba(220, 220, 220, 0.9);")
        date_shadow = QGraphicsDropShadowEffect()
        date_shadow.setBlurRadius(8)
        date_shadow.setOffset(1, 1)
        date_shadow.setColor(QColor(0, 0, 0, 160))
        self.date_label.setGraphicsEffect(date_shadow)

        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)

        self.setLayout(layout)
        self.move(40, 40)

    def _tick(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%A, %B %-d %Y"))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        bg = QColor(0, 0, 0, 120)
        painter.setBrush(bg)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 14, 14)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        self.close()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Steam Deck Clock")
    clock = Clock()
    clock.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
