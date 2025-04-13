#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

SOURCE_VIDEO="/home/zero/solrunners/media/video"
SOURCE_AUDIO="/home/zero/solrunners/media/audio"
SOURCE_AUDIO="/home/zero/solrunners/media/static"
SOURCE_AUDIO="/home/zero/solrunners/media/templates"
DESTINATION="/storage"

echo "Syncing all the SoL Media from '${SOURCE}' into the SHM storage '${DESTINATION}'"

if [[ ! -d "${DESTINATION}" ]]; then
  echo "Destination folder does not exist ${DESTINATION}, exiting..."
  sudo df
  exit 1
fi

cp -r "${SOURCE_VIDEO}" "${DESTINATION}"
cp -r "${SOURCE_AUDIO}" "${DESTINATION}"

echo "All done"