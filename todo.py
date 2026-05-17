#!/usr/bin/env python3
import re
import sys
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QPolygon

JOURNAL_PATH = "/home/deck/claude/learning-journal.md"

# Clicking a bullet cycles through these statuses in order
NEXT_STATUS = {"todo": "doing", "doing": "done", "done": "blocked", "blocked": "todo"}

STATUS_COLORS = {
    "todo":    QColor(160, 160, 160, 160),   # gray
    "doing":   QColor(255, 180, 30,  230),   # amber
    "done":    QColor(80,  210, 100, 230),   # green
    "blocked": QColor(220, 60,  60,  230),   # red
}

MARKER_TO_STATUS = {" ": "todo", "~": "doing", "x": "done", "!": "blocked"}
STATUS_TO_MARKER = {v: k for k, v in MARKER_TO_STATUS.items()}


def read_todos():
    try:
        with open(JOURNAL_PATH) as f:
            content = f.read()
    except FileNotFoundError:
        return []

    in_section = False
    todos = []
    for line in content.splitlines():
        if re.match(r"^## To Do", line):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            m = re.match(r"^- \[([ ~x!])\] (.+)", line)
            if m:
                status = MARKER_TO_STATUS.get(m.group(1), "todo")
                todos.append({"text": m.group(2), "status": status})
    return todos


def update_journal(text, old_status, new_status):
    with open(JOURNAL_PATH) as f:
        content = f.read()
    old_line = f"- [{STATUS_TO_MARKER[old_status]}] {text}"
    new_line = f"- [{STATUS_TO_MARKER[new_status]}] {text}"
    with open(JOURNAL_PATH, "w") as f:
        f.write(content.replace(old_line, new_line, 1))


class BulletWidget(QWidget):
    """Clickable diamond bullet — click to cycle through RAG statuses."""
    toggled = pyqtSignal(str)

    R = 9  # diamond radius

    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.status = status
        size = self.R * 2 + 12
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = STATUS_COLORS[self.status]
        cx, cy, r = self.width() // 2, self.height() // 2, self.R

        diamond = QPolygon([
            QPoint(cx,     cy - r),   # top
            QPoint(cx + r, cy),       # right
            QPoint(cx,     cy + r),   # bottom
            QPoint(cx - r, cy),       # left
        ])

        if self.status == "todo":
            painter.setPen(QPen(QColor(160, 160, 160, 180), 1.5))
            painter.setBrush(Qt.NoBrush)
            painter.drawPolygon(diamond)
        else:
            # Soft outer glow ring
            glow = QColor(color)
            glow.setAlpha(45)
            painter.setPen(Qt.NoPen)
            painter.setBrush(glow)
            glow_diamond = QPolygon([
                QPoint(cx,         cy - r - 4),
                QPoint(cx + r + 4, cy),
                QPoint(cx,         cy + r + 4),
                QPoint(cx - r - 4, cy),
            ])
            painter.drawPolygon(glow_diamond)
            # Filled inner diamond
            painter.setBrush(color)
            painter.drawPolygon(diamond)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.status = NEXT_STATUS[self.status]
            self.update()
            self.toggled.emit(self.status)


class ToDoItem(QWidget):
    def __init__(self, text, status, parent=None):
        super().__init__(parent)
        self.text = text
        self.status = status
        self.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 1, 0, 1)
        layout.setSpacing(10)

        self.bullet = BulletWidget(status)
        self.bullet.toggled.connect(self._on_toggle)
        layout.addWidget(self.bullet, 0, Qt.AlignVCenter)

        self.label = QLabel(text)
        self.label.setFont(QFont("Monospace", 12))
        self.label.setWordWrap(True)
        self._style_label()
        layout.addWidget(self.label, 1)

    def _style_label(self):
        styles = {
            "todo":    "color: rgba(220,220,220,220);",
            "doing":   "color: rgba(255,210,100,230);",
            "done":    "color: rgba(160,160,160,150); text-decoration: line-through;",
            "blocked": "color: rgba(230,100,100,230);",
        }
        self.label.setStyleSheet(f"background: transparent; {styles[self.status]}")

    def _on_toggle(self, new_status):
        old_status = self.status
        self.status = new_status
        self._style_label()
        update_journal(self.text, old_status, new_status)


class ToDoApp(QWidget):
    def __init__(self):
        super().__init__()
        self._drag_pos = None
        self._init_ui()
        self._refresh()

        timer = QTimer(self)
        timer.timeout.connect(self._refresh)
        timer.start(5000)

    def _init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(400)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._inner = QWidget()
        self._inner.setObjectName("inner")
        self._inner.setStyleSheet("""
            QWidget#inner { background: rgba(18, 18, 18, 215); border-radius: 14px; }
        """)

        inner_layout = QVBoxLayout(self._inner)
        inner_layout.setContentsMargins(20, 14, 20, 16)
        inner_layout.setSpacing(2)

        title = QLabel("To Do")
        title.setFont(QFont("Monospace", 15, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent; padding-bottom: 6px;")
        inner_layout.addWidget(title)

        self._list_layout = QVBoxLayout()
        self._list_layout.setSpacing(0)
        inner_layout.addLayout(self._list_layout)

        outer.addWidget(self._inner)
        self.move(460, 40)

    def _refresh(self):
        todos = read_todos()

        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not todos:
            lbl = QLabel("Nothing outstanding.")
            lbl.setStyleSheet("color: rgba(160,160,160,150); background: transparent; font-size: 12pt;")
            self._list_layout.addWidget(lbl)
            return

        for todo in todos:
            self._list_layout.addWidget(ToDoItem(todo["text"], todo["status"]))

    def paintEvent(self, event):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.grabMouse()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.releaseMouse()
            self._drag_pos = None


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Learning To Do")
    todo = ToDoApp()
    todo.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
