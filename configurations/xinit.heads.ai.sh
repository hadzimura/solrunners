#!/usr/bin/env bash
# AI startup script for Heads runtime without window manager.

set -euo pipefail

# Auto-detect connected HDMI output — handles HDMI-1 vs HDMI-2 across RPi models.
# Use --auto to select the display's native preferred mode from its EDID. This is
# more portable than hardcoding 1920x1080: different TVs/monitors may only offer
# 1280x720 progressive (1920x1080i interlaced does not work as an X framebuffer).
# After --rotate left the session becomes portrait (e.g. 720x1280 for a 720p TV).
# Config.py reads actual resolution at runtime via xrandr, so the app adapts.
DISPLAY_OUTPUT=$(xrandr | awk '/ connected/ {print $1; exit}')
xrandr --output "$DISPLAY_OUTPUT" --auto --rotate left

cd /home/zero/solrunners
export PYTHONPATH="${PYTHONPATH:-}:/home/zero/solrunners"
export PYTHONUNBUFFERED=1
source /home/zero/solrunners/.venv/bin/activate
xset -dpms
xset s off
xset s noblank

exec /home/zero/solrunners/.venv/bin/python /home/zero/solrunners/Heads.ai.py --system rpi --fullscreen
