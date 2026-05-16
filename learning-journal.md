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
- `QSystemTrayIcon` creates a small icon in the system tray (notification area) — useful for apps that should stay running in the background without taking up taskbar space
- `Qt.Tool` window flag hides a window from the taskbar — needed when using a tray icon so the window doesn't appear in both places
- `app.setQuitOnLastWindowClosed(False)` is required when hiding windows to tray — without it, hiding the last window shuts the whole app down
- `menu.aboutToShow` signal fires just before a right-click menu appears — useful for updating checkbox states to reflect current app state before the user sees them
- `QLabel` supports **HTML rich text** — wrap text in `<span style="...">` to style just part of a label differently (e.g. smaller AM/PM alongside a large time display)
- User preferences can be saved to a **JSON config file** with Python's built-in `json` module — load on startup, write on change; no external libraries needed

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

##### Fix 5 — `clock.py`: close on double-click → hide to system tray

> **Why it was changed:** Closing the clock meant re-launching it from the terminal or app menu each time. A system tray icon lets it stay running in the background and be toggled without leaving the desktop.

**Before:**
```python
def mouseDoubleClickEvent(self, event):
    self.close()  # kills the app entirely
```

**After:**
```python
def mouseDoubleClickEvent(self, event):
    self.hide()  # hides the window but keeps the app running
```

The tray icon is set up in a new `_init_tray()` method:

```python
def _init_tray(self):
    self._tray = QSystemTrayIcon(QIcon.fromTheme("clock"), self)
    self._tray.setToolTip("Steam Deck Clock")
    menu = QMenu()
    self._show_action = menu.addAction("Show")
    self._show_action.setCheckable(True)   # gives it a checkbox
    self._show_action.setChecked(True)     # ticked by default (clock starts visible)
    self._show_action.triggered.connect(self._toggle_visibility)
    menu.addSeparator()
    menu.addAction("Quit", QApplication.instance().quit)
    menu.aboutToShow.connect(self._update_show_action)  # sync checkbox before menu appears
    self._tray.setContextMenu(menu)
    self._tray.activated.connect(self._tray_clicked)    # left-click also toggles
    self._tray.show()
```

Two supporting methods keep the checkbox in sync with the actual window state:

```python
def _update_show_action(self):
    self._show_action.setChecked(self.isVisible())  # tick = visible, unticked = hidden

def _toggle_visibility(self):
    if self.isVisible():
        self.hide()
    else:
        self.show()
        self.raise_()  # bring to front if other windows are on top
```

`app.setQuitOnLastWindowClosed(False)` was also added in `main()` — without it, hiding the window would shut the whole app down.

---

#### Status

##### Fix 6 — `clock.py`: position memory and 12/24-hour toggle

> **Why it was added:** The clock always opened at `(40, 40)` regardless of where it was dragged. The 12/24-hour preference was also lost on every relaunch.

Settings are saved to `~/.config/steam-deck-clock.json` as a small JSON file:

```json
{"x": 240, "y": 80, "use_24h": false}
```

**Loading on startup:**
```python
def _load_config(self):
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)  # reads the saved JSON file
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # file doesn't exist yet — use defaults

# In _init_ui(), position is restored:
self.move(self._config.get("x", 40), self._config.get("y", 40))
# .get("x", 40) means "use the saved x value, or 40 if there isn't one"
```

**Saving on drag end and preference change:**
```python
def _save_config(self):
    with open(CONFIG_PATH, "w") as f:
        json.dump({"x": self.x(), "y": self.y(), "use_24h": self._use_24h}, f)

def mouseReleaseEvent(self, event):
    if event.button() == Qt.LeftButton:
        self.releaseMouse()
        self._drag_pos = None
        self._save_config()  # write position every time drag ends
```

**12/24-hour toggle in the tray menu:**
```python
self._24h_action = menu.addAction("24-hour clock")
self._24h_action.setCheckable(True)
self._24h_action.setChecked(self._use_24h)
self._24h_action.triggered.connect(self._toggle_24h)

def _toggle_24h(self, checked):
    self._use_24h = checked
    self._save_config()   # persist the preference immediately
    self._tick()          # update the display right away, don't wait for next second
```

**AM/PM styled smaller using HTML rich text:**

`QLabel` supports HTML — wrapping part of the text in a `<span>` lets you style it independently without needing a second label:

```python
time_str = now.strftime("%I:%M:%S")   # e.g. "03:45:12"
ampm = now.strftime("%p")             # "AM" or "PM"
self.time_label.setText(
    f'{time_str} <span style="font-size:20pt; font-weight:bold;">{ampm}</span>'
    # ↑ main time stays at 52pt, AM/PM drops to 20pt bold
)
```

---

#### Status

| Issue | Status |
|-------|--------|
| `install.sh` used broken `pip install --user` | ✅ Fixed |
| `text-shadow` silently ignored by Qt | ✅ Fixed |
| Clock autostart not configured | ✅ Fixed |
| Drag breaks if mouse moves faster than window | ✅ Fixed |
| No way to hide clock without closing it entirely | ✅ Fixed — system tray icon added |
| Clock forgets position and time format on relaunch | ✅ Fixed — JSON config file |

---
