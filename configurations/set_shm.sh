#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

sudo mkdir /storage
sudo chown zero:zero /storage
sudo echo "tmpfs /storage tmpfs nodev,nosuid,size=1500M 0 0" >> /etc/fstab
sudo systemctl daemon-reload
sudo mount -a
