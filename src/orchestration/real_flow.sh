#!/opt/homebrew/bin/bash

# Date: 2022-01-21
# Author: Gustav Collin Rasmussen
# Purpose: BASH workflow that inserts data in database.

WORKOUT_DATE=$(date +%F)  # '2023-01-19'  # 2022-03-02,2022-03-03
YEAR_TO_PLOT=$(date +%Y)  # "2023"
MONTH_TO_PLOT=$(date +%B)  # "August"
# TRAINING_PROGRAM='nfp'  # 'gvt'
FILE_FORMAT='yml'  # default is json

# --workout_number 2

if ! python3 ./src/CRUD/insert.py --file_format "$FILE_FORMAT" --datatype real --dates "$WORKOUT_DATE"; then
    echo "Error: Failed to insert data in database."
    exit 1
fi

echo "Data inserted in database. Preparing figures..."

if ! python3 ./src/combined_metrics/combined_metrics.py --year_to_plot "$YEAR_TO_PLOT" --month_to_plot "$MONTH_TO_PLOT"; then
    echo "Error: Failed to prepare figures."
    exit 1
fi

# python3 src/model/plot_model.py --datatype real --pgm $TRAINING_PROGRAM

open_images() {
  open ./img/"$YEAR_TO_PLOT"_workout_frequency.png
  # open ./img/workout_frequency.png
  # open ./img/workout_duration.png
  open ./img/workout_duration_"$MONTH_TO_PLOT"_"$YEAR_TO_PLOT".png
  # open ./img/workout_duration_volume_1rm_bb_bench_press.png
  # open img/real_fitted_data_squat_${TRAINING_PROGRAM}.png
  # open img/real_fitted_data_barbell_bench_press_${TRAINING_PROGRAM}.png
  # open img/real_fitted_data_squat_splines.png
  # open img/real_fitted_data_deadlift_splines.png
  # open img/real_fitted_data_seated_row_splines.png
  # open img/real_fitted_data_barbell_bench_press_splines.png
}

if ! open_images; then
    echo "Error: Failed to open images."
    exit 1
fi
