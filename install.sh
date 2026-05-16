#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLOCK="$SCRIPT_DIR/clock.py"
DESKTOP_FILE="$HOME/.local/share/applications/steam-deck-clock.desktop"
AUTOSTART_FILE="$HOME/.config/autostart/steam-deck-clock.desktop"

# Check dependency
if ! $HOME/clock-env/bin/python3 -c "from PyQt5.QtWidgets import QApplication" 2>/dev/null; then
    echo "PyQt5 not found. Installing..."
    python3 -m venv ~/clock-env
    ~/clock-env/bin/pip install PyQt5
fi

chmod +x "$CLOCK"

# Write .desktop with the actual path
cat > "$DESKTOP_FILE" <<EOF
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

echo "Installed to $DESKTOP_FILE"

read -rp "Launch clock at desktop login? [y/N] " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    mkdir -p "$HOME/.config/autostart"
    cp "$DESKTOP_FILE" "$AUTOSTART_FILE"
    echo "Autostart enabled."
fi

echo ""
echo "Done! Run it now with: $HOME/clock-env/bin/python3 $CLOCK"
echo "Or find 'Steam Deck Clock' in your app menu."
