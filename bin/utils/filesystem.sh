#!/usr/bin/env bash

find_workout_files() {
  local base_path="$1"
  local workout_date="$2"
  local file_format="$3"

  if [[ ! -d "$base_path" ]]; then
    return 0
  fi

  find "$base_path" -name "*training_log_${workout_date}*.${file_format}" -print0
}
