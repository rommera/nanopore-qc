#!/usr/bin/env bash
#
# Creates a Windows desktop shortcut (.bat + .vbs) for the Nanopore QC Dashboard
# when running under WSL2.
#
# The shortcut launches WSL, activates conda, and starts the Streamlit app.
# A .vbs wrapper is used to hide the terminal flash when double-clicking.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Convert WSL path to Windows path for the icon
SCRIPT_DIR_WIN=$(wslpath -w "$SCRIPT_DIR" 2>/dev/null) || {
    echo "ERROR: This script must be run inside WSL2."
    exit 1
}

# Locate Windows Desktop folder
WIN_USER=$(cmd.exe /C "echo %USERNAME%" 2>/dev/null | tr -d '\r')
WIN_DESKTOP="/mnt/c/Users/${WIN_USER}/Desktop"

if [ ! -d "$WIN_DESKTOP" ]; then
    echo "ERROR: Could not find Windows Desktop at $WIN_DESKTOP"
    echo "Please provide your Windows Desktop path."
    exit 1
fi

# Convert the WSL project path to what WSL sees
WSL_DISTRO=$(wslpath -w / 2>/dev/null | sed 's|\\\\wsl.localhost\\||;s|\\.*||' || echo "Ubuntu")

# --- Create the .bat launcher ---
BAT_FILE="${WIN_DESKTOP}/Nanopore_QC.bat"
cat > "$BAT_FILE" <<BATEOF
@echo off
echo Starting Nanopore QC Dashboard...
echo.
echo Keep this window open. Press Ctrl+C to stop.
echo.
start "" http://localhost:8501
wsl -d ${WSL_DISTRO} -- bash -lc "cd '${SCRIPT_DIR}' && ./run.sh"
BATEOF

# --- Create a .vbs wrapper for a cleaner launch (optional, hides cmd flash) ---
VBS_FILE="${WIN_DESKTOP}/Nanopore_QC.vbs"
BAT_FILE_WIN="${SCRIPT_DIR_WIN}\\..\\..\\..\\..\\..\\mnt\\c\\Users\\${WIN_USER}\\Desktop\\Nanopore_QC.bat"
# Simpler: use the direct windows path
cat > "$VBS_FILE" <<VBSEOF
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c ""C:\Users\\${WIN_USER}\Desktop\Nanopore_QC.bat""", 1, False
VBSEOF

echo "Desktop shortcuts created:"
echo "  - ${WIN_DESKTOP}/Nanopore_QC.bat  (double-click to launch)"
echo "  - ${WIN_DESKTOP}/Nanopore_QC.vbs  (alternative: launches without cmd flash)"
echo ""
echo "Your colleagues can double-click 'Nanopore_QC.bat' on their Windows Desktop."
echo "The dashboard will open in their default browser."
