#!/opt/homebrew/bin/bash

# test plotting code

FILE_FORMAT='yml'


YEAR_TO_PLOT="2023"


MONTHS=("January" "February" "March" "April" "May" "June" "July")

for month in ${MONTHS[@]}; do
    echo "$month"

    MONTH_TO_PLOT="$month"  # "July"

    if ! python3 ./src/combined_metrics/combined_metrics.py --file_format "$FILE_FORMAT"  --year_to_plot "$YEAR_TO_PLOT" --month_to_plot "$MONTH_TO_PLOT"; then
        echo "Error: Failed to prepare figures."
        exit 1
    fi


    open_images() {
    # open ./img/workout_frequency.png
    open ./img/workout_duration_"$MONTH_TO_PLOT"_"$YEAR_TO_PLOT".png
    # open ./img/workout_duration_volume_1rm_bb_bench_press.png
    }


    if ! open_images; then
        echo "Error: Failed to open images."
        exit 1
    fi

done
