# SOL-01

# General

## Packages

``` shell
sudo apt install --yes ffmpeg git 
      libsdl2-mixer-2.0-0 \
      libsdl2-2.0-0 \
      mpg123 \
      python3 \
      python3-dev \  
      libopenal1 \
      sox \
      tree
```

      python3-opengl \

## Python venv

``` shell
$ python3 -m venv /home/zero/sol-audio/.solenv
$ source /home/zero/sol-audio/.solenv/bin/activate
```

Activate for session: `/home/zero/.bashrc`

```
source /home/zero/sol-audio/.solenv/bin/activate
export PYTHONPATH=$PYTHONPATH:/home/zero/sol-audio/
```

apt-get install libglfw3-dev libgles2-mesa-dev
sudo apt-get install libosmesa6-dev
sudo apt-get install freeglut3-dev

sudo amixer cset numid=3 <n>
# where n is 0=auto, 1=headphones, 2=hdmi.


ImportError: 
    Error occured while running `from pyglet.gl import *`
    HINT: make sure you have OpenGL install. On Ubuntu, you can run 'apt-get install python-opengl'.
    If you're running on a server, you may need a virtual frame buffer; something like this should work:
    'xvfb-run -s "-screen 0 1400x900x24" python <your_script.py>'

    8  git clone https://github.com/goodtft/LCD-show.git
    9  chmod -R 755 LCD-show

https://avikdas.com/2018/12/31/setting-up-lcd-screen-on-raspberry-pi.html

apt install xserver-xorg
            xinit x11-xserver-utils blackbox xterm raspberrypi-ui-mods

mkdir /etc/X11/xorg.conf.d
cp /root/LCD-show/usr/99-calibration.conf-35-270 /etc/X11/xorg.conf.d/99-calibration.conf
cp /root/LCD-show/usr/99-fbturbo.conf /usr/share/X11/xorg.conf.d/
cp /root/LCD-show/usr/99-fbturbo.conf /etc/X11/xorg.conf.d/


   10  cd LCD-show/
   11  ./LCD35-show
   12  sh4d0w
   13  halt
   14  cat /boot/config.txt
   15  alsa-info 
   17  alsa-info 
   18  alsamixer 
   19  aplay -l
   20  history


$   sudo apt install mpg123


 

# Pulse Audio

## Packages

``` shell
$ sudo apt-get install pulseaudio pavucontrol paprefs
$ sudo usermod -a -G audio,pulse,pulse-access zero
```

``` shell
$ pacmd list-sinks
1 sink(s) available.
  * index: 0
        name: <alsa_output.platform-bcm2835_audio.analog-stereo>
        driver: <module-alsa-card.c>
        flags: HARDWARE HW_MUTE_CTRL HW_VOLUME_CTRL DECIBEL_VOLUME LATENCY 
        state: SUSPENDED
        suspend cause: IDLE
        priority: 9009
        volume: front-left: 56210 /  86% / -4.00 dB,   front-right: 56210 /  86% / -4.00 dB
                balance 0.00
        base volume: 56210 /  86% / -4.00 dB
        volume steps: 65537
        muted: no
        current latency: 0.00 ms
        max request: 0 KiB
        max rewind: 0 KiB
        monitor source: 0
        sample spec: s16le 2ch 44100Hz
        channel map: front-left,front-right
                     Stereo
        used by: 0
        linked by: 0
        fixed latency: 59.95 ms
        card: 0 <alsa_card.platform-bcm2835_audio>
        module: 6
        properties:
                alsa.resolution_bits = "16"
                device.api = "alsa"
                device.class = "sound"
                alsa.class = "generic"
                alsa.subclass = "generic-mix"
                alsa.name = "bcm2835 Headphones"
                alsa.id = "bcm2835 Headphones"
                alsa.subdevice = "0"
                alsa.subdevice_name = "subdevice #0"
                alsa.device = "0"
                alsa.card = "0"
                alsa.card_name = "bcm2835 Headphones"
                alsa.long_card_name = "bcm2835 Headphones"
                alsa.driver_name = "snd_bcm2835"
                device.bus_path = "platform-bcm2835_audio"
                sysfs.path = "/devices/platform/soc/3f00b840.mailbox/bcm2835_audio/sound/card0"
                device.form_factor = "internal"
                device.string = "hw:0"
                device.buffering.buffer_size = "10576"
                device.buffering.fragment_size = "2640"
                device.access_mode = "mmap"
                device.profile.name = "analog-stereo"
                device.profile.description = "Analog Stereo"
                device.description = "Built-in Audio Analog Stereo"
                module-udev-detect.discovered = "1"
                device.icon_name = "audio-card"
        ports:
                analog-output: Analog Output (priority 9900, latency offset 0 usec, available: unknown)
                        properties:
                                
        active port: <analog-output>
```

