#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

SOL_NETORK="10.0.0"

BASE_PATH="/Users/zero/Develop/github.com/hadzimura/solrunners"
SOURCE_PATH="${BASE_PATH}/media"
DEFAULT_DESTINATION_PATH="/home/zero/solrunners/media"
VIDEO_DESTINATION_PATH="/home/zero/solrunners/media/video"
AUDIO_DESTINATION_PATH="/home/zero/solrunners/media/audio"

BASHRC="/home/zero/.bashrc"

DEFAULT_SYNC=(fonts raspberry static templates)
ENTROPY_VIDEO_FOLDER="video/entropy"
ENTROPY_AUDIO_FOLDER="audio/entropy"
TATE_FOLDER="video/tate"
HEADS_VIDEO_FOLDER="video/heads"
HEADS_AUDIO_FOLDER="audio/heads"
TALKING_HEADS_AUDIO_FOLDER="audio/talking_heads"

if [[ -z "${1}" ]]; then
  echo "Need to specify the room to sync (1-5), exiting..."
  exit 1
fi

DESTINATION_IP=${1}
DESTINATION_USER="zero"
# DESTINATION_HOST="${SOL_NETORK}.${DESTINATION_IP}"
DESTINATION_HOST="room${DESTINATION_IP}"
echo "Running deployment scenario to '${DESTINATION_HOST}'"
DESTINATION="${DESTINATION_HOST}"

echo "Syncing default media folders"
for FOLDER in "${DEFAULT_SYNC[@]}"; do
  echo "Syncing '${SOURCE_PATH}/${FOLDER}' to host '${DESTINATION_HOST}'";
  rsync -azP --delete --mkpath ${SOURCE_PATH}/${FOLDER} ${DESTINATION}:${DEFAULT_DESTINATION_PATH}
done
echo "Done syncing default media folders"

echo "Syncing .bashrc"
  rsync -azP --delete --mkpath ${BASE_PATH}/configurations/.bashrc ${DESTINATION}:${BASHRC}
echo "Done syncing default media folders"


echo "Syncing additional media folders"
case "${DESTINATION_IP}" in
    1) echo "Host '${DESTINATION_HOST}' does not need additional syncing" ;;
    2) echo "Host '${DESTINATION_HOST}' does not need additional syncing" ;;
    3) echo "Syncing folder '${ENTROPY_FOLDER}' to host '${DESTINATION_HOST}'"
       rsync -azP --delete --mkpath ${SOURCE_PATH}/${ENTROPY_VIDEO_FOLDER} ${DESTINATION}:${VIDEO_DESTINATION_PATH}
       rsync -azP --delete --mkpath ${SOURCE_PATH}/${ENTROPY_AUDIO_FOLDER} ${DESTINATION}:${AUDIO_DESTINATION_PATH} ;;
    4) echo "Syncing folder '${TATE_FOLDER}' to host '${DESTINATION_HOST}'"
       # rsync -azP --delete --mkpath ${SOURCE_PATH}/${TATE_FOLDER} ${DESTINATION}:${VIDEO_DESTINATION_PATH}
       rsync -azP --delete --mkpath ${SOURCE_PATH}/${TALKING_HEADS_AUDIO_FOLDER} ${DESTINATION}:${AUDIO_DESTINATION_PATH} ;;
    5) echo "Syncing folder '${HEADS_VIDEO_FOLDER}' and '${HEADS_AUDIO_FOLDER}' to host '${DESTINATION_HOST}'"
       # rsync -azP --delete --mkpath ${SOURCE_PATH}/${HEADS_FOLDER} ${DESTINATION}:${VIDEO_DESTINATION_PATH}
       rsync -azP --delete --mkpath ${SOURCE_PATH}/${HEADS_VIDEO_FOLDER} ${DESTINATION}:${VIDEO_DESTINATION_PATH}
       rsync -azP --delete --mkpath ${SOURCE_PATH}/${HEADS_AUDIO_FOLDER} ${DESTINATION}:${AUDIO_DESTINATION_PATH} ;;
    test) echo "Nothing to be done, only testing" ;;
esac

echo "All done"

