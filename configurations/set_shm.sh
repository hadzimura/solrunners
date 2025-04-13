#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

sudo mkdir /storage
sudo chown zero:zero /storage

# This goes into the /etc/fstab
# tmpfs /storage tmpfs nodev,nosuid,size=1.5G 0 0

sudo mount -a