#!/usr/bin/env bash

set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"
PYTHON_BIN="${PYTHON_BIN:-$PROJECT_ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
	PYTHON_BIN=$(command -v python3)
fi

# Date: 2022-01-15
# Author: Gustav Collin Rasmussen
# Purpose: BASH workflow that deletes data, creates data and inserts it in database.

NUMBER_OF_WORKOUTS=100

# python3 src/utils/cleanup.py data/simulated/ data/sim_db.json
# echo 'cleanup complete'
"$PYTHON_BIN" -m src.simulations.simulate_data "$NUMBER_OF_WORKOUTS"
# echo 'simulations complete'
"$PYTHON_BIN" -m src.crud.insert --datatype simulated
# echo 'simulations inserted in database. Preparing figures ..'
# python3 src/model/plot_model.py --datatype simulated
# open img/fitted_data_barbell_bench_press.png
