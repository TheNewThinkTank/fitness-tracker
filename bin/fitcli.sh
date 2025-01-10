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

insert_data() {
  local file_format=$1
  local workout_date=$2
  if ! python3 ./src/crud/insert.py --file_format "$file_format" --datatype real --dates "$workout_date"; then
    log "Error: Failed to insert data in database."
    exit 1
  fi
  log "Data inserted in database."
}

prepare_figures() {
  local year=$1
  local month=$2
  if ! python3 ./src/combined_metrics/combined_metrics.py --year_to_plot "$year" --month_to_plot "$month"; then
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

# Load USER, EMAIL, and ATHLETE from the .env file
load_env_variables() {
  if [ -f .env ]; then
    # shellcheck source=/dev/null
    source .env
  else
    echo "Warning: .env file not found. Using default values."
    USER="default_user"
    EMAIL="default_email"
    ATHLETE="default_athlete"
  fi
}

# Read img_path from config.yml
load_config_variables() {
  if [ -f .config/config.yml ]; then
    GOOGLE_DRIVE_DATA_PATH=$(yq e '.google_drive_data_path' .config/config.yml | sed "s/<USER>/$USER/g; s/<EMAIL>/$EMAIL/g")
    IMG_PATH=$(yq e '.img_path' .config/config.yml | sed "s|<GOOGLE_DRIVE_DATA_PATH>|$GOOGLE_DRIVE_DATA_PATH|g; s/<ATHLETE>/$ATHLETE/g")
    IMG_PATH="${IMG_PATH}${YEAR_TO_PLOT}/"
    echo "$GOOGLE_DRIVE_DATA_PATH"  # /Users/$USER/Library/CloudStorage/GoogleDrive-$EMAIL/My Drive/DATA/fitness-tracker-data
    echo "$IMG_PATH"  # $GOOGLE_DRIVE_DATA_PATH/$ATHLETE/img/
  else
    echo "Warning: config.yml file not found. Using default img_path."
    IMG_PATH="/Users/${USER}/Library/CloudStorage/GoogleDrive-${EMAIL}/My Drive/DATA/fitness-tracker-data/${ATHLETE}/img/2025/"
  fi
}

# Parse command-line arguments
parse_arguments() {
  while getopts ":d:f:c:h" opt; do
    case ${opt} in
      d )
        WORKOUT_DATE=$OPTARG
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

# Main function for script execution
main() {
  # Code to be executed when the script is run directly

  # Default values
  WORKOUT_DATE=$(date +%F)
  YEAR_TO_PLOT=$(date +%Y)
  MONTH_TO_PLOT=$(date +%B)
  FILE_FORMAT='yml'
  CONFIG_FILE='./fitcli.conf'
  LOG_FILE='logs/fitcli.log'

  load_env_variables

  load_config_variables

  SUPPORTED_FILE_FORMATS=('yml' 'json' 'csv')

  # Parse command-line arguments
  WORKOUT_DATES=()  # Initialize an array for multiple dates

  # while getopts ":d:f:c:h" opt; do
  #   case ${opt} in
  #     d )
  #       IFS=',' read -r -a input_dates <<< "$OPTARG"
  #       for date in "${input_dates[@]}"; do
  #         if validate_date "$date"; then
  #           WORKOUT_DATES+=("$date")
  #         else
  #           log "Error: Invalid date format. Expected YYYY-MM-DD."
  #           exit 1
  #         fi
  #       done
  #       ;;
  #     f )
  #       if validate_file_format "$OPTARG"; then
  #         FILE_FORMAT=$OPTARG
  #       else
  #         log "Error: Unsupported file format. Supported formats: ${SUPPORTED_FILE_FORMATS[*]}"
  #         exit 1
  #       fi
  #       ;;
  #     c )
  #       CONFIG_FILE=$OPTARG
  #       ;;
  #     h )
  #       show_help
  #       exit 0
  #       ;;
  #     \? )
  #       log "Invalid option: -$OPTARG"
  #       show_help
  #       exit 1
  #       ;;
  #     : )
  #       log "Invalid option: -$OPTARG requires an argument"
  #       show_help
  #       exit 1
  #       ;;
  #   esac
  # done

  # Default to today's date if none provided
  if [[ ${#WORKOUT_DATES[@]} -eq 0 ]]; then
    mapfile -t WORKOUT_DATES < <(date +%F)
  fi

  parse_arguments "$@"

  # Load configuration
  load_config

  # Check dependencies
  check_dependencies

  log "Workflow started"
  log "Workout date: $WORKOUT_DATE, File format: $FILE_FORMAT"

  # insert_data "$FILE_FORMAT" "$WORKOUT_DATE"
  # Process each date
  for workout_date in "${WORKOUT_DATES[@]}"; do
    log "Processing for date: $workout_date"
    insert_data "$FILE_FORMAT" "$workout_date"
  done

  prepare_figures "$YEAR_TO_PLOT" "$MONTH_TO_PLOT"
  open_images "$YEAR_TO_PLOT" "$MONTH_TO_PLOT"

  log "Workflow completed successfully"
}

# Execute main if the script is run directly
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
