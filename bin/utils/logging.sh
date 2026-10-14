#!/usr/bin/env bash

log() {
  if [[ -f "$LOG_FILE" ]]; then
    local log_size archive
    log_size=$(wc -c < "$LOG_FILE") || return
    if (( log_size >= 10485760 )); then
      for (( archive = 5; archive > 1; archive-- )); do
        if [[ -f "${LOG_FILE}.$((archive - 1))" ]]; then
          mv "${LOG_FILE}.$((archive - 1))" "${LOG_FILE}.${archive}" || return
        fi
      done
      mv "$LOG_FILE" "${LOG_FILE}.1" || return
    fi
  fi
  printf '%s - %s\n' "$(date +'%Y-%m-%d %H:%M:%S')" "$1" | tee -a "$LOG_FILE"
}
