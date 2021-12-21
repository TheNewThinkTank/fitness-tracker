"""
Date: 2021-12-20
Author: Gustav Collin Rasmussen
Purpose: Simulate weight-training data
"""

import json
import pathlib
import random
import pandas as pd
from datetime import datetime

# TODO: Implement improving trend across workouts
# TODO: Implement declining trend across sets (also taking reps into account)


def get_dates(number_of_workouts):
    """Get list of dates."""
    start = datetime(2021, 1, 1)
    datelist = pd.date_range(start, periods=300).tolist()
    datelist = [date.strftime("%Y-%m-%d") for date in datelist]
    return random.sample(datelist, k=number_of_workouts)


def simulate_split():
    """Simulate data for workout split."""
    return random.choice(["back", "chest", "legs", "shoulders"])


def simulate_exercises(workout_split):
    """Simulate data for exercises."""

    workout_chest_exercises = random.sample(
        ["benchpress", "flys", "pullovers", "dips"], k=3
    )
    workout_back_exercises = random.sample(
        ["chinups", "lat pulldowns", "seated row", "dead row"], k=3
    )
    workout_leg_exercises = random.sample(
        ["squat", "legpress", "leg extention", "deadlift"], k=3
    )
    workout_shoulder_exercises = random.sample(
        [
            "dumbbel side lateral raises",
            "cable side lateral raises",
            "dumbbel front lateral raises",
            "seated dumbbel rear lateral raises",
        ],
        k=3,
    )

    switcher = {
        "back": workout_back_exercises,
        "chest": workout_chest_exercises,
        "legs": workout_leg_exercises,
        "shoulders": workout_shoulder_exercises,
    }

    return switcher.get(workout_split, "Invalid muscle-group")


def simulate_sets_reps_weight():
    """Simulate data for sets, reps and weight."""
    no_of_sets = random.randint(1, 6)

    data = []

    for set in range(1, no_of_sets + 1):
        data.append(
            {
                "set no.": set,
                "reps": random.randint(1, 20),
                "weight": f"{random.randint(1, 100)} kg",
            }
        )

    return data


def attach_data_to_exercise(exercises):
    """Fill in sets, reps and weight data for each exercise"""

    data = {}

    for exercise in exercises:
        data[exercise] = simulate_sets_reps_weight()

    return data


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

    number_of_workouts = 100
    dates = get_dates(number_of_workouts)

    for workout in range(number_of_workouts):
        workout_date = dates[workout]
        workout_split = simulate_split()
        exercises = simulate_exercises(workout_split)
        data = attach_data_to_exercise(exercises)
        formatted_data = format_data(workout_date, workout_split, data)
        write_data(formatted_data)


if __name__ == "__main__":
    main()
