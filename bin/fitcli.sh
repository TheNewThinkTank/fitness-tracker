#!/usr/bin/env bash

set -euo pipefail

# BASH workflow that inserts data into a database and prepares figures.

# shellcheck disable=SC2034
CONFIG_FILE=".config/fitcli.conf"

mkdir -p logs

# Load utility functions
UTILS_DIR="bin/utils"

# shellcheck disable=SC1091
source "${UTILS_DIR}/logging.sh"
# shellcheck disable=SC1091
source "${UTILS_DIR}/validation.sh"
# shellcheck disable=SC1091
source "${UTILS_DIR}/config.sh"
# shellcheck disable=SC1091
source "${UTILS_DIR}/filesystem.sh"
# shellcheck disable=SC1091
source "${UTILS_DIR}/date.sh"
# shellcheck disable=SC1091
source "${UTILS_DIR}/env.sh"
# shellcheck disable=SC1091
source "${UTILS_DIR}/help.sh"
# shellcheck disable=SC1091
source "${UTILS_DIR}/args.sh"
# shellcheck disable=SC1091
source "${UTILS_DIR}/figures.sh"

load_config_variables() {
  if [ -f .config/settings.toml ]; then
    # Call the Python script to process the configuration
    GOOGLE_DRIVE_DATA_PATH=$(python3 ./src/utils/config.py | grep "GOOGLE_DRIVE_DATA_PATH" | cut -d':' -f2- | xargs)
    IMG_PATH=$(python3 ./src/utils/config.py | grep "IMG_PATH" | cut -d':' -f2- | xargs)
    IMG_PATH="${IMG_PATH}${YEAR_TO_PLOT}/"

    log "DEBUG: GOOGLE_DRIVE_DATA_PATH = $GOOGLE_DRIVE_DATA_PATH"
    log "DEBUG: IMG_PATH = $IMG_PATH"
  else
    log "Warning: .config/settings.toml file not found. Using default img_path."
    IMG_PATH="/Users/${USER}/Library/CloudStorage/GoogleDrive-${EMAIL}/My Drive/DATA/fitness-tracker-data/${ATHLETE}/img/2025/"
  fi
}

process_workout_date() {
  local workout_date="$1"

  log "Processing for date: $workout_date"

  if [[ "$OSTYPE" == "darwin"* ]]; then
    YEAR=$(date -j -f "%Y-%m-%d" "$workout_date" +%Y)
    MONTH_NUM=$(date -j -f "%Y-%m-%d" "$workout_date" +%m)
  else
    YEAR=$(date -d "$workout_date" +%Y)
    MONTH_NUM=$(date -d "$workout_date" +%m)
  fi

  MONTH_NAME=$(get_month_name "$MONTH_NUM")
  BASE_PATH="${GOOGLE_DRIVE_DATA_PATH}/${DYNACONF_ATHLETE}/log_archive/${FILE_FORMAT^^}/${YEAR}/${MONTH_NAME}"

  log "BASE_PATH: $BASE_PATH"

  WORKOUT_FILES=()
  while IFS= read -r -d '' file; do
    WORKOUT_FILES+=("$file")
  done < <(find_workout_files "$BASE_PATH" "$workout_date" "$FILE_FORMAT")

  if [[ ${#WORKOUT_FILES[@]} -eq 0 ]]; then
    log "Error: No workout files found for date $workout_date."
    exit 1
  fi

  log "Found ${#WORKOUT_FILES[@]} workout files for date $workout_date."

  for ((i = 0; i < ${#WORKOUT_FILES[@]}; i++)); do
    WORKOUT_NUMBER=$((i + 1))
    log "Processing workout file: ${WORKOUT_FILES[$i]} (Workout number: $WORKOUT_NUMBER)"
    if ! python3 ./src/crud/insert.py \
      --file_format "$FILE_FORMAT" \
      --datatype real \
      --dates "$workout_date" \
      --workout_number "$WORKOUT_NUMBER"; then
      log "Error: Failed to insert data from file ${WORKOUT_FILES[$i]} into the database."
      continue
    fi
    log "Data from file ${WORKOUT_FILES[$i]} inserted into the database."
  done

  prepare_figures "$YEAR" "$MONTH_NAME"
  open_figures "$YEAR" "$MONTH_NAME"
}

main() {
  # Default values
  FILE_FORMAT='yml'
  # shellcheck disable=SC2034
  CONFIG_FILE='./fitcli.conf'
  # shellcheck disable=SC2034
  LOG_FILE='logs/fitcli.log'
  # shellcheck disable=SC2034
  SUPPORTED_FILE_FORMATS=('yml' 'json' 'csv')

  parse_arguments "$@"

  # Set default WORKOUT_DATE only if not provided via -d
  if [[ -z "${WORKOUT_DATE:-}" ]]; then
    WORKOUT_DATE=$(date +%F)
    WORKOUT_DATES=("$WORKOUT_DATE")  # Default to today's date
  fi

  # Calculate YEAR_TO_PLOT and MONTH_TO_PLOT based on WORKOUT_DATE
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS date command
    YEAR_TO_PLOT=$(date -j -f "%Y-%m-%d" "$WORKOUT_DATE" +%Y)
    # MONTH_TO_PLOT=$(date -j -f "%Y-%m-%d" "$WORKOUT_DATE" +%B)
  else
    # Linux date command
    YEAR_TO_PLOT=$(date -d "$WORKOUT_DATE" +%Y)
    # MONTH_TO_PLOT=$(date -d "$WORKOUT_DATE" +%B)
  fi

  load_env_variables
  validate_env_variables
  load_config_variables  # This depends on YEAR_TO_PLOT, so it must be called after YEAR_TO_PLOT is set

  log "DEBUG: GOOGLE_DRIVE_DATA_PATH = $GOOGLE_DRIVE_DATA_PATH"
  log "DEBUG: IMG_PATH = $IMG_PATH"

  load_config
  check_dependencies

  log "Workflow started"

  for workout_date in "${WORKOUT_DATES[@]}"; do
    process_workout_date "$workout_date"
  done

  log "Workflow completed successfully"
}

# Execute main if the script is run directly
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
