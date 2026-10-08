#!/usr/bin/env bash

set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"
PYTHON_BIN="${PYTHON_BIN:-$PROJECT_ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
    PYTHON_BIN=$(command -v python3)
fi

# test plotting code

YEAR_TO_PLOT="2023"


MONTHS=("January" "February" "March" "April" "May" "June" "July")

for month in "${MONTHS[@]}"; do
    echo "$month"

    MONTH_TO_PLOT="$month"  # "July"

    if ! "$PYTHON_BIN" -m src.combined_metrics.combined_metrics --year_to_plot "$YEAR_TO_PLOT" --month_to_plot "$MONTH_TO_PLOT"; then
        echo "Error: Failed to prepare figures."
        exit 1
    fi


    open_images() {
    # open ./img/workout_frequency.png
        if command -v open >/dev/null 2>&1; then
            open "$PROJECT_ROOT/data/img/$YEAR_TO_PLOT/workout_duration_${MONTH_TO_PLOT}_${YEAR_TO_PLOT}.png"
        elif command -v xdg-open >/dev/null 2>&1; then
            xdg-open "$PROJECT_ROOT/data/img/$YEAR_TO_PLOT/workout_duration_${MONTH_TO_PLOT}_${YEAR_TO_PLOT}.png"
        fi
    # open ./img/workout_duration_volume_1rm_bb_bench_press.png
    }


    if ! open_images; then
        echo "Error: Failed to open images."
        exit 1
    fi

done
