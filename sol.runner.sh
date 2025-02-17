#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

source .venv/bin/activate

export PYTHONPATH=$PYTHONPATH:${PWD}
export PYTHONUNBUFFERED=1


set -e

NODE="--no-master"
NODE_TYPE="Slave"

if [[ -z "$2" ]]; then
  if [[ -z "${ROOM}" ]]; then
    echo "No Sol Runner type detected, use either <first> runtime argument or the <SOL> environmental variable to set"
    exit 1
  fi
else
  ROOM="${2}"
fi

if [[ -z "$1" ]]; then
  if [[ -z "${SOL}" ]]; then
    echo "No Sol Runner type detected, use either <first> runtime argument or the <SOL> environmental variable to set"
    exit 1
  fi
else
  SOL="${1}"
fi

if [[ "${SOL}" == 'audio' && "${ROOM}" -eq 1 ]]; then
  echo "Running as the Master Node"
  NODE="--master"
  NODE_TYPE="Master"
  echo "Launching the Sol Runner: ${SOL}:${ROOM} as '${NODE_TYPE}' Node"
  python3 audio.py --sol "${SOL}" --room "${ROOM}" "${NODE}"

elif [[ "${SOL}" == 'video' && "${ROOM}" -eq 3 ]]; then
  python3 sol-video/entro.py
fi

