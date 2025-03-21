#!/usr/bin/env bash

set -euo pipefail

log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

load_env_variables() {
  if [ -f .config/.env ]; then
    # shellcheck source=/dev/null
    source .config/.env
  else
    echo "Warning: .env file not found. Using default values."
    # DYNACONF_USER="default_user"
    # DYNACONF_EMAIL="default_email"
    DYNACONF_ATHLETE="default_athlete"
  fi
}

load_config_variables() {
  if [ -f .config/settings.toml ]; then
    # Call the Python script to process the configuration
    GOOGLE_DRIVE_DATA_PATH=$(python3 ./src/utils/config.py | grep "GOOGLE_DRIVE_DATA_PATH" | cut -d':' -f2- | xargs)
    GOOGLE_DRIVE_DATA_PATH+="/${ATHLETE}/log_archive/YML"
    log "DEBUG: GOOGLE_DRIVE_DATA_PATH = $GOOGLE_DRIVE_DATA_PATH"
  else
    log "Warning: .config/settings.toml file not found."
    GOOGLE_DRIVE_DATA_PATH="/Users/${USER}/Library/CloudStorage/GoogleDrive-${EMAIL}/My Drive/DATA/fitness-tracker-data/${ATHLETE}/log_archive/YML"
    log "DEBUG: GOOGLE_DRIVE_DATA_PATH = $GOOGLE_DRIVE_DATA_PATH"
  fi
}

load_env_variables
load_config_variables
# log "DEBUG: GOOGLE_DRIVE_DATA_PATH = $GOOGLE_DRIVE_DATA_PATH"

# Find all assisted bodyweight exercises in the workout logs.

cd "${GOOGLE_DRIVE_DATA_PATH}"

# grep -rnE --include="*.{yaml,yml}" "weight: BODYWEIGHT - .* kg" .

# using ripgrep
rg --glob="*.{yaml,yml}" "weight: BODYWEIGHT - .* kg"
