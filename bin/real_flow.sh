#!/usr/bin/env bash

set -euo pipefail

# Date: 2022-01-21
# Author: Gustav Collin Rasmussen
# Purpose: BASH workflow that inserts data into a database and prepares figures.

# datatype values: real/simulated

# Constants
IMG_PATH='./docs/project_docs/img/'

# Functions
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
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
  open "${IMG_PATH}${year}_workout_frequency.png"
  open "${IMG_PATH}workout_duration_${month}_${year}.png"
}

# Main script
WORKOUT_DATE=$(date +%F)  # '2024-02-23'  # 2022-03-02,2022-03-03
YEAR_TO_PLOT=$(date +%Y)  # "2024"
MONTH_TO_PLOT=$(date +%B)  # "August"
# TRAINING_PROGRAM='nfp'  # 'gvt'
FILE_FORMAT='yml'  # default is json

# --workout_number 2

log "Workflow started"
log "Workout date: $WORKOUT_DATE, File format: $FILE_FORMAT"

insert_data "$FILE_FORMAT" "$WORKOUT_DATE"
prepare_figures "$YEAR_TO_PLOT" "$MONTH_TO_PLOT"

if ! open_images "$YEAR_TO_PLOT" "$MONTH_TO_PLOT"; then
  log "Error: Failed to open images."
  exit 1
fi

log "Workflow completed successfully"
