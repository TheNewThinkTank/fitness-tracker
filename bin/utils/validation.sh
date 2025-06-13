#!/usr/bin/env bash

check_dependencies() {
  command -v python3 >/dev/null 2>&1 || { log "Python3 is required but it's not installed. Aborting."; exit 1; }
  command -v open >/dev/null 2>&1 || { log "'open' command is required but it's not installed. Aborting."; exit 1; }
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
