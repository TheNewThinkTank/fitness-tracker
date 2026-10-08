#!/usr/bin/env bash

prepare_figures() {
  local year=$1
  local month=$2
  if ! "$PYTHON_BIN" "$PROJECT_ROOT/src/combined_metrics/combined_metrics.py" \
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
  local opener
  if command -v open >/dev/null 2>&1; then
    opener=open
  elif command -v xdg-open >/dev/null 2>&1; then
    opener=xdg-open
  else
    log "Figures saved in $IMG_PATH; no desktop image viewer available."
    return 0
  fi
  "$opener" "${IMG_PATH}${year}_workout_frequency.png" || { log "Error: Failed to open image ${year}_workout_frequency.png"; exit 1; }
  "$opener" "${IMG_PATH}workout_duration_${month}_${year}.png" || { log "Error: Failed to open image workout_duration_${month}_${year}.png"; exit 1; }
}
