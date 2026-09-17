#!/usr/bin/env bash

load_env_variables() {
  local project_root="${PROJECT_ROOT:-$PWD}"
  if [[ -f "$project_root/.env" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "$project_root/.env"
    set +a
  fi

  FITNESS_TRACKER_DATA_DIR="${FITNESS_TRACKER_DATA_DIR:-$project_root/data}"
  if [[ "$FITNESS_TRACKER_DATA_DIR" != /* ]]; then
    FITNESS_TRACKER_DATA_DIR="$project_root/$FITNESS_TRACKER_DATA_DIR"
  fi
  export FITNESS_TRACKER_DATA_DIR
  export FITNESS_TRACKER_ATHLETE="${FITNESS_TRACKER_ATHLETE:-default}"
}

validate_env_variables() {
  if [[ ! -d "$FITNESS_TRACKER_DATA_DIR" ]]; then
    log "Error: FITNESS_TRACKER_DATA_DIR is not a directory: $FITNESS_TRACKER_DATA_DIR"
    exit 1
  fi
}
