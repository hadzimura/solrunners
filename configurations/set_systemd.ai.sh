#!/usr/bin/env bash
# Deploy AI systemd services.

set -euo pipefail

if [[ -z "${1:-}" ]]; then
  echo "Service name needed: entropy | heads | fountain"
  exit 1
fi

TARGET="${1}"
UNIT=""

case "${TARGET}" in
  entropy)
    UNIT="sol.entropy.ai.service"
    ;;
  heads)
    UNIT="sol.heads.ai.service"
    ;;
  fountain)
    UNIT="sol.fountain.ai.service"
    ;;
  *)
    echo "Undefined service '${TARGET}', exiting..."
    exit 1
    ;;
esac

echo "Installing unit: ${UNIT}"
sudo cp "/home/zero/solrunners/configurations/systemd/${UNIT}" /etc/systemd/system/

# Ensure startup scripts are executable for xinit services.
if [[ "${TARGET}" == "entropy" ]]; then
  sudo chmod +x /home/zero/solrunners/configurations/xinit.entropy.ai.sh
fi
if [[ "${TARGET}" == "heads" ]]; then
  sudo chmod +x /home/zero/solrunners/configurations/xinit.heads.ai.sh
fi

echo "Reloading systemd and activating ${UNIT}"
sudo systemctl daemon-reload
sudo systemctl enable "${UNIT}"
sudo systemctl restart "${UNIT}"

echo "Done"

