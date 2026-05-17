#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLOCK="$SCRIPT_DIR/clock.py"
TODO="$SCRIPT_DIR/todo.py"
APPS_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"

# Check / create venv with PyQt5
if ! "$HOME/clock-env/bin/python3" -c "from PyQt5.QtWidgets import QApplication" 2>/dev/null; then
    echo "PyQt5 not found. Installing..."
    python3 -m venv ~/clock-env
    ~/clock-env/bin/pip install PyQt5
fi

chmod +x "$CLOCK" "$TODO"
mkdir -p "$APPS_DIR" "$AUTOSTART_DIR"

# ── Clock ──────────────────────────────────────────────────────────────────────

cat > "$APPS_DIR/steam-deck-clock.desktop" <<EOF
[Desktop Entry]
Name=Steam Deck Clock
Comment=Transparent desktop clock with date
Exec=$HOME/clock-env/bin/python3 $CLOCK
Icon=clock
Terminal=false
Type=Application
Categories=Utility;
Keywords=clock;time;date;desktop;
StartupNotify=false
EOF
echo "Installed clock to $APPS_DIR/steam-deck-clock.desktop"

# ── To-do ──────────────────────────────────────────────────────────────────────

cat > "$APPS_DIR/steam-deck-todo.desktop" <<EOF
[Desktop Entry]
Name=Steam Deck To Do
Comment=Floating to-do list and ideas panel
Exec=$HOME/clock-env/bin/python3 $TODO
Icon=checkbox
Terminal=false
Type=Application
Categories=Utility;
Keywords=todo;tasks;ideas;list;journal;
StartupNotify=false
EOF
echo "Installed to-do to $APPS_DIR/steam-deck-todo.desktop"

# ── Autostart ──────────────────────────────────────────────────────────────────

read -rp "Launch clock and to-do at desktop login? [y/N] " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    cp "$APPS_DIR/steam-deck-clock.desktop" "$AUTOSTART_DIR/steam-deck-clock.desktop"
    cp "$APPS_DIR/steam-deck-todo.desktop"  "$AUTOSTART_DIR/steam-deck-todo.desktop"
    echo "Autostart enabled for both apps."
fi

echo ""
echo "Done!"
echo "  Clock: $HOME/clock-env/bin/python3 $CLOCK"
echo "  To-do: $HOME/clock-env/bin/python3 $TODO"
