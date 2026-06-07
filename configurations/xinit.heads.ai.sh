#!/usr/bin/env bash
# AI startup script for Heads runtime without window manager.

set -euo pipefail

# Auto-detect connected HDMI output — handles HDMI-1 vs HDMI-2 across RPi models.
# Force 1920x1080 mode so that after --rotate left the X session becomes 1080x1920,
# filling the full portrait panel. --auto would pick the preferred 1440x900 mode
# which only yields a 900x1440 framebuffer — smaller than the physical display.
DISPLAY_OUTPUT=$(xrandr | awk '/ connected/ {print $1; exit}')
xrandr --output "$DISPLAY_OUTPUT" --mode 1920x1080 --rotate left

cd /home/zero/solrunners
export PYTHONPATH="${PYTHONPATH:-}:/home/zero/solrunners"
export PYTHONUNBUFFERED=1
source /home/zero/solrunners/.venv/bin/activate
xset -dpms
xset s off
xset s noblank

exec /home/zero/solrunners/.venv/bin/python /home/zero/solrunners/Heads.ai.py --system rpi --fullscreen
