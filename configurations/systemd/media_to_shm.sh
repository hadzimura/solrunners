#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

SOURCE="/home/zero/solrunners/media/video"
DESTINATION="/storage"

echo "Syncing all the SoL Media from '${SOURCE}' into the SHM storage '${DESTINATION}'"

if [[ ! -d "${DESTINATION}" ]]; then
  echo "Destination folder does not exist ${DESTINATION}, exiting..."
  sudo df
  exit 1
fi

cp -r "${SOURCE}" "${DESTINATION}"

echo "All done"