#!/usr/bin/env bash
#
# Creates a desktop shortcut for the Nanopore QC Dashboard.
# Works on Linux systems with a standard desktop environment.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_DIR="${HOME}/Desktop"
DESKTOP_FILE="${DESKTOP_DIR}/nanopore-qc.desktop"

# Ensure Desktop directory exists
mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=Nanopore QC
Comment=Nanopore Sequencing QC Dashboard
Exec=bash -c 'cd "${SCRIPT_DIR}" && ./run.sh'
Icon=${SCRIPT_DIR}/icon.svg
Terminal=true
Type=Application
Categories=Science;Education;
StartupNotify=true
EOF

chmod +x "$DESKTOP_FILE"

# Mark as trusted on GNOME-based desktops (suppresses "untrusted" warning)
if command -v gio &>/dev/null; then
    gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true
fi

echo "Desktop shortcut created at: $DESKTOP_FILE"
echo "You should now see 'Nanopore QC' on your desktop."
