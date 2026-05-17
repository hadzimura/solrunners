# xrandr --output HDMI-1 --mode 1366x768 --rotate left
# xrandr --output HDMI-1 --mode 1366x768 --rotate left
# xrandr --output HDMI-1 --mode 1920x1080 --rotate left
xrandr --output HDMI-1 --rotate left
cd /home/zero/solrunners
export PYTHONPATH=$PYTHONPATH:/home/zero/solrunners
export PYTHONUNBUFFERED=1
source /home/zero/solrunners/.venv/bin/activate
xset -dpms     # disable DPMS (Energy Star) features.
xset s off     # disable screen saver
xset s noblank # don't blank the video device
exec matchbox-window-manager -use_titlebar no & unclutter & xterm
# exec matchbox-window-manager -use_titlebar no & unclutter & xterm


