#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

SOURCE_VIDEO="/home/zero/solrunners/media/video"
SOURCE_AUDIO="/home/zero/solrunners/media/audio"
SOURCE_STATIC="/home/zero/solrunners/media/static"
SOURCE_TEMPLATES="/home/zero/solrunners/media/templates"
DESTINATION="/storage"

echo "Syncing all the SoL Media from '${SOURCE}' into the SHM storage '${DESTINATION}'"

if [[ ! -d "${DESTINATION}" ]]; then
  echo "Destination folder does not exist ${DESTINATION}, exiting..."
  sudo df
  exit 1
fi

echo "Syncing all the SoL Media from '${SOURCE_VIDEO}' into the SHM storage '${DESTINATION}'"
cp -r "${SOURCE_VIDEO}" "${DESTINATION}"
echo "Syncing all the SoL Media from '${SOURCE_AUDIO}' into the SHM storage '${DESTINATION}'"
cp -r "${SOURCE_AUDIO}" "${DESTINATION}"
echo "Syncing all the SoL Media from '${SOURCE_STATIC}' into the SHM storage '${DESTINATION}'"
cp -r "${SOURCE_STATIC}" "${DESTINATION}"
echo "Syncing all the SoL Media from '${SOURCE_TEMPLATES}' into the SHM storage '${DESTINATION}'"
cp -r "${SOURCE_TEMPLATES}" "${DESTINATION}"

touch /storage/.ready

echo "All done"