#!/usr/bin/env bash
# configurations/xinit.tate.sh
# Startup script for Tate node — launched by xinit from sol.tate.service.
# X server is already running when this script executes; no WM is started.

set -euo pipefail

# Prevent display blanking / DPMS power-off during gallery playback
xset -dpms
xset s off
xset s noblank

cd /home/zero/solrunners
export PYTHONPATH="/home/zero/solrunners"
export PYTHONUNBUFFERED=1

source /home/zero/solrunners/.venv/bin/activate

exec /home/zero/solrunners/.venv/bin/python /home/zero/solrunners/tate.py
