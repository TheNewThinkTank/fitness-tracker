#!/usr/bin/env bash

load_env_variables() {
  if [ -f .config/.env ]; then
    set -a
    # shellcheck source=/dev/null
    source .config/.env
    set +a  
  else
    echo "Warning: .env file not found. Using default values."
    # DYNACONF_USER="default_user"
    # DYNACONF_EMAIL="default_email"
    # DYNACONF_ATHLETE="default_athlete"
  fi
}

validate_env_variables() {
  local required_vars=("USER" "EMAIL" "ATHLETE")
  for var in "${required_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
      log "Error: Environment variable $var is not set."
      exit 1
    fi
  done
}
