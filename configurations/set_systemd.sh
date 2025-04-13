#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

if [[ -z "${1}" ]]; then
  echo "Service name needed! (storage|sol|...)"
fi

SERVICE="${1}"

echo "Deploying SystemD service '${SERVICE}'"

case "${SERVICE}" in

  storage)
    sudo cp /home/zero/solrunners/configurations/systemd/storage.service /etc/systemd/system/
    ;;
  *)
    echo "Undefined service name '${SERVICE}', exiting..."
    exit 1 ;;
esac

echo "Reloading daemons now..."
sudo systemctl daemon-reload
echo "Enabling and starting '${SERVICE}.service'"
sudo systemctl enable "${SERVICE}.service"
sudo systemctl start "${SERVICE}.service"
echo "All done"
