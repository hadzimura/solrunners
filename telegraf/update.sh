#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

sudo -i
cp -rf /home/zero/solrunners/telegraf.conf /etc/telegraf
service telegraf restart
