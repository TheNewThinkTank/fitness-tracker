"""
Date: 2021-12-20
Author: Gustav Collin Rasmussen
Purpose: Simulate weight-training data
"""

import json
import os
import pathlib
import random
from datetime import datetime
from pprint import pprint as pp

import numpy as np
import pandas as pd
import yaml

# To make simulations/samples more realistic:
# TODO: higher reps must result in lower weight for a given set
# TODO: Implement declining trend across sets (also taking reps into account) to simulate fatigue
# TODO: Implement improving trend across workouts
# (mainly more weight, could also be higher reps, more sets, more exercises and higher workout frequency)


def cleanup() -> None:
    """Empty all simulated data."""

    p = pathlib.Path("data/simulated/")
    all_files = os.listdir(p)

    for f in all_files:
        os.remove(p / f)

    assert os.listdir(p) == []

    return


def get_available_exercises(workout_split="chest"):
    """Fetch musclegroup-exercises catalogue, with weight-ranges."""
    with open("src/simulations/muscles_and_exercises.yaml", "r") as rf:
        available_exercises = yaml.load(rf, Loader=yaml.FullLoader)
    return available_exercises[workout_split]


def get_dates(number_of_workouts):
    """Get list of dates."""
    start = datetime(2021, 1, 1)
    datelist = pd.date_range(start, periods=300).tolist()
    datelist = [date.strftime("%Y-%m-%d") for date in datelist]
    return random.sample(datelist, k=number_of_workouts)


def simulate_split():
    """Simulate data for workout split."""
    return random.choice(["back", "chest", "legs", "shoulders"])


def simulate_exercises(available_exercises):
    """Simulate data for exercises."""
    return random.sample(available_exercises, k=3)


def high_reps_low_weight(weight_range):
    """Simulate that higher reps leads to lower weights"""

    reps_available = list(range(1, 20))

    # ensure weight has same len as reps_available
    weights = np.linspace(weight_range[0], weight_range[-1], len(reps_available))

    reversed_reps = list(reversed(reps_available))
    normalized_w = reversed_reps / np.sum(reps_available)  # probabilities must sum to 1
    weight_choice = int(np.random.choice(weights, p=normalized_w))
    return f"{weight_choice} kg"


def simulate_sets_reps_weight(exercises):
    """Simulate data for sets, reps and weight."""

    mapping = {}

    for exercise in exercises:
        no_of_sets = random.randint(1, 6)
        for k, weight_range in exercise.items():
            mapping[k] = []
            for set in range(1, no_of_sets + 1):
                actual_reps = random.randint(1, 20)
                actual_weight = high_reps_low_weight(weight_range)
                mapping[k].append(
                    [
                        {
                            "set no.": set,
                            "reps": actual_reps,
                            "weight": actual_weight,
                        }
                    ]
                )

    return mapping


def format_data(workout_date, workout_split, data):
    """Prepare data format for JSON file."""

    final_data = {"date": workout_date, "split": workout_split, "exercises": data}

    return final_data


def write_data(formatted_data):
    """Insert simulated, formatted data into JSON file."""

    date = formatted_data["date"]

    p = pathlib.Path("data/simulated/")
    p.mkdir(parents=True, exist_ok=True)
    fn = f"simulated_training_log_{date}.json"
    filepath = p / fn

    with filepath.open("w", encoding="utf-8") as f:
        json.dump(formatted_data, f)


def main():
    """Simulate specified number of workouts and insert their data into JSON files."""

    # cleanup()
    # pp(high_reps_low_weight([0, 20]))

    number_of_workouts = 2
    dates = get_dates(number_of_workouts)

    for workout in range(number_of_workouts):
        workout_date = dates[workout]
        workout_split = simulate_split()
        available_exercises = get_available_exercises(workout_split)
        exercises = simulate_exercises(available_exercises)
        data = simulate_sets_reps_weight(exercises)
        # pp(data)
        formatted_data = format_data(workout_date, workout_split, data)
        write_data(formatted_data)


if __name__ == "__main__":
    main()
