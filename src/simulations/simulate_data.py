"""
Date: 2021-12-20
Purpose: Simulate weight-training data
"""

import random
from datetime import datetime
# from workout_simulator import WorkoutSimulator  # type: ignore
from pprint import pprint as pp
from datetime_tools.generate_days import generate_dates  # type: ignore


def reservoir_sample(generator, k: int):
    """Select k random elements from the generator using reservoir sampling."""
    reservoir = []
    
    for i, element in enumerate(generator):
        if i < k:
            reservoir.append(element)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = element

    return reservoir


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

    date_generator = generate_dates(start, periods)
    return reservoir_sample(date_generator, number_of_workouts)


def main() -> None:
    """Simulate specified number of workouts and insert their data into JSON files."""

    number_of_workouts = 10  # 1  # or you could use: int(sys.argv[1])  # Example: 3 * 365
    start_date = datetime(2018, 1, 1)  # Start date for generating dates
    periods = 4 * 365  # Number of days to generate
    # Get random workout dates
    dates = get_dates(number_of_workouts, start_date, periods)
    dates_sorted = sorted(dates)
    pp(dates_sorted)

    # workout_date = dates[0]
    # progress = 10
    # TRAINING_CATALOGUE: str = "src/simulations/muscles_and_exercises_weight_ranges.yaml"
    # OUTPUT_DIR: str = "data/simulated/"
    # simulated_workout = WorkoutSimulator(workout_date,
    #                                      progress,
    #                                      TRAINING_CATALOGUE,
    #                                      OUTPUT_DIR,
    #                                      )
    # simulated_exercises = simulated_workout.select_random_exercises()
    # print(type(simulated_exercises))
    # print(simulated_exercises)

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
