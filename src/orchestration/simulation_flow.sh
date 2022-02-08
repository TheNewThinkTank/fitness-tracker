#!/usr/local/bin/bash

# Date: 2022-01-15
# Author: Gustav Collin Rasmussen
# Purpose: BASH workflow that deletes data, creates data and inserts it in database.

python3 src/helpers/cleanup.py data/simulated/ data/sim_db.json
echo 'cleanup complete'
python3 src/simulations/simulate_data.py 100
echo 'simulations complete'
python3 src/CRUD/insert.py simulated
echo 'simulations inserted in database. Preparing figures ..'
python3 src/model/plot_model.py --datatype simulated
open img/fitted_data_barbell_bench_press.png
