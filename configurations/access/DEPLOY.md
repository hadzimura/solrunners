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

echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINqhhcw3svD9s4+GniljpF7yGH6LnW/0K7PQUTyda2G9 room4@runner" >  /home/zero/.ssh/id_ed25519.pub
chmod 600 /home/zero/.ssh/id*