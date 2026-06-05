#!/usr/bin/env bash
# AI startup script for Heads runtime without window manager.

set -euo pipefail

xrandr --output HDMI-1 --rotate left
cd /home/zero/solrunners
export PYTHONPATH="$PYTHONPATH:/home/zero/solrunners"
export PYTHONUNBUFFERED=1
source /home/zero/solrunners/.venv/bin/activate
xset -dpms
xset s off
xset s noblank

exec /home/zero/solrunners/.venv/bin/python /home/zero/solrunners/Heads.ai.py --system rpi --fullscreen