# Optional: Service

`/etc/systemd/system/pulseaudio.service` 

``` toml
[Unit]
Description=PulseAudio Daemon

[Install]
WantedBy=multi-user.target

[Service]
Type=simple
PrivateTmp=true
ExecStart=/usr/bin/pulseaudio --system --realtime --disallow-exit --no-cpu-limit
```

# Boot

http://rptl.io/configtxt

## kernel parameters
File is `/boot/firmware/cmdline.txt` and:

``` 
console=serial0,115200 console=tty1 root=PARTUUID=e75229ef-02 rootfstype=ext4 fsck.repair=yes rootwait quiet splash plymouth.ignore-serial-consoles cfg80211.ieee80211_regdom=CZ loglevel=3 logo.nologo vt.global_cursor_default=0
```

## boot logo

``` 
$ scp -r zero@10.0.0.211:/usr/share/plymouth/themes/pix/splash.png .
$ scp -r splash.png zero@10.0.0.211:/usr/share/plymouth/themes/pix/
``` 

sudo usermod -a -G tty zero

# Bluetooth

https://askubuntu.com/questions/701978/how-can-a-bluetooth-keyboard-that-requires-a-code-entry-be-paired-in-the-termina

``` shell
$ bluetoothctl
[bluetooth]# power on
Changing power on succeeded

[bluetooth]# agent on
Agent registered

[bluetooth]# default-agent 
Default agent request successful

[bluetooth]# scan on
Discovery started
[NEW] Device F4:EE:25:52:EE:4B RAPOO 5.0KB

[bluetooth]# pair F4:EE:25:52:EE:4B
Attempting to pair with F4:EE:25:52:EE:4B
[CHG] Device F4:EE:25:52:EE:4B Connected: yes
[CHG] Device F4:EE:25:52:EE:4B Bonded: yes
```

https://askubuntu.com/questions/62858/turn-off-monitor-using-command-line

 "640x480"x75.0   31.50  640 656 720 840  480 481 484 500 -hsync -vsync (37.5 kHz e)
[  6437.421] (II) modeset(0): Modeline "640x480"x59.9   25.18  640 656 752 800  480 490 492 525 -hsync -vsync (31.5 kHz e)

309  xset -display :0 screen-saver reset
  310  xset -display :0 s reset
  311  xset -display :0
  312  xset -display :0 q
  313  xset -display :0 s 0
  314  xset -display :0 q
  315  xset -display :0 -dpms
  316  xset -display :0 q

https://forums.raspberrypi.com/viewtopic.php?t=359778
https://rpishop.cz/chladice-pro-raspberry-pi-5/6496-raspberry-pi-5-active-cooler.html#tab-discussion
dtparam=fan_temp0=40000 dtparam=fan_temp0_hyst=10000 dtparam=fan_temp0_speed=125
Dobrý den, jedná se o chybu na současné verze libreelec. Starší verze nebo další update by měli problém vyřešit. Mělo by pomoci přidat ovladače do souboru config.txt /boot/firmware/config.txt dtparam=fan_temp0=40000 dtparam=fan_temp0_hyst=10000 dtparam=fan_temp0_speed=125
 Odpovědět

https://www.jeffgeerling.com/blog/2023/overclocking-and-underclocking-raspberry-pi-5