#!/usr/bin/env python3
import math, random, sys, re
from datetime import date, datetime
from PyQt5.QtWidgets import (QApplication, QGraphicsOpacityEffect,
    QHBoxLayout, QLabel, QMenu, QPushButton, QSystemTrayIcon, QVBoxLayout, QWidget)
from PyQt5.QtCore import (Qt, QEasingCurve, QFileSystemWatcher, QPoint,
    QPropertyAnimation, QTimer, pyqtSignal)
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPolygon

JOURNAL_PATH = "/home/deck/claude/learning-journal.md"
IDEA_COLOR   = QColor(160, 120, 255, 210)
SPARKLE_COLS = [QColor(c) for c in ["#c084fc","#818cf8","#f9a8d4","#fcd34d","#a5f3fc"]]
PARTY_COLS   = [QColor(c) for c in ["#f87171","#fbbf24","#34d399","#818cf8","#f9a8d4","#ffffff"]]


# ── Journal helpers ────────────────────────────────────────────────────────────

def _read_section(heading):
    try: lines = open(JOURNAL_PATH).read().splitlines()
    except FileNotFoundError: return []
    in_sec = False; out = []
    for line in lines:
        if re.match(rf"^## {re.escape(heading)}", line): in_sec = True; continue
        if in_sec and line.startswith("## "): break
        if in_sec: out.append(line)
    return out

def read_todos():
    out = []
    for line in _read_section("To Do"):
        m = re.match(r"^- \[([ x])\] (.+)", line)
        if m: out.append({"text": m.group(2), "done": m.group(1) == "x"})
    return out

def read_ideas():
    out = []
    for line in _read_section("Ideas"):
        m = re.match(r"^- (\d{4}-\d{2}-\d{2}) (.+)", line)
        if m: out.append({"date": m.group(1), "text": m.group(2)})
    return out

def mark_done(text):
    c = open(JOURNAL_PATH).read()
    open(JOURNAL_PATH,"w").write(c.replace(f"- [ ] {text}", f"- [x] {text}", 1))

def promote_idea(text, d):
    c = open(JOURNAL_PATH).read()
    c = c.replace(f"- {d} {text}\n", "")
    c = re.sub(r"(## To Do\n)", rf"\1- [ ] {text}\n", c)
    open(JOURNAL_PATH,"w").write(c)

def dismiss_idea(text, d):
    c = open(JOURNAL_PATH).read()
    open(JOURNAL_PATH,"w").write(c.replace(f"- {d} {text}\n", ""))

def mark_undone(text):
    c = open(JOURNAL_PATH).read()
    open(JOURNAL_PATH,"w").write(c.replace(f"- [x] {text}", f"- [ ] {text}", 1))

def age_label(ds):
    try:
        days = (date.today() - datetime.strptime(ds,"%Y-%m-%d").date()).days
        return "today" if days==0 else f"{days}d ago" if days<14 else f"{days//7}w ago"
    except ValueError: return ""

def idea_alpha(ds):
    try:
        days = (date.today() - datetime.strptime(ds,"%Y-%m-%d").date()).days
        return max(0.55, 1.0 - days/60)
    except ValueError: return 1.0


# ── Particle system ────────────────────────────────────────────────────────────

class _P:
    def __init__(self, x, y, color, vx, vy, life, size):
        self.x=x; self.y=y; self.color=color
        self.vx=vx; self.vy=vy; self.life=life; self.max_life=life; self.size=size
    def step(self): self.x+=self.vx; self.y+=self.vy; self.vy+=0.15; self.life-=1
    @property
    def alpha(self): return int(255*self.life/self.max_life)

class ParticleOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._ps=[]; self._t=QTimer(self); self._t.timeout.connect(self._tick)

    def burst(self, x, y, colors, count=24):
        for _ in range(count):
            a=random.uniform(0,math.pi*2); s=random.uniform(1.5,6.5)
            self._ps.append(_P(x,y,random.choice(colors),
                math.cos(a)*s, math.sin(a)*s-random.uniform(1,3.5),
                random.randint(35,65), random.randint(4,9)))
        self.resize(self.parent().size()); self.raise_(); self.show()
        if not self._t.isActive(): self._t.start(16)

    def _tick(self):
        for p in self._ps: p.step()
        self._ps=[p for p in self._ps if p.life>0]
        if not self._ps: self._t.stop()
        self.update()

    def paintEvent(self, event):
        if not self._ps: return
        painter=QPainter(self); painter.setRenderHint(QPainter.Antialiasing)
        for p in self._ps:
            c=QColor(p.color); c.setAlpha(p.alpha)
            painter.setPen(Qt.NoPen); painter.setBrush(c)
            painter.drawEllipse(int(p.x-p.size/2),int(p.y-p.size/2),p.size,p.size)


