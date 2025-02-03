#!/usr/bin/env bash

set -euo pipefail

# BASH workflow that inserts data into a database and prepares figures.

CONFIG_FILE=".config/fitcli.conf"

# Functions
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

validate_date() {
  local input_date="$1"
  echo "Validating date: $input_date"

  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS date command
    if date -j -f "%Y-%m-%d" "$input_date" > /dev/null 2>&1; then
      echo "Date is valid."
      return 0
    else
      echo "Date is invalid."
      return 1
    fi
  else
    # Linux date command
    if date -d "$input_date" +"%Y-%m-%d" > /dev/null 2>&1; then
      echo "Date is valid."
      return 0
    else
      echo "Date is invalid."
      return 1
    fi
  fi
}

validate_file_format() {
  local format=$1
  for supported_format in "${SUPPORTED_FILE_FORMATS[@]}"; do
    if [[ "$supported_format" == "$format" ]]; then
      return 0
    fi
  done
  return 1
}

prepare_figures() {
  local year=$1
  local month=$2
  if ! python3 ./src/combined_metrics/combined_metrics.py \
    --year_to_plot "$year" \
    --month_to_plot "$month"; then
    log "Error: Failed to prepare figures."
    exit 1
  fi
  log "Figures prepared successfully."
}

open_images() {
  local year=$1
  local month=$2
  open "${IMG_PATH}${year}_workout_frequency.png" || { log "Error: Failed to open image ${year}_workout_frequency.png"; exit 1; }
  open "${IMG_PATH}workout_duration_${month}_${year}.png" || { log "Error: Failed to open image workout_duration_${month}_${year}.png"; exit 1; }
}

show_help() {
  echo "Usage: fitcli [-d WORKOUT_DATE] [-f FILE_FORMAT] [-c CONFIG_FILE]"
  echo ""
  echo "Options:"
  echo "  -d WORKOUT_DATE    Specify the workout date (default: today)"
  echo "  -f FILE_FORMAT     Specify the file format (default: yml)"
  echo "  -c CONFIG_FILE     Specify the configuration file (default: ./fitcli.conf)"
  echo "  -h                 Show this help message"
}

check_dependencies() {
  command -v python3 >/dev/null 2>&1 || { log "Python3 is required but it's not installed. Aborting."; exit 1; }
  command -v open >/dev/null 2>&1 || { log "'open' command is required but it's not installed. Aborting."; exit 1; }
}

load_config() {
  if [[ -f "$CONFIG_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$CONFIG_FILE"
  else
    log "Configuration file $CONFIG_FILE not found. Using default values."
  fi
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
    IMG_PATH=$(python3 ./src/utils/config.py | grep "IMG_PATH" | cut -d':' -f2- | xargs)
    IMG_PATH="${IMG_PATH}${YEAR_TO_PLOT}/"

    log "DEBUG: GOOGLE_DRIVE_DATA_PATH = $GOOGLE_DRIVE_DATA_PATH"
    log "DEBUG: IMG_PATH = $IMG_PATH"
  else
    log "Warning: .config/settings.toml file not found. Using default img_path."
    IMG_PATH="/Users/${USER}/Library/CloudStorage/GoogleDrive-${EMAIL}/My Drive/DATA/fitness-tracker-data/${ATHLETE}/img/2025/"
  fi
}

validate_env_variables() {
  local required_vars=("USER" "EMAIL" "ATHLETE")
  for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
      log "Error: Environment variable $var is not set."
      exit 1
    fi
  done
}

parse_arguments() {
  while getopts ":d:f:c:h" opt; do
    case ${opt} in
      d )
        WORKOUT_DATE=$OPTARG
        WORKOUT_DATES=("$WORKOUT_DATE")  # Initialize WORKOUT_DATES with the provided date
        ;;
      f )
        FILE_FORMAT=$OPTARG
        ;;
      c )
        CONFIG_FILE=$OPTARG
        ;;
      h )
        echo "Usage: $0 [-d WORKOUT_DATE] [-f FILE_FORMAT] [-c CONFIG_FILE]"
        exit 0
        ;;
      \? )
        echo "Invalid option: $OPTARG" 1>&2
        exit 1
        ;;
      : )
        echo "Invalid option: $OPTARG requires an argument" 1>&2
        exit 1
        ;;
    esac
  done
  shift $((OPTIND -1))
}

get_month_name() {
  local month_num=$1
  case $month_num in
    01) echo "January" ;;
    02) echo "February" ;;
    03) echo "March" ;;
    04) echo "April" ;;
    05) echo "May" ;;
    06) echo "June" ;;
    07) echo "July" ;;
    08) echo "August" ;;
    09) echo "September" ;;
    10) echo "October" ;;
    11) echo "November" ;;
    12) echo "December" ;;
    *) echo "Invalid month number: $month_num" >&2; exit 1 ;;
  esac
}

main() {
  # Default values
  FILE_FORMAT='yml'
  CONFIG_FILE='./fitcli.conf'
  LOG_FILE='logs/fitcli.log'

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
    log "Processing for date: $workout_date"

    if [[ "$OSTYPE" == "darwin"* ]]; then
      # macOS date command
      YEAR=$(date -j -f "%Y-%m-%d" "$workout_date" +%Y)
      MONTH_NUM=$(date -j -f "%Y-%m-%d" "$workout_date" +%m)
    else
      # Linux date command
      YEAR=$(date -d "$workout_date" +%Y)
      MONTH_NUM=$(date -d "$workout_date" +%m)
    fi

    MONTH_NAME=$(get_month_name "$MONTH_NUM")
    BASE_PATH="${GOOGLE_DRIVE_DATA_PATH}/${DYNACONF_ATHLETE}/log_archive/${FILE_FORMAT^^}/${YEAR}/${MONTH_NAME}"

    log "BASE_PATH: $BASE_PATH"

    # Find all workout files for the given date
    WORKOUT_FILES=()
    while IFS= read -r -d '' file; do
      WORKOUT_FILES+=("$file")
    done < <(find "$BASE_PATH" -name "*training_log_${workout_date}*.${FILE_FORMAT}" -print0)

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

        # exit 1
        continue  # Skip to the next file instead of exiting

      fi
      log "Data from file ${WORKOUT_FILES[$i]} inserted into the database."
    done

    prepare_figures "$YEAR" "$MONTH_NAME"
    open_images "$YEAR" "$MONTH_NAME"
  done

  log "Workflow completed successfully"
}

# Execute main if the script is run directly
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
