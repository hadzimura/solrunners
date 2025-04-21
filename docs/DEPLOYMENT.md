# Runners

Image: `Raspberry PI OS (64 bit)`

| hostname | ip address | wlan0 MAC           |
|----------|------------|---------------------|
| room1    | 10.0.0.1   | `B8:27:EB:19:5D:5C` |
| room2    | 10.0.0.2   | `1C:B7:2C:D5:0E:3D` |
| room3    | 10.0.0.3   | `2C:CF:67:5B:7E:D2` |
| room4    | 10.0.0.4   | `2C:CF:67:AB:95:2A` |
| room5    | 10.0.0.5   | `2C:CF:67:5B:80:DB` |


``` shell
sudo apt update
sudo apt upgrade 
sudo apt-get install xinit x11-xserver-utils matchbox-window-manager xautomation unclutter mc xterm
``` 

/etc/systemd/system/getty@tty1.service.d/autologin.conf
```  text
[Service]
ExecStart=
ExecStart=-/sbin/agetty -nonewline --noissue --autologin zero --noclear %I $TERM
ExecStart=-/usr/bin/agetty --skip-login --nonewline --noissue --autologin zero --noclear %I $TERM
``` 

``` shell
mkdir /home/zero/.ssh
chmod 700 /home/zero/.ssh

echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHiV4uSS7QQ/KRwCPWBNC6zEqoDibEkLYOgxOdrnZBBB zeromini@rk" > /home/zero/.ssh/authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINqhhcw3svD9s4+GniljpF7yGH6LnW/0K7PQUTyda2G9 room1@runner" >> /home/zero/.ssh/authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINqhhcw3svD9s4+GniljpF7yGH6LnW/0K7PQUTyda2G9 room2@runner" >> /home/zero/.ssh/authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINqhhcw3svD9s4+GniljpF7yGH6LnW/0K7PQUTyda2G9 room3@runner" >> /home/zero/.ssh/authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINqhhcw3svD9s4+GniljpF7yGH6LnW/0K7PQUTyda2G9 room4@runner" >> /home/zero/.ssh/authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINqhhcw3svD9s4+GniljpF7yGH6LnW/0K7PQUTyda2G9 room5@runner" >> /home/zero/.ssh/authorized_keys
chmod 600 /home/zero/.ssh/authorized_keys

echo -e "-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACDaoYXMN7Lw/bOPhp4pY6Re8hh+i51v9Cuz0FE8nWthvQAAAJDW6CgF1ugo
BQAAAAtzc2gtZWQyNTUxOQAAACDaoYXMN7Lw/bOPhp4pY6Re8hh+i51v9Cuz0FE8nWthvQ
AAAEC7W5p6wuCLmsku4pGfNN/3uuQxrV/EtaCxudDGJyL2x9qhhcw3svD9s4+GniljpF7y
GH6LnW/0K7PQUTyda2G9AAAAC3plcm9Ac29sLTAxAQI=
-----END OPENSSH PRIVATE KEY-----" > /home/zero/.ssh/id_ed25519

echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINqhhcw3svD9s4+GniljpF7yGH6LnW/0K7PQUTyda2G9 room3@runner" >  /home/zero/.ssh/id_ed25519.pub
chmod 600 /home/zero/.ssh/id*
```

`/etc/hosts`

``` text
10.0.0.1        room1
10.0.0.2        room2
10.0.0.3        room3
10.0.0.4        room4
10.0.0.5        room5
```

Current host has `127.0.0.1`

# Git

``` text
git clone git@github.com:hadzimura/solrunners.git /home/zero/solrunners
python3 -m venv /home/zero/solrunners/.venv
source /home/zero/solrunners/.venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r /home/zero/solrunners/requirements.txt
python3 -m pip install -r /home/zero/solrunners/requirements.gpio.txt
python3 -m pip install -r /home/zero/solrunners/requirements.lite.txt
sudo cp /home/zero/solrunners/media/raspberry/splash.png /usr/share/plymouth/themes/pix/
``` 

.bashrc

``` 
echo "source /home/zero/solrunners/.venv/bin/activate" >> /home/zero/.bashrc
echo "export PYTHONPATH=$PYTHONPATH:/home/zero/solrunners/" >> /home/zero/.bashrc
``` 

https://repos.influxdata.com/debian/
``` 
sudo -i
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
apt update
apt install telegraf
rm /etc/telegraf/telegraf.conf
cp /home/zero/solrunners/telegraf.conf /etc/telegraf
!!!! sudo usermod -a -G video telegraf
service telegraf start
``` 
influx token: Si5w9T32qtMKfHvjzY2xAS-UuubDxqK7Roqo6jXOrh0rJ24_GGQXWfzwq6ym-376zdY7bkkxhNfYU16daFWNWA==

kiosk mode
https://www.raspberrypi.com/tutorials/how-to-use-a-raspberry-pi-in-kiosk-mode/
https://reelyactive.github.io/diy/pi-kiosk/  

