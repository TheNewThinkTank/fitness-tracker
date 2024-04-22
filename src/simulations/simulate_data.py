"""
Date: 2021-12-20
Purpose: Simulate weight-training data
"""

import random
from datetime import datetime
import pandas as pd  # type: ignore
from workout_simulator import WorkoutSimulator  # type: ignore


def get_dates(number_of_workouts: int, start: datetime, periods: int) -> list[str]:
    """Get list of dates.

    :param number_of_workouts: _description_
    :type number_of_workouts: int
    :param start: _description_
    :type start: datetime
    :param periods: _description_
    :type periods: int
    :return: _description_
    :rtype: list[str]
    """

    datelist = pd.date_range(start, periods=periods).tolist()
    datelist = [date.strftime("%Y-%m-%d") for date in datelist]

    return random.sample(datelist, k=number_of_workouts)


def main() -> None:
    """Simulate specified number of workouts and insert their data into JSON files."""

    number_of_workouts = 1  # int(sys.argv[1])  # 3 * 365
    dates = get_dates(number_of_workouts, datetime(2018, 1, 1), 4 * 365)

    workout_date = dates[0]
    progress = 10

    TRAINING_CATALOGUE: str = "src/simulations/muscles_and_exercises_weight_ranges.yaml"
    OUTPUT_DIR: str = "data/simulated/"

    simulated_workout = WorkoutSimulator(workout_date,
                                         progress,
                                         TRAINING_CATALOGUE,
                                         OUTPUT_DIR,
                                         )

    simulated_exercises = simulated_workout.select_random_exercises()
    print(type(simulated_exercises))
    print(simulated_exercises)

    # actual_reps = random.randint(1, 10)
    # weight_range = [50, 90]

    # weight_choice = simulated_workout.high_reps_low_weight(weight_range, actual_reps)
    # print(weight_choice)

    """
    progress = 10  # to simulate higher weight per set across workouts
    for workout in range(number_of_workouts):
        workout_date = dates[workout]
        simulated_workout = WorkoutSimulator(workout_date, progress)

        # actual_reps = random.randint(1, 10)
        # weight_range = [50, 90]

        # simulated_workout.high_reps_low_weight(weight_range, actual_reps)
        # pp(simulated_workout)
        # simulated_workout.write_data()
        # progress += 1_000
    """


if __name__ == "__main__":
    main()
