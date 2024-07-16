#!/usr/bin/env bash

set -euo pipefail

# Date: 2022-01-21
# Author: Gustav Collin Rasmussen
# Purpose: BASH workflow that inserts data into a database and prepares figures.

# Configuration file
CONFIG_FILE="./fitcli.conf"

# Functions
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

validate_date() {
  date -d "$1" +"%Y-%m-%d" > /dev/null 2>&1
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
    source "$CONFIG_FILE"
  else
    log "Configuration file $CONFIG_FILE not found. Using default values."
  fi
}

# Default values
WORKOUT_DATE=$(date +%F)
YEAR_TO_PLOT=$(date +%Y)
MONTH_TO_PLOT=$(date +%B)
FILE_FORMAT='yml'
CONFIG_FILE='./fitcli.conf'
LOG_FILE='./fitcli.log'
IMG_PATH='./docs/project_docs/img/'
SUPPORTED_FILE_FORMATS=('yml' 'json' 'csv')

# Parse command-line arguments
while getopts ":d:f:c:h" opt; do
  case ${opt} in
    d )
      if validate_date "$OPTARG"; then
        WORKOUT_DATE=$OPTARG
      else
        log "Error: Invalid date format. Expected YYYY-MM-DD."
        exit 1
      fi
      ;;
    f )
      if validate_file_format "$OPTARG"; then
        FILE_FORMAT=$OPTARG
      else
        log "Error: Unsupported file format. Supported formats: ${SUPPORTED_FILE_FORMATS[*]}"
        exit 1
      fi
      ;;
    c )
      CONFIG_FILE=$OPTARG
      ;;
    h )
      show_help
      exit 0
      ;;
    \? )
      log "Invalid option: -$OPTARG"
      show_help
      exit 1
      ;;
    : )
      log "Invalid option: -$OPTARG requires an argument"
      show_help
      exit 1
      ;;
  esac
done

# Load configuration
load_config

# Check dependencies
check_dependencies

log "Workflow started"
log "Workout date: $WORKOUT_DATE, File format: $FILE_FORMAT"

insert_data "$FILE_FORMAT" "$WORKOUT_DATE"
prepare_figures "$YEAR_TO_PLOT" "$MONTH_TO_PLOT"
open_images "$YEAR_TO_PLOT" "$MONTH_TO_PLOT"

log "Workflow completed successfully"
