#!/usr/bin/env bash

set -euo pipefail

# Load USER, EMAIL, and ATHLETE from the .env file
if [ -f .config/.env ]; then
  # shellcheck source=/dev/null
  source .config/.env
else
  echo "Warning: .env file not found. Using default values."
  USER="default_user"
  EMAIL="default_email"
  ATHLETE="default_athlete"
fi

# Read img_path from config.yml
if [ -f .config/settings.toml ]; then
  # Load variables from settings.toml
  GOOGLE_DRIVE_DATA_PATH=$(tomlq -r '.default.GOOGLE_DRIVE_DATA_PATH' .config/settings.toml | sed "s/{{ env.USER }}/${USER}/g; s/{{ env.EMAIL }}/${EMAIL}/g")
  IMG_PATH=$(tomlq -r '.default.img_path' .config/settings.toml | sed "s/{{ this.google_drive_data_path }}/${GOOGLE_DRIVE_DATA_PATH}/g; s/{{ env.ATHLETE }}/${ATHLETE}/g")
  IMG_PATH="${IMG_PATH}${YEAR_TO_PLOT}/"
  
  echo "$GOOGLE_DRIVE_DATA_PATH"  # /Users/$USER/Library/CloudStorage/GoogleDrive-$EMAIL/My Drive/DATA/fitness-tracker-data
  echo "$IMG_PATH"  # $GOOGLE_DRIVE_DATA_PATH/$ATHLETE/img/
else
  echo "Warning: .config/settings.toml file not found. Using default img_path."
  IMG_PATH="/Users/${USER}/Library/CloudStorage/GoogleDrive-${EMAIL}/My Drive/DATA/fitness-tracker-data/${ATHLETE}/img/2025/"
fi
