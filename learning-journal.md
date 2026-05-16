# Learning Journal

A personal record of learning sessions — what was tried, what broke, what was figured out, and what comes next.

---

### 2026-05-16 — Getting a transparent clock running on the Steam Deck
**Category:** Steam Deck / Linux | Python | Git & Version Control

**Goal:** Build a transparent desktop clock with date display in PyQt5, push it to GitHub, and get it running on the Steam Deck in Desktop Mode.

**What happened:**
Started with a working PyQt5 clock app written on a dev machine, but the files had been committed to a feature branch rather than main — so cloning the repo on the Steam Deck only pulled down a README. After learning about branches and using `git fetch` + `git checkout`, the right branch was found. Then PyQt5 wasn't installed, and installing it on Steam Deck hit three separate walls: the filesystem is read-only by default, pacman's keyring wasn't initialised, and Valve's SteamOS package signatures weren't trusted. The solution was a Python virtual environment, bypassing pacman entirely.

**Key learnings:**
- `git clone` only checks out the default branch (main) — files on other branches won't appear until you `git checkout` that branch
- `git branch -a` lists all branches including remote ones with their full names
- Steam Deck's filesystem is read-only by default — `sudo steamos-readonly disable` is needed before pacman can install anything
- `pacman-key --init` and `pacman-key --populate archlinux` are required before pacman can verify package signatures on a fresh Steam Deck
- SteamOS uses its own package signing keys which can conflict with standard Arch keyring setup
- A Python virtual environment (`python3 -m venv`) sidesteps pacman entirely for Python packages
- `bash` treats spaces as argument separators — running multiple commands on one line without `;` or `&&` passes everything as arguments to the first command
- `cd` = change directory; `pwd` shows where you currently are; `ls` lists files in current folder
- Qt stylesheet engine is not real CSS — `text-shadow` is silently ignored
- In bash, `!` is a special character inside double quotes — swap to single quotes to avoid "event not found" errors
- Pull requests on GitHub are two steps: Create PR, then Merge PR on the next page

**Real examples from this session:**
```bash
# Check all branches including remote ones
git branch -a

# Switch to a remote branch
git fetch origin
git checkout claude/steam-deck-desktop-clock-GJtho

# Unlock Steam Deck filesystem
sudo steamos-readonly disable

# Initialise pacman keyring
sudo pacman-key --init
sudo pacman-key --populate archlinux

# Create a virtual environment and install PyQt5 inside it
python3 -m venv ~/clock-env
~/clock-env/bin/pip install PyQt5

# Run the clock using the venv python
~/clock-env/bin/python3 clock.py

# Avoid bash ! special character issue
python3 -c 'from PyQt5.QtWidgets import QApplication; print("PyQt5 works!")'
```

**Left open:**
- ~~`install.sh` still uses broken `pip install PyQt5 --user` — needs updating to use venv approach~~ — **Fixed:** install.sh already uses the venv approach
- ~~`text-shadow` in the stylesheet should be replaced with `QGraphicsDropShadowEffect`~~ — **Fixed:** added `QGraphicsDropShadowEffect` to both time and date labels
- ~~Clock autostart not yet configured~~ — **Fixed:** `.desktop` file created in `~/.local/share/applications/` and copied to `~/.config/autostart/`
- The drag behaviour can break if mouse moves faster than the window — worth exploring `grabMouse()`

---
