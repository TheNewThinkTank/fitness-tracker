#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

if [[ -f "$PROJECT_ROOT/.env" ]]; then
  # shellcheck source=/dev/null
  source "$PROJECT_ROOT/.env"
fi

DATA_DIR="${FITNESS_TRACKER_DATA_DIR:-$PROJECT_ROOT/data}"
if [[ "$DATA_DIR" != /* ]]; then
  DATA_DIR="$PROJECT_ROOT/$DATA_DIR"
fi
LOG_ARCHIVE="$DATA_DIR/log_archive/YML"

if [[ ! -d "$LOG_ARCHIVE" ]]; then
  echo "Workout archive does not exist: $LOG_ARCHIVE" >&2
  exit 1
fi

# Find all assisted bodyweight exercises in the workout logs.

rg --glob="*.{yaml,yml}" "weight: BODYWEIGHT - .* kg" "$LOG_ARCHIVE"
