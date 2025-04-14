#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

sudo cp -rf /home/zero/solrunners/telegraf/telegraf.conf /etc/telegraf
sudo service telegraf restart
