#!/usr/bin/env bash

set -euo pipefail

# Load USER, EMAIL, and ATHLETE from the .env file
if [ -f .env ]; then
  # shellcheck source=/dev/null
  source .env
else
  echo "Warning: .env file not found. Using default values."
  USER="default_user"
  EMAIL="default_email"
  ATHLETE="default_athlete"
fi

# Read img_path from config.yml
if [ -f .config/config.yml ]; then
  GOOGLE_DRIVE_DATA_PATH=$(yq e '.google_drive_data_path' .config/config.yml | sed "s/<USER>/$USER/g; s/<EMAIL>/$EMAIL/g")
  IMG_PATH=$(yq e '.img_path' .config/config.yml | sed "s|<GOOGLE_DRIVE_DATA_PATH>|$GOOGLE_DRIVE_DATA_PATH|g; s/<ATHLETE>/$ATHLETE/g")
  echo $GOOGLE_DRIVE_DATA_PATH  # /Users/$USER/Library/CloudStorage/GoogleDrive-$EMAIL/My Drive/DATA/fitness-tracker-data
  echo $IMG_PATH  # $GOOGLE_DRIVE_DATA_PATH/$ATHLETE/img/
else
  echo "Warning: config.yml file not found. Using default img_path."
  IMG_PATH="/Users/${USER}/Library/CloudStorage/GoogleDrive-${EMAIL}/My Drive/DATA/fitness-tracker-data/${ATHLETE}/img/2025/"
fi
