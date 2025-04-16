# Runners

Image: `Raspberry PI OS (64 bit)`

| hostname | ip address | wlan0 MAC           |
|----------|------------|---------------------|
| room1    | 10.0.0.1   | `B8:27:EB:19:5D:5C` |
| room2    | 10.0.0.2   | `1C:B7:2C:D5:0E:3D` |
| room3    | 10.0.0.3   | `2C:CF:67:5B:80:DB` |
| room4    | 10.0.0.4   | `2C:CF:67:AB:95:2A` |
| room5    | 10.0.0.5   | `2C:CF:67:5B:7E:D2` |

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
rm -rf /home/zero/solrunners/.venv
python3 -m venv /home/zero/solrunners/.venv
source /home/zero/solrunners/.venv/bin/activate
    
    python3 -m pip install --upgrade pip
python3 -m pip install -r /home/zero/solrunners/requirements.txt


``` 

.bashrc

``` 
echo "source /home/zero/solrunners/.venv/bin/activate" >> /home/zero/.bashrc
echo "export PYTHONPATH=$PYTHONPATH:/home/zero/solrunners/" >> /home/zero/.bashrc
``` 

fi

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




o make it permanent you have to use  systemctl set-default as shown below:

sudo systemctl set-default multi-user.target
and reboot.

To revert graphical session use

sudo systemctl set-default graphical.target

   48  service --status-all
service cups disable
systemctl cups disable
systemctl cups.service disable
systemctl list-unit-files | grep enabled
   53  systemctl disable cups
systemctl disable bluetooth
   55  systemctl list-unit-files | grep enabled
   systemctl disable nfs-client.target
   57  systemctl disable wayvnc
   58  systemctl disable sol.service
   59  systemctl disable lightdm.service
   

sudo apt-get install build-essential cmake git unzip pkg-config
sudo apt-get install libjpeg-dev libpng-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install libgtk2.0-dev libcanberra-gtk* libgtk-3-dev
sudo apt-get install libgstreamer1.0-dev gstreamer1.0-gtk3
sudo apt-get install libgstreamer-plugins-base1.0-dev gstreamer1.0-gl
sudo apt-get install libxvidcore-dev libx264-dev
sudo apt-get install python3-dev python3-numpy python3-pip
sudo apt-get install libtbbmalloc2 libtbb-dev libdc1394-dev
sudo apt-get install libv4l-dev v4l-utils
sudo apt-get install libopenblas-dev libatlas-base-dev libblas-dev
sudo apt-get install liblapack-dev gfortran libhdf5-dev
sudo apt-get install libprotobuf-dev libgoogle-glog-dev libgflags-dev
sudo apt-get install protobuf-compiler

-D OPENCV_EXTRA_MODULES_PATH=~/opencv/opencv_contrib/modules \

cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D ENABLE_NEON=ON \
-D WITH_OPENMP=ON \
-D WITH_OPENCL=OFF \
-D BUILD_TIFF=ON \
-D WITH_FFMPEG=ON \
-D WITH_TBB=ON \
-D BUILD_TBB=ON \
-D WITH_GSTREAMER=ON \
-D HIGHGUI_PLUGIN_LIST=gtk \
-D VIDEOIO_PLUGIN_LIST=all \
-D BUILD_TESTS=OFF \
-D WITH_EIGEN=OFF \
-D WITH_V4L=ON \
-D WITH_LIBV4L=ON \
-D WITH_VTK=OFF \
-D WITH_QT=OFF \
-D WITH_PROTOBUF=ON \
-D OPENCV_ENABLE_NONFREE=ON \
-D INSTALL_C_EXAMPLES=OFF \
-D INSTALL_PYTHON_EXAMPLES=ON \
-D PYTHON3_PACKAGES_PATH=/usr/lib/python3/dist-packages \
-D OPENCV_GENERATE_PKGCONFIG=ON \
-D BUILD_EXAMPLES=OFF ..

kiosk mode
https://www.raspberrypi.com/tutorials/how-to-use-a-raspberry-pi-in-kiosk-mode/
https://reelyactive.github.io/diy/pi-kiosk/  