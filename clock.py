#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication, QGraphicsDropShadowEffect, QLabel, QMenu, QSystemTrayIcon, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QColor, QIcon, QPainter, QFontDatabase
from datetime import datetime


class Clock(QWidget):
    def __init__(self):
        super().__init__()
        self._drag_pos = None
        self._init_ui()
        self._init_tray()
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

    def _init_tray(self):
        self._tray = QSystemTrayIcon(QIcon.fromTheme("clock"), self)
        self._tray.setToolTip("Steam Deck Clock")
        menu = QMenu()
        self._show_action = menu.addAction("Show")
        self._show_action.setCheckable(True)
        self._show_action.setChecked(True)
        self._show_action.triggered.connect(self._toggle_visibility)
        menu.addSeparator()
        menu.addAction("Quit", QApplication.instance().quit)
        menu.aboutToShow.connect(self._update_show_action)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._tray_clicked)
        self._tray.show()

    def _update_show_action(self):
        self._show_action.setChecked(self.isVisible())

    def _toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()

    def _tray_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # single left-click
            self._toggle_visibility()

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
            self.grabMouse()  # route all mouse events here even if cursor leaves the window

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.releaseMouse()
            self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        self.hide()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Steam Deck Clock")
    app.setQuitOnLastWindowClosed(False)  # keep running when clock is hidden to tray
    clock = Clock()
    clock.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
