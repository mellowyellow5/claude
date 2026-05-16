# Learning Journal

A personal record of learning sessions — what was tried, what broke, what was figured out, and what comes next.

---

### 2026-05-16 — Getting a transparent clock running on the Steam Deck

**Category:** `Steam Deck / Linux` · `Python` · `Git & Version Control` · `PyQt5`

**Goal:** Build a transparent desktop clock with date display in PyQt5, push it to GitHub, and get it running on the Steam Deck in Desktop Mode.

---

#### What happened

Started with a working PyQt5 clock app written on a dev machine, but the files had been committed to a feature branch rather than `main` — so cloning the repo on the Steam Deck only pulled down a README. After learning about branches and using `git fetch` + `git checkout`, the right branch was found.

Then PyQt5 wasn't installed, and installing it on Steam Deck hit three separate walls: the filesystem is read-only by default, pacman's keyring wasn't initialised, and Valve's SteamOS package signatures weren't trusted. The solution was a **Python virtual environment**, bypassing pacman entirely.

---

#### Key learnings

**Git & Version Control**
- `git clone` only checks out the **default branch** (`main`) — files on other branches won't appear until you `git checkout` that branch
- `git branch -a` lists all branches including remote ones with their full names
- Pull requests on GitHub are two steps: **Create PR**, then a separate **Merge PR** button appears on the next page

**Steam Deck / Linux**
- Steam Deck's filesystem is **read-only by default** — `sudo steamos-readonly disable` is needed before pacman can install anything
- `pacman-key --init` and `pacman-key --populate archlinux` are required before pacman can verify package signatures on a fresh Steam Deck
- SteamOS uses its own package signing keys which can conflict with the standard Arch keyring setup
- A **Python virtual environment** (`python3 -m venv`) sidesteps pacman entirely for Python packages — nothing needs to be written to the read-only system filesystem

**Bash**
- `bash` treats spaces as argument separators — running multiple commands on one line without `;` or `&&` passes everything after the first space as arguments to the first command
- `cd` = change directory · `pwd` = print working directory (where you are) · `ls` = list files here
- `!` is a special character inside **double quotes** — swap to **single quotes** to avoid "event not found" errors

**PyQt5 / Python**
- Qt's stylesheet engine is **not real CSS** — properties like `text-shadow` are silently ignored with no error or warning; the shadow just doesn't appear

---

#### Commands used this session

```bash
# Check all branches including remote ones
git branch -a

# Switch to a specific remote branch
git fetch origin
git checkout claude/steam-deck-desktop-clock-GJtho

# Unlock Steam Deck filesystem (temporary — resets on reboot)
sudo steamos-readonly disable

# Initialise pacman keyring so it can verify packages
sudo pacman-key --init
sudo pacman-key --populate archlinux

# Create a virtual environment and install PyQt5 inside it
python3 -m venv ~/clock-env
~/clock-env/bin/pip install PyQt5

# Run the clock using the venv Python (not system Python)
~/clock-env/bin/python3 clock.py

# Test PyQt5 without triggering bash's ! special character
python3 -c 'from PyQt5.QtWidgets import QApplication; print("PyQt5 works!")'
```

---

#### Fixes made after the session

---

##### Fix 1 — `install.sh`: system pip → virtual environment

> **Why it broke:** The original script used `pip install PyQt5 --user` which tries to write to the system Python. On Steam Deck the filesystem is read-only, so this fails silently or with a permissions error.

**Before:**
```python
if ! python3 -c "from PyQt5.QtWidgets import QApplication" 2>/dev/null; then
    pip install PyQt5 --user
```

**After:**
```python
if ! $HOME/clock-env/bin/python3 -c "from PyQt5.QtWidgets import QApplication" 2>/dev/null; then
    python3 -m venv ~/clock-env          # create isolated Python environment
    ~/clock-env/bin/pip install PyQt5    # install into the venv, not the system
```

The `Exec=` line in the `.desktop` file also had to change so it launches using the venv Python:

```diff
- Exec=python3 clock.py
+ Exec=/home/deck/clock-env/bin/python3 /home/deck/claude/clock.py
```

---

##### Fix 2 — `clock.py`: `text-shadow` CSS → `QGraphicsDropShadowEffect`

> **Why it broke:** Qt's stylesheet engine understands a subset of CSS but silently ignores anything it doesn't support. `text-shadow` is one of those — no error appears, the shadow simply doesn't exist.

**Before:**
```python
self.time_label.setStyleSheet("color: white; text-shadow: 0 2px 8px rgba(0,0,0,0.8);")
# ↑ the text-shadow part is completely ignored by Qt — no error, just no shadow
```

**After:**
```python
self.time_label.setStyleSheet("color: white;")
time_shadow = QGraphicsDropShadowEffect()   # Qt's built-in shadow system
time_shadow.setBlurRadius(12)               # how soft/spread the shadow is
time_shadow.setOffset(2, 2)                 # 2px right, 2px down
time_shadow.setColor(QColor(0, 0, 0, 180)) # black, 180/255 opacity
self.time_label.setGraphicsEffect(time_shadow)
```

The same pattern was applied to `date_label` with slightly softer values (blur 8, offset 1) since the text is smaller.

---

##### Fix 3 — Autostart: `.desktop` files created

> **Why it wasn't working:** The `install.sh` script had the autostart logic, but it had never been run on this machine. The files were created manually instead.

Two files are needed:

| File | Purpose |
|------|---------|
| `~/.local/share/applications/steam-deck-clock.desktop` | Makes the clock appear in the app launcher menu |
| `~/.config/autostart/steam-deck-clock.desktop` | Launches the clock automatically at Desktop Mode login |

The autostart file is a copy of the applications file — KDE Plasma (Steam Deck's Desktop Mode) reads `~/.config/autostart/` on login and launches anything it finds there.

---

##### Fix 4 — `clock.py`: drag behaviour with `grabMouse()`

> **Why it broke:** When dragging quickly, the mouse cursor can move faster than the window can reposition itself. The moment the cursor leaves the window boundary, Qt stops sending `mouseMoveEvent` to that widget — so the drag stops, even though the button is still held down.

**Before:**
```python
def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
        self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

def mouseMoveEvent(self, event):
    if event.buttons() == Qt.LeftButton and self._drag_pos:  # stops working if cursor leaves window
        self.move(event.globalPos() - self._drag_pos)

def mouseReleaseEvent(self, event):
    self._drag_pos = None
```

**After:**
```python
def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
        self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
        self.grabMouse()  # tell Qt: send ALL mouse events here, even if cursor leaves the window

def mouseMoveEvent(self, event):
    if self._drag_pos is not None:       # simpler check — grabMouse() guarantees we only get
        self.move(event.globalPos() - self._drag_pos)  # events while dragging

def mouseReleaseEvent(self, event):
    if event.button() == Qt.LeftButton:
        self.releaseMouse()   # give mouse control back to whatever is under the cursor
        self._drag_pos = None
```

`grabMouse()` is a Qt feature that redirects **all** mouse events from anywhere on screen to one widget until `releaseMouse()` is called. This is standard practice for drag operations.

---

#### Status

| Issue | Status |
|-------|--------|
| `install.sh` used broken `pip install --user` | ✅ Fixed |
| `text-shadow` silently ignored by Qt | ✅ Fixed |
| Clock autostart not configured | ✅ Fixed |
| Drag breaks if mouse moves faster than window | ✅ Fixed |

---
