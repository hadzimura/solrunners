#!/bin/bash

if [[ -z "${1}" ]]; then
  echo "Specify source folder as first runtime argument"
  exit 1
elif [[ ! -d "${1}" ]]; then
  echo "Source folder '${1}' does not exist, exiting..."
  exit 1
fi

if [[ -z "${2}" ]]; then
  echo "Specify target channel (left|right) as second runtime argument"
  exit 1
elif [[ "${2}" != "left" && "${2}" != "right" ]]; then
  echo "Only (left|right) is available for channel setting, exiting..."
elif [[ "${2}" == "left" ]]; then
  FF_PAN="pan=stereo|c0=c0"
elif [[ "${2}" == "right" ]]; then
  FF_PAN="pan=stereo|c1=c1"
fi

SOURCE_FOLDER="${1}"
TARGET_CHANNEL="${2}"
DESTINATION_FOLDER="${SOURCE_FOLDER}/${TARGET_CHANNEL}"

echo "Mixing WAV mono files from folder '${SOURCE_FOLDER}' to '${TARGET_CHANNEL}' stereo channel"
echo "Rendered files will be available within the '${DESTINATION_FOLDER}'"

if [[ -d "${DESTINATION_FOLDER}" ]]; then
  echo "Destination folder already exists: '${DESTINATION_FOLDER}', please remove the folder first..."
  exit 1
else
  echo "Creating destination folder: '${DESTINATION_FOLDER}'"
  mkdir -p "${DESTINATION_FOLDER}"
fi

for INPUT_FILE in "${SOURCE_FOLDER}"/*.wav
do

    TEMP_FILE="${SOURCE_FOLDER}/$(basename "${INPUT_FILE}" .wav).temp.wav"
    FINAL_FILE="${SOURCE_FOLDER}/${TARGET_CHANNEL}/$(basename "${INPUT_FILE}" .wav).${TARGET_CHANNEL}.wav"
    ffmpeg -i "${INPUT_FILE}" -filter_complex "[0:a][0:a]amerge=inputs=2[a]" -map "[a]" "${TEMP_FILE}"
    ffmpeg -i "${TEMP_FILE}" -af "${FF_PAN}" "${FINAL_FILE}"
    rm "${TEMP_FILE}"

done