# ── Bullets ────────────────────────────────────────────────────────────────────

class SimpleBullet(QWidget):
    clicked = pyqtSignal()
    R = 9
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.R*2+12, self.R*2+12); self.setCursor(Qt.PointingHandCursor)
    def paintEvent(self, event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        cx,cy,r=self.width()//2,self.height()//2,self.R
        p.setPen(QPen(QColor(160,160,160,200),1.5)); p.setBrush(Qt.NoBrush)
        p.drawPolygon(QPolygon([QPoint(cx,cy-r),QPoint(cx+r,cy),QPoint(cx,cy+r),QPoint(cx-r,cy)]))
    def mousePressEvent(self, e):
        if e.button()==Qt.LeftButton: self.clicked.emit()

class SparkleBullet(QWidget):
    R=7
    def __init__(self, alpha=1.0, parent=None):
        super().__init__(parent); self._a=alpha; self.setFixedSize(self.R*2+12,self.R*2+12)
    def paintEvent(self, event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        cx,cy,r=self.width()//2,self.height()//2,self.R
        c=QColor(IDEA_COLOR); c.setAlpha(int(IDEA_COLOR.alpha()*self._a))
        pts=[QPoint(int(cx+(r if i%2==0 else r*.38)*math.cos(math.pi*i/4-math.pi/4)),
                    int(cy+(r if i%2==0 else r*.38)*math.sin(math.pi*i/4-math.pi/4)))
             for i in range(8)]
        p.setPen(Qt.NoPen); p.setBrush(c); p.drawPolygon(QPolygon(pts))


# ── To-do item ─────────────────────────────────────────────────────────────────

class ToDoItem(QWidget):
    party_at       = pyqtSignal(QPoint)
    removal_done   = pyqtSignal()
    undo_requested = pyqtSignal(str)

    _UNDO_SECS = 10

    def __init__(self, text, parent=None):
        super().__init__(parent); self.text=text
        self._countdown=0; self._countdown_timer=None; self._fade_timer=None
        self.setStyleSheet("background:transparent;")
        layout=QHBoxLayout(self); layout.setContentsMargins(0,2,0,2); layout.setSpacing(10)
        self.bullet=SimpleBullet(); self.bullet.clicked.connect(self._on_click)
        layout.addWidget(self.bullet,0,Qt.AlignVCenter)
        self.label=QLabel(text); self.label.setFont(QFont("Monospace",12))
        self.label.setWordWrap(True)
        self.label.setStyleSheet("background:transparent;color:rgba(220,220,220,220);")
        layout.addWidget(self.label,1)

    def _on_click(self): mark_done(self.text); self.play_completion()

    def play_completion(self):
        self.bullet.hide()
        tick=QLabel("✓"); tick.setFont(QFont("Monospace",16,QFont.Bold))
        tick.setStyleSheet("color:rgba(80,210,100,230);background:transparent;")
        tick.setFixedSize(30,30); tick.setAlignment(Qt.AlignCenter)
        self.layout().insertWidget(0,tick)
        self.label.setStyleSheet(
            "background:transparent;color:rgba(160,160,160,150);text-decoration:line-through;")
        self.party_at.emit(self.mapToGlobal(QPoint(self.width()//2,self.height()//2)))

        self._countdown=self._UNDO_SECS
        self._undo_btn=QPushButton(f"Undo ({self._countdown})")
        self._undo_btn.setStyleSheet(
            "QPushButton{background:rgba(200,130,20,200);border:none;border-radius:10px;"
            "color:white;font-size:9pt;font-weight:bold;padding:2px 10px;}"
            "QPushButton:hover{background:rgba(230,155,30,240);}")
        self._undo_btn.setCursor(Qt.PointingHandCursor)
        self._undo_btn.clicked.connect(self._undo)
        self.layout().addWidget(self._undo_btn, 0, Qt.AlignVCenter)

        self._countdown_timer=QTimer(self)
        self._countdown_timer.timeout.connect(self._tick_countdown)
        self._countdown_timer.start(1000)

        self._fade_timer=QTimer(self)
        self._fade_timer.setSingleShot(True)
        self._fade_timer.timeout.connect(self._start_fade)
        self._fade_timer.start(self._UNDO_SECS * 1000)

    def _tick_countdown(self):
        self._countdown -= 1
        if self._countdown > 0:
            self._undo_btn.setText(f"Undo ({self._countdown})")

    def _start_fade(self):
        if self._countdown_timer: self._countdown_timer.stop()
        if hasattr(self, "_undo_btn"): self._undo_btn.hide()
        self._fade_out()

    def _undo(self):
        if self._countdown_timer: self._countdown_timer.stop()
        if self._fade_timer: self._fade_timer.stop()
        mark_undone(self.text)
        self.undo_requested.emit(self.text)

    def _fade_out(self):
        effect=QGraphicsOpacityEffect(self); self.setGraphicsEffect(effect)
        self._opa=QPropertyAnimation(effect,b"opacity")
        self._opa.setDuration(1500); self._opa.setStartValue(1.0); self._opa.setEndValue(0.0)
        self._opa.setEasingCurve(QEasingCurve.InCubic)
        self._opa.finished.connect(self._collapse); self._opa.start()

    def _collapse(self):
        self._ha=QPropertyAnimation(self,b"maximumHeight")
        self._ha.setDuration(400); self._ha.setStartValue(self.height()); self._ha.setEndValue(0)
        self._ha.setEasingCurve(QEasingCurve.InCubic)
        self._ha.finished.connect(self.removal_done.emit); self._ha.start()


# ── Idea item ──────────────────────────────────────────────────────────────────

class IdeaItem(QWidget):
    sparkle_at = pyqtSignal(QPoint)
    promoted   = pyqtSignal()
    dismissed  = pyqtSignal()

    def __init__(self, text, idea_date, parent=None):
        super().__init__(parent); self.text=text; self.idea_date=idea_date
        alpha=idea_alpha(idea_date); self.setStyleSheet("background:transparent;")
        layout=QHBoxLayout(self); layout.setContentsMargins(0,2,0,2); layout.setSpacing(8)
        layout.addWidget(SparkleBullet(alpha),0,Qt.AlignVCenter)
        col=QVBoxLayout(); col.setSpacing(0)
        lbl=QLabel(text); lbl.setFont(QFont("Monospace",11)); lbl.setWordWrap(True)
        lbl.setStyleSheet(f"background:transparent;color:rgba(200,180,255,{int(220*alpha)});")
        col.addWidget(lbl)
        age=QLabel(age_label(idea_date)); age.setFont(QFont("Monospace",8))
        age.setStyleSheet(f"background:transparent;color:rgba(160,140,200,{int(140*alpha)});")
        col.addWidget(age); layout.addLayout(col,1)
        bs=("QPushButton{background:transparent;border:none;color:rgba(160,140,200,180);"
            "font-size:12pt;padding:0 3px;}QPushButton:hover{color:rgba(200,180,255,255);}")
        for sym,tip,slot in [("↑","Move to To Do",self._promote),("×","Dismiss",self._dismiss)]:
            b=QPushButton(sym); b.setFixedSize(24,24); b.setToolTip(tip)
            b.setStyleSheet(bs); b.clicked.connect(slot); layout.addWidget(b,0,Qt.AlignVCenter)

    def _promote(self):
        self.sparkle_at.emit(self.mapToGlobal(QPoint(self.width()//2,self.height()//2)))
        promote_idea(self.text,self.idea_date); self.promoted.emit()

    def _dismiss(self):
        dismiss_idea(self.text,self.idea_date); self.dismissed.emit()


# ── Collapsible section ────────────────────────────────────────────────────────

class CollapsibleSection(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self._collapsed = False; self._natural_h = 0
        self.setStyleSheet("background:transparent;")

        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(4)

        # Clickable header row
        hdr = QWidget(); hdr.setStyleSheet("background:transparent;")
        hdr.setCursor(Qt.PointingHandCursor)
        hdr.mousePressEvent = lambda e: self.toggle()
        hl = QHBoxLayout(hdr); hl.setContentsMargins(0,0,0,0)
        self._lbl = QLabel(title); self._lbl.setFont(QFont("Monospace",13,QFont.Bold))
        self._lbl.setStyleSheet("color:white;background:transparent;")
        self._chev = QLabel("▾"); self._chev.setFont(QFont("Monospace",14))
        self._chev.setStyleSheet("color:rgba(200,200,200,180);background:transparent;")
        hl.addWidget(self._lbl); hl.addStretch(); hl.addWidget(self._chev)
        root.addWidget(hdr)

        # Content area — items go here
        self._content = QWidget()
        self._content.setStyleSheet("background:transparent;")
        self._content.setMinimumHeight(0)     # allow shrinking to zero
        self._cl = QVBoxLayout(self._content)
        self._cl.setContentsMargins(0,4,0,0); self._cl.setSpacing(0)
        root.addWidget(self._content)

    def add_item(self, w):
        self._cl.addWidget(w)
        # Let the content expand naturally; measure after adding
        self._content.setMaximumHeight(16777215)

    def clear_items(self):
        while self._cl.count():
            item = self._cl.takeAt(0)
            if item.widget(): item.widget().deleteLater()

    def toggle(self):
        self._collapsed = not self._collapsed
        self._chev.setText("▸" if self._collapsed else "▾")

        if self._collapsed:
            # Capture natural height before shrinking
            self._natural_h = self._content.sizeHint().height()
            self._content.setMinimumHeight(0)
            self._anim = QPropertyAnimation(self._content, b"maximumHeight")
            self._anim.setDuration(280)
            self._anim.setEasingCurve(QEasingCurve.InOutCubic)
            self._anim.setStartValue(self._natural_h)
            self._anim.setEndValue(0)
        else:
            target = self._natural_h or self._content.sizeHint().height()
            self._content.setMinimumHeight(0)
            self._content.setMaximumHeight(0)
            self._anim = QPropertyAnimation(self._content, b"maximumHeight")
            self._anim.setDuration(280)
            self._anim.setEasingCurve(QEasingCurve.InOutCubic)
            self._anim.setStartValue(0)
            self._anim.setEndValue(target)
            self._anim.finished.connect(lambda: self._content.setMaximumHeight(16777215))

        # Resize the parent window on every animation tick
        self._anim.valueChanged.connect(self._resize_window)
        self._anim.start()

    def _resize_window(self):
        w = self.window()
        if w:
            w.setMaximumHeight(16777215)
            w.resize(w.width(), w.layout().sizeHint().height()
                     + w.layout().contentsMargins().top()
                     + w.layout().contentsMargins().bottom())


# ── Main window ────────────────────────────────────────────────────────────────

class ToDoApp(QWidget):
    def __init__(self):
        super().__init__()
        self._drag_pos=None
        self._known={}; self._animating=set(); self._self_done=set()
        self._item_widgets={}
        self._init_ui(); self._build_all()

        self._watcher=QFileSystemWatcher([JOURNAL_PATH])
        self._watcher.fileChanged.connect(self._on_file_changed)
        t=QTimer(self); t.timeout.connect(self._on_file_changed); t.start(3000)
        self._init_tray()

    def _init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(430)
        self.setMaximumHeight(16777215)
        self._particles=ParticleOverlay(self)

        self._root=QVBoxLayout(self)
        self._root.setContentsMargins(20,14,20,16); self._root.setSpacing(8)

        self._todo_sec=CollapsibleSection("To Do")
        self._root.addWidget(self._todo_sec)

        sep=QWidget(); sep.setFixedHeight(1)
        sep.setStyleSheet("background:rgba(255,255,255,28);")
        self._root.addWidget(sep)

        self._idea_sec=CollapsibleSection("Next Projects")
        self._root.addWidget(self._idea_sec)
        self.move(460,40)

    def _init_tray(self):
        self._tray=QSystemTrayIcon(QIcon.fromTheme("checkbox"),self)
        self._tray.setToolTip("Steam Deck To Do")
        menu=QMenu()
        self._show_action=menu.addAction("Show")
        self._show_action.setCheckable(True)
        self._show_action.setChecked(True)
        self._show_action.triggered.connect(self._toggle_visibility)
        menu.addSeparator()
        menu.addAction("Quit",QApplication.instance().quit)
        menu.aboutToShow.connect(lambda: self._show_action.setChecked(self.isVisible()))
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._tray_clicked)
        self._tray.show()

    def _toggle_visibility(self):
        if self.isVisible(): self.hide()
        else: self.show(); self.raise_()

    def _tray_clicked(self,reason):
        if reason==QSystemTrayIcon.Trigger: self._toggle_visibility()

    def paintEvent(self, event):
        painter=QPainter(self); painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(18,18,18,215)); painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(),14,14)

    # ── File watching ──────────────────────────────────────────────────────────

    def _on_file_changed(self, *_):
        if JOURNAL_PATH not in self._watcher.files():
            self._watcher.addPath(JOURNAL_PATH)
        todos=read_todos()
        new_state={t["text"]:t["done"] for t in todos}
        for text,done in new_state.items():
            if done and not self._known.get(text,False):
                if text in self._self_done: self._self_done.discard(text)
                elif text not in self._animating: self._animate_external(text)
        not_done_new={t for t,d in new_state.items() if not d}
        not_done_old={t for t,d in self._known.items() if not d}
        self._known=new_state
        if not_done_new!=not_done_old:
            # Skip rebuild if every change is an item we're already animating —
            # _on_removal will trigger the rebuild once the animation finishes
            newly_done=not_done_old - not_done_new
            new_items=not_done_new - not_done_old
            if new_items or not newly_done.issubset(self._animating):
                self._build_todos()

    def _animate_external(self, text):
        w=self._item_widgets.get(text)
        if w:
            self._animating.add(text)
            w.party_at.connect(self._on_party)
            w.removal_done.connect(lambda t=text: self._on_removal(t))
            w.play_completion()

    def _on_removal(self, text):
        self._animating.discard(text); self._item_widgets.pop(text,None)
        self._build_todos()

    def _on_undo(self, text):
        self._animating.discard(text); self._self_done.discard(text)
        self._build_todos()

    # ── Build lists ────────────────────────────────────────────────────────────

    def _build_all(self): self._build_todos(); self._build_ideas()

    def _build_todos(self):
        self._todo_sec.clear_items(); self._item_widgets={}
        todos=[t for t in read_todos() if not t["done"] and t["text"] not in self._animating]
        self._known={t["text"]:t["done"] for t in read_todos()}
        if todos:
            for t in todos:
                item=ToDoItem(t["text"])
                item.party_at.connect(self._on_party)
                item.removal_done.connect(lambda _,txt=t["text"]: self._on_removal(txt))
                item.undo_requested.connect(self._on_undo)
                item.bullet.clicked.connect(lambda txt=t["text"]: self._self_done.add(txt))
                item.bullet.clicked.connect(lambda txt=t["text"]: self._animating.add(txt))
                self._item_widgets[t["text"]]=item
                self._todo_sec.add_item(item)
        else:
            lbl=QLabel("Nothing outstanding.")
            lbl.setStyleSheet("color:rgba(160,160,160,140);background:transparent;font-size:11pt;")
            self._todo_sec.add_item(lbl)
        self.adjustSize()

    def _build_ideas(self):
        self._idea_sec.clear_items()
        ideas=read_ideas()
        if ideas:
            for i in ideas:
                item=IdeaItem(i["text"],i["date"])
                item.sparkle_at.connect(self._on_sparkle)
                item.promoted.connect(self._build_all)
                item.dismissed.connect(self._build_ideas)
                self._idea_sec.add_item(item)
        else:
            lbl=QLabel("No ideas yet.")
            lbl.setStyleSheet("color:rgba(160,160,160,140);background:transparent;font-size:11pt;")
            self._idea_sec.add_item(lbl)
        self.adjustSize()

    def _on_party(self, gp):
        lp=self.mapFromGlobal(gp); self._particles.burst(lp.x(),lp.y(),PARTY_COLS,count=60)
    def _on_sparkle(self, gp):
        lp=self.mapFromGlobal(gp); self._particles.burst(lp.x(),lp.y(),SPARKLE_COLS,count=22)

    def resizeEvent(self, e): self._particles.resize(self.size())

    def mousePressEvent(self,e):
        if e.button()==Qt.LeftButton:
            self._drag_pos=e.globalPos()-self.frameGeometry().topLeft(); self.grabMouse()
    def mouseMoveEvent(self,e):
        if self._drag_pos: self.move(e.globalPos()-self._drag_pos)
    def mouseReleaseEvent(self,e):
        if e.button()==Qt.LeftButton: self.releaseMouse(); self._drag_pos=None


def main():
    app=QApplication(sys.argv)
    app.setApplicationName("Learning To Do")
    app.setQuitOnLastWindowClosed(False)
    todo=ToDoApp(); todo.show()
    sys.exit(app.exec_())

if __name__=="__main__": main()
