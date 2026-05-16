#!/usr/bin/env python3
import json
import os
import sys
from PyQt5.QtWidgets import QApplication, QGraphicsDropShadowEffect, QLabel, QMenu, QSystemTrayIcon, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QPainter
from datetime import datetime

CONFIG_PATH = os.path.expanduser("~/.config/steam-deck-clock.json")


class Clock(QWidget):
    def __init__(self):
        super().__init__()
        self._drag_pos = None
        self._config = self._load_config()
        self._use_24h = self._config.get("use_24h", True)
        self._init_ui()
        self._init_tray()
        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(1000)
        self._tick()

    def _load_config(self):
        try:
            with open(CONFIG_PATH) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_config(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump({"x": self.x(), "y": self.y(), "use_24h": self._use_24h}, f)

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
        self.move(self._config.get("x", 40), self._config.get("y", 40))

    def _init_tray(self):
        self._tray = QSystemTrayIcon(QIcon.fromTheme("clock"), self)
        self._tray.setToolTip("Steam Deck Clock")
        menu = QMenu()
        self._show_action = menu.addAction("Show")
        self._show_action.setCheckable(True)
        self._show_action.setChecked(True)
        self._show_action.triggered.connect(self._toggle_visibility)
        menu.addSeparator()
        self._24h_action = menu.addAction("24-hour clock")
        self._24h_action.setCheckable(True)
        self._24h_action.setChecked(self._use_24h)
        self._24h_action.triggered.connect(self._toggle_24h)
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

    def _toggle_24h(self, checked):
        self._use_24h = checked
        self._save_config()
        self._tick()  # update display immediately

    def _tray_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # single left-click
            self._toggle_visibility()

    def _tick(self):
        now = datetime.now()
        if self._use_24h:
            self.time_label.setText(now.strftime("%H:%M:%S"))
        else:
            time_str = now.strftime("%I:%M:%S")
            ampm = now.strftime("%p")
            self.time_label.setText(
                f'{time_str} <span style="font-size:20pt; font-weight:bold;">{ampm}</span>'
            )
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
            self._save_config()  # remember new position

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
