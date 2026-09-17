#!/usr/bin/env bash

set -euo pipefail

if [[ -f .env ]]; then
  # shellcheck source=/dev/null
  source .env
fi

FITNESS_TRACKER_DATA_DIR="${FITNESS_TRACKER_DATA_DIR:-data}"
YEAR_TO_PLOT="${YEAR_TO_PLOT:-$(date +%Y)}"
IMG_PATH="${FITNESS_TRACKER_DATA_DIR%/}/img/${YEAR_TO_PLOT}/"

echo "$FITNESS_TRACKER_DATA_DIR"
echo "$IMG_PATH"
