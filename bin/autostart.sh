#!/bin/sh
cd /home/zero/solrunners
export PYTHONPATH=$PYTHONPATH:/home/zero/solrunners
export PYTHONUNBUFFERED=1
source /home/zero/solrunners/.venv/bin/activate
xset -dpms     # disable DPMS (Energy Star) features.
xset s off     # disable screen saver
xset s noblank # don't blank the video device
matchbox-window-manager -use_titlebar no -use_cursor no &
unclutter &  python3 sol/runner.py --room 3
# exec /home/zero/solrunners/run.sh
# exec xterm