# Runners

Image: `Raspberry PI OS (64 bit)`

| hostname | ip address | wlan0 MAC            |
|----------|------------|----------------------|
| room1    | 10.0.0.1   | `B8:27:EB:19:5D:5C ` |
| room2    | 10.0.0.2   |                      |
| room3    | 10.0.0.3   | `2C:CF:67:5B:80:DB`  |
| room4    | 10.0.0.4   | `2C:CF:67:AB:95:2A`  |
| room5    | 10.0.0.5   | `2C:CF:67:5B:7E:D2`  |

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

fi