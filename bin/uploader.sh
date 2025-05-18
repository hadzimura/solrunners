#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

# Base paths
BASE_DEVEL_PATH="/Users/zero/Develop/github.com/hadzimura"
BASE_SSD_PATH="/Volumes/springs"
BASE_RPI_PATH="/home/zero/"
BASE_MEDIA_PATH="solrunners/media"

# Media
ENTROPY="${BASE_MEDIA_PATH}/entropy"
FOUNTAIN="${BASE_MEDIA_PATH}/fountain"
HEADS="${BASE_MEDIA_PATH}/heads"
TATE="${BASE_MEDIA_PATH}/tate"
EXIT="${BASE_MEDIA_PATH}/exit"
TEST="${BASE_MEDIA_PATH}/test"

# Service
BASHRC="/home/zero/.bashrc"

if [[ -z "${1}" ]]; then
  echo "Need to specify the instance to sync (entropy|fountain|heads|tate|exit), exiting..."
  exit 1
fi
INSTANCE="${1}"

if [[ -z "${2}" ]]; then
  echo "Need to specify the source for sync operation (devel|ssd), exiting..."
  exit 1
fi
SOURCE="${2}"

if [[ -z "${3}" ]]; then
  echo "Need to specify the destination for sync operation (ssd|rpi), exiting..."
  exit 1
fi
DESTINATION="${3}"

case "${SOURCE}" in
  devel)  SOURCE_PATH="${BASE_DEVEL_PATH}" ;;
  ssd)    SOURCE_PATH="${BASE_SSD_PATH}" ;;
  *)      echo "Undefined SOURCE (2), needs to be (devel|ssd). Exiting."
          exit 1 ;;
esac

case "${DESTINATION}" in
  rpi)    DESTINATION_PATH="${BASE_RPI_PATH}/${BASE_MEDIA_PATH}" ;;
  ssd)    DESTINATION_PATH="${BASE_SSD_PATH}/${BASE_MEDIA_PATH}" ;;
  *)      echo "Undefined DESTINATION (3), needs to be (rpi|ssd). Exiting."
          exit 1 ;;
esac

case "${INSTANCE}" in
  entropy)  SOURCE_PATH+="/${ENTROPY}"
            DESTINATION_HOST="10.0.0.3:${DESTINATION_PATH}" ;;
  fountain) SOURCE_PATH+="/${FOUNTAIN}"
            DESTINATION_HOST="10.0.0.1:${DESTINATION_PATH}" ;;
  heads)    SOURCE_PATH+="/${HEADS}"
            DESTINATION_HOST="10.0.0.4:${DESTINATION_PATH}" ;;
  tate)     SOURCE_PATH+="/${TATE}"
            DESTINATION_HOST="10.0.0.2:${DESTINATION_PATH}" ;;
  exit)     SOURCE_PATH+="/${EXIT}"
            DESTINATION_HOST="10.0.0.5:${DESTINATION_PATH}" ;;
  test)     SOURCE_PATH+="/${TEST}"
            DESTINATION_HOST="10.0.0.5:${DESTINATION_PATH}" ;;
  *)        echo "Undefined INSTANCE (1), needs to be (entropy|fountain|heads|tate|exit). Exiting."
            exit 1 ;;
esac

echo -e "--------------------------
Running sync operation for
  instance : ${INSTANCE}
  from     : ${SOURCE_PATH}"
case "${DESTINATION}" in
  rpi) echo "  to       : ${DESTINATION_HOST}" ;;
  ssd) echo "  to       : ${DESTINATION_PATH}" ;;
esac
echo "--------------------------"
read -p "Hit ENTER to sync..."

#echo "Syncing .bashrc"
#  rsync -azP --delete --mkpath ${BASE_DEVEL_PATH}/configurations/.bashrc ${DESTINATION}:${BASHRC}
#echo "Done syncing default media folders"

echo "Starting sync..."

case "${DESTINATION}" in
  rpi)  rsync -azP --delete --mkpath ${SOURCE_PATH} ${DESTINATION_HOST} ;;
  ssd)  rsync -azP --delete --mkpath ${SOURCE_PATH} ${DESTINATION_PATH} ;;
  test) rsync -azP --delete --mkpath ${SOURCE_PATH} ${DESTINATION_PATH} ;;
esac




#
#case "${INSTANCE}" in
#    entropy) echo "Host '${DESTINATION_HOST}' does not need additional syncing" ;;
#    fountain) echo "Host '${DESTINATION_HOST}' does not need additional syncing" ;;
#    3) echo "Syncing folder '${ENTROPY_FOLDER}' to host '${DESTINATION_HOST}'"
#       rsync -azP --delete --mkpath ${MEDIA_PATH}/${ENTROPY_VIDEO_FOLDER} ${DESTINATION}:${VIDEO_DESTINATION_PATH}
#       rsync -azP --delete --mkpath ${MEDIA_PATH}/${ENTROPY_AUDIO_FOLDER} ${DESTINATION}:${AUDIO_DESTINATION_PATH} ;;
#    4) echo "Syncing folder '${TATE_FOLDER}' to host '${DESTINATION_HOST}'"
#       rsync -azP --delete --mkpath ${MEDIA_PATH}/${TALKING_HEADS_AUDIO_FOLDER} ${DESTINATION}:${AUDIO_DESTINATION_PATH}
#       rsync -azP --delete --mkpath ${MEDIA_PATH}/${FOUNTAIN_AUDIO_FOLDER} ${DESTINATION}:${AUDIO_DESTINATION_PATH} ;;
#    5) echo "Syncing folder '${HEADS_VIDEO_FOLDER}' and '${HEADS_AUDIO_FOLDER}' to host '${DESTINATION_HOST}'"
#       # rsync -azP --delete --mkpath ${MEDIA_PATH}/${HEADS_FOLDER} ${DESTINATION}:${VIDEO_DESTINATION_PATH}
#       rsync -azP --delete --mkpath ${MEDIA_PATH}/${HEADS_VIDEO_FOLDER} ${DESTINATION}:${VIDEO_DESTINATION_PATH}
#       rsync -azP --delete --mkpath ${MEDIA_PATH}/${HEADS_AUDIO_FOLDER} ${DESTINATION}:${AUDIO_DESTINATION_PATH} ;;
#    test) echo "Nothing to be done, only testing" ;;
#esac

echo "All done"

