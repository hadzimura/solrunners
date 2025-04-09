#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

sudo cp /home/zero/solrunners/configurations/systemd/sol.service /etc/systemd/system/
# sudo cp /home/zero/solrunners/configurations/systemd/sol-watcher.service /etc/systemd/system/
# sudo cp /home/zero/solrunners/configurations/systemd/sol-watcher.path /etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl enable sol.service
# sudo systemctl enable sol-watcher.service

sudo systemctl start sol.service
# sudo systemctl start sol-watcher.service