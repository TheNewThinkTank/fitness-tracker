"""
Date: 2021-12-20
Author: Gustav Collin Rasmussen
Purpose: Simulate weight-training data
"""

import typing
import numpy as np  # type: ignore
import json
import pathlib
import random

# import sys
from datetime import datetime
import pandas as pd  # type: ignore
import yaml  # type: ignore

# from pprint import pprint as pp


class SimulateWorkout:
    """Simulate a workout"""

    splits: list = ["back", "chest", "legs", "shoulders"]
    training_catalogue: str = "src/simulations/muscles_and_exercises.yaml"
    output_dir: str = "data/simulated/"

    def __init__(self, workout_date, progress) -> None:
        self.workout_date = workout_date
        self.progress = progress
        self.split = random.choice(self.splits)

    def get_available_exercises(self) -> list[dict]:
        """Fetch musclegroup-exercises catalogue, with weight-ranges."""
        with open(self.training_catalogue, "r") as rf:
            available_exercises = yaml.load(rf, Loader=yaml.FullLoader)
        return available_exercises[self.split]

    def simulate_exercises(self) -> list[dict]:
        """Simulate data for exercises."""
        return random.sample(self.get_available_exercises(), k=random.randint(2, 6))

    def high_reps_low_weight(self, weight_range, actual_reps) -> str:
        """Simulate that higher reps leads to lower weights.
        choose weight from inverted 1RM estimate plus randomised progression"""

        weight_choice = weight_range[-1] * ((100 - actual_reps * 2.5) / 100) + np.log10(
            self.progress
        )

        # print(weight_range, actual_reps, self.progress, weight_choice)

        return f"{weight_choice:.2f} kg"

    def simulate_sets_reps_weight(self) -> dict:
        """Simulate data for sets, reps and weight."""
        mapping = {}
        for exercise in self.simulate_exercises():
            no_of_sets = random.randint(1, 6)
            for k, weight_range in exercise.items():
                mapping[k] = []
                for set in range(1, no_of_sets + 1):
                    actual_reps = random.randint(1, 10)
                    actual_weight = self.high_reps_low_weight(weight_range, actual_reps)
                    mapping[k].append(
                        {
                            "set no.": set,
                            "reps": actual_reps,
                            "weight": actual_weight,
                        }
                    )

        return mapping

    def format_data(self) -> dict:
        """Prepare data format for JSON file."""
        return {
            "date": self.workout_date,
            "split": self.split,
            "exercises": self.simulate_sets_reps_weight(),
        }

    def write_data(self) -> None:
        """Insert simulated, formatted data into JSON file."""
        date = self.format_data()["date"]
        p = pathlib.Path(self.output_dir)
        p.mkdir(parents=True, exist_ok=True)
        fn = f"simulated_training_log_{date}.json"
        filepath = p / fn
        with filepath.open("w", encoding="utf-8") as f:
            json.dump(self.format_data(), f)


def get_dates(
    number_of_workouts: int, start: datetime, periods: int
) -> typing.List[str]:
    """Get list of dates."""
    datelist = pd.date_range(start, periods=periods).tolist()
    datelist = [date.strftime("%Y-%m-%d") for date in datelist]
    return random.sample(datelist, k=number_of_workouts)


def main() -> None:
    """Simulate specified number of workouts and insert their data into JSON files."""

    number_of_workouts = 1  # int(sys.argv[1])  # 3 * 365
    dates = get_dates(number_of_workouts, datetime(2018, 1, 1), 4 * 365)

    workout_date = dates[0]
    progress = 10

    simulated_workout = SimulateWorkout(workout_date, progress)

    simulated_exercises = simulated_workout.simulate_exercises()
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
        simulated_workout = SimulateWorkout(workout_date, progress)

        # actual_reps = random.randint(1, 10)
        # weight_range = [50, 90]

        # simulated_workout.high_reps_low_weight(weight_range, actual_reps)
        # pp(simulated_workout)
        # simulated_workout.write_data()
        # progress += 1_000
    """


if __name__ == "__main__":
    main()
