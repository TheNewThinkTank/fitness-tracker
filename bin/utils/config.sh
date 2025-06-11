#!/usr/bin/env bash

load_config() {
  if [[ -f "$CONFIG_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$CONFIG_FILE"
  else
    log "Configuration file $CONFIG_FILE not found. Using default values."
  fi
}
