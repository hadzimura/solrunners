#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

# Environmental Variables
# export SOL="audio"
# export SOL="video"
# export ROOM=1
# export ROOM=2
# export ROOM=3
# export ROOM=4
# export ROOM=5
export PYTHONPATH=$PYTHONPATH:${PWD}
export PYTHONUNBUFFERED=1
source .venv/bin/activate

# Variables
NODE="--no-master"
NODE_TYPE="Slave"

if [[ -z "${1}" ]]; then
  if [[ -z "${ROOM}" ]]; then
    echo "No Sol Runner type detected, use either <first> runtime argument or the <SOL> environmental variable to set"
    exit 1
  fi
else
  ROOM="${1}"
fi

if [[ "${ROOM}" -eq 1 ]]; then
  echo "Running as the Master Node"
  NODE="--master"
  NODE_TYPE="Master"
fi

echo "Launching the Sol Runner: ${ROOM} as '${NODE_TYPE}' Node"
python3 sol/runner.py --room "${ROOM}" "${NODE}"
