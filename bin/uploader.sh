#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

SOL_NETORK="10.0.0"

BASE_PATH="/Users/zero/Develop/github.com/hadzimura/solrunners/"
SOURCE_PATH="${BASE_PATH}/media"
DEFAULT_DESTINATION_PATH="/home/zero/solrunners/media"
VIDEO_DESTINATION_PATH="/home/zero/solrunners/media/video"
AUDIO_DESTINATION_PATH="/home/zero/solrunners/media/audio"

BASHRC="/home/zero/.bashrc"

DEFAULT_SYNC=(fonts raspberry static templates)
ENTROPY_VIDEO_FOLDER="video/entropy"
ENTROPY_AUDIO_FOLDER="audio/entropy"
TATE_FOLDER="video/tate"
HEADS_FOLDER="video/heads"

if [[ -z "${1}" ]]; then
  echo "Need to specify the room to sync (1-5), exiting..."
  exit 1
fi

DESTINATION_IP=${1}

if [[ "${DESTINATION_IP}" == "test" ]]; then
  DESTINATION_HOST="tbuild01blade02.cz.o2"
  DESTINATION_USER="ra035312"
  DESTINATION_PATH="/home/ra035312/media"
  echo "Running testing scenario to '${DESTINATION_USER}@${DESTINATION_HOST}'"
else
  DESTINATION_USER="zero"
  # DESTINATION_HOST="${SOL_NETORK}.${DESTINATION_IP}"
  DESTINATION_HOST="room${DESTINATION_IP}"
  # echo "Running deployment scenario to '${DESTINATION_USER}@${DESTINATION_HOST}'"
  echo "Running deployment scenario to '${DESTINATION_HOST}'"
fi

DESTINATION="${DESTINATION_HOST}"

echo "Syncing default media folders"
for FOLDER in "${DEFAULT_SYNC[@]}"; do
  echo "Syncing ' ${SOURCE_PATH}/${FOLDER}' to host '${DESTINATION_HOST}'";
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
       rsync -azP --delete --mkpath ${SOURCE_PATH}/${ENTROPY_FOLDER} ${DESTINATION}:${VIDEO_DESTINATION_PATH} ;;
    4) echo "Syncing folder '${TATE_FOLDER}' to host '${DESTINATION_HOST}'"
       rsync -azP --delete --mkpath ${SOURCE_PATH}/${TATE_FOLDER} ${DESTINATION}:${VIDEO_DESTINATION_PATH} ;;
    5) echo "Syncing folder '${HEADS_FOLDER}' to host '${DESTINATION_HOST}'"
       # rsync -azP --delete --mkpath ${SOURCE_PATH}/${HEADS_FOLDER} ${DESTINATION}:${VIDEO_DESTINATION_PATH}
       rsync -azP --delete --mkpath ${SOURCE_PATH}/${ENTROPY_VIDEO_FOLDER} ${DESTINATION}:${VIDEO_DESTINATION_PATH}
       rsync -azP --delete --mkpath ${SOURCE_PATH}/${ENTROPY_AUDIO_FOLDER} ${DESTINATION}:${AUDIO_DESTINATION_PATH} ;;
    test) echo "Nothing to be done, only testing" ;;
esac

echo "All done"

