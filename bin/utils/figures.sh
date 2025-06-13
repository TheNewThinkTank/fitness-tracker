#!/usr/bin/env bash

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

open_figures() {
  local year=$1
  local month=$2
  open "${IMG_PATH}${year}_workout_frequency.png" || { log "Error: Failed to open image ${year}_workout_frequency.png"; exit 1; }
  open "${IMG_PATH}workout_duration_${month}_${year}.png" || { log "Error: Failed to open image workout_duration_${month}_${year}.png"; exit 1; }
}
