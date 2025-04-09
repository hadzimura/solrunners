xrandr --output HDMI-2 --mode 1920x1080 --rotate left
cd /home/zero/solrunners
export PYTHONPATH=$PYTHONPATH:/home/zero/solrunners
export PYTHONUNBUFFERED=1
source /home/zero/solrunners/.venv/bin/activate
exec python3 sol/runner.py --room 5
# exec /home/zero/solrunners/run.sh
# exec xterm