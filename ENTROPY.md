# The Entropy: Behind the Screen

"The Entropy" is part of the `Springs of Life: From the Sucher's family archives` exhibition. 

It consists of two pre-rendered `H.264` movies that run at `1366x768` resolution and the [Entro.py](Entro.py) controller script that uses [OpenCV](https://opencv.org) version `4.11.0` for runtime per-frame visual enhancements. Audio streams are handled via [pyglet](https://pyglet.readthedocs.io/en/latest/) framework (`1.5.27`). 

Playback itself is hosted on top of [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) (sporting `8GB` of RAM) microcomputer connected to an LCD TV screen. It is powered by the [Raspberry Pi OS (64-bit)](https://www.raspberrypi.com/software/operating-systems/) that runs in `kiosk-mode` using [matchbox-window-manager](https://github.com/NetPLC/matchbox-window-manager). 

## Kiosk Runtime

The operating system boots into an `init:3` runlevel and starts the Xorg server using `.bashrc`:

``` text
if [ -z $SSH_TTY ]; then
    startx &>/dev/null
else
  echo "Not executing SoL Runner as we are logged over SSH"
fi
``` 

The `startx` shell wrapper uses `.xinitrc` to execute commands on top of the Xorg session:

``` text
xrandr --output HDMI-1 --mode 1366x768
cd /home/zero/solrunners
export PYTHONPATH=$PYTHONPATH:/home/zero/solrunners
export PYTHONUNBUFFERED=1
source /home/zero/solrunners/.venv/bin/activate
xset -dpms
xset s off
xset s noblank
exec matchbox-window-manager -use_titlebar no & unclutter & python3 Entro.py
```

All the media files are pre-loaded into the `SHM` (ramdisk) filesystem during the `RPi` boot sequence to avoid corruption should the power outage occur. 

[Unit]
Description=Move SoL Media Data to SHM storage
After=network.target

[Service]
Type=simple
ExecStart=/home/zero/solrunners/configurations/systemd/media_to_shm.sh
WorkingDirectory=/home/zero/solrunners
StandardOutput=inherit
StandardError=inherit
Restart=no
User=zero

[Install]
WantedBy=multi-user.target

# Entro.py

main


runtime has two modes that repeat indefinitely: 

1. `countdown`
2. `entropy`