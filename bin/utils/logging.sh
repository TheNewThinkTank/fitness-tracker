#!/usr/bin/env bash

log() {
  "$PYTHON_BIN" -m src.utils.log_archive --log-dir "$(dirname "$LOG_FILE")" \
    append --file "${LOG_FILE##*/}" --message="$1"
}
