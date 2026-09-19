#!/usr/bin/env bash

set -euo pipefail

# BASH workflow that inserts data into a database and prepares figures.

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"

# shellcheck disable=SC2034
CONFIG_FILE="$PROJECT_ROOT/.config/fitcli.conf"

mkdir -p "$PROJECT_ROOT/logs"

if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="python"
fi
export PYTHON_BIN
# shellcheck disable=SC2034  # Read by validate_file_format in sourced validation.sh.
SUPPORTED_FILE_FORMATS=('yml' 'json')

# Load utility functions
UTILS_DIR="$SCRIPT_DIR/utils"

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
  if [[ -f "$PROJECT_ROOT/.config/settings.toml" ]]; then
    local config_output
    config_output=$(PYTHONPATH="$PROJECT_ROOT" "$PYTHON_BIN" -m src.utils.config)
    FITNESS_TRACKER_DATA_DIR=$(printf '%s\n' "$config_output" | awk -F': ' '/^DATA_DIR:/ {print $2}')
    IMG_PATH=$(printf '%s\n' "$config_output" | awk -F': ' '/^IMG_PATH:/ {print $2}')
    IMG_PATH="${IMG_PATH%/}/${YEAR_TO_PLOT}/"

    log "DEBUG: FITNESS_TRACKER_DATA_DIR = $FITNESS_TRACKER_DATA_DIR"
    log "DEBUG: IMG_PATH = $IMG_PATH"
  else
    log "Warning: .config/settings.toml file not found. Using environment defaults."
    IMG_PATH="${FITNESS_TRACKER_DATA_DIR%/}/img/${YEAR_TO_PLOT}/"
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
  local archive_format
  archive_format=$(printf '%s' "$FILE_FORMAT" | tr '[:lower:]' '[:upper:]')
  BASE_PATH="${FITNESS_TRACKER_DATA_DIR%/}/log_archive/${archive_format}/${YEAR}/${MONTH_NAME}"

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

    # run pydantic validation on the workout file
    if ! "$PYTHON_BIN" "$PROJECT_ROOT/src/utils/validate.py" --file "${WORKOUT_FILES[$i]}"; then
      log "Error: Validation failed for file ${WORKOUT_FILES[$i]}."
      continue
    fi

    if ! "$PYTHON_BIN" "$PROJECT_ROOT/src/crud/insert.py" \
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
  CONFIG_FILE="${CONFIG_FILE:-$PROJECT_ROOT/.config/fitcli.conf}"
  # shellcheck disable=SC2034
  LOG_FILE="$PROJECT_ROOT/logs/fitcli.log"
  # shellcheck disable=SC2034
  parse_arguments "$@"

  if ! validate_file_format "$FILE_FORMAT"; then
    log "Error: Unsupported file format: $FILE_FORMAT"
    exit 1
  fi

  # Set default WORKOUT_DATE only if not provided via -d
  if [[ -z "${WORKOUT_DATE:-}" ]]; then
    WORKOUT_DATE=$(date +%F)
    WORKOUT_DATES=("$WORKOUT_DATE")  # Default to today's date
  fi

  if ! validate_date "$WORKOUT_DATE"; then
    exit 1
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

  log "DEBUG: FITNESS_TRACKER_DATA_DIR = $FITNESS_TRACKER_DATA_DIR"
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
