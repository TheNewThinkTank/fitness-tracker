"""
Date: 2021-12-20
Author: Gustav Collin Rasmussen
Purpose: Simulate weight-training data
"""

import json
import pathlib
import random

# from pprint import pprint as pp

from faker import Faker
from faker.providers import DynamicProvider

fake = Faker()


def simulate_date_and_split():
    """Simulate data for workout date and split."""

    workout_date = fake.date()

    splits_provider = DynamicProvider(
        provider_name="splits",
        elements=["back", "chest", "legs", "shoulders"],
    )

    fake.add_provider(splits_provider)
    workout_split = fake.splits()

    return workout_date, workout_split


def simulate_exercises(workout_split):
    """Simulate data for exercises."""
    chest_exercises_provider = DynamicProvider(
        provider_name="chest_exercises",
        elements=["benchpress", "flys", "pullovers", "dips"],
    )

    back_exercises_provider = DynamicProvider(
        provider_name="back_exercises",
        elements=["chinups", "lat pulldowns", "seated row", "dead row"],
    )

    leg_exercises_provider = DynamicProvider(
        provider_name="leg_exercises",
        elements=["squat", "legpress", "leg extention", "deadlift"],
    )

    shoulder_exercises_provider = DynamicProvider(
        provider_name="shoulder_exercises",
        elements=[
            "dumbbel side lateral raises",
            "cable side lateral raises",
            "dumbbel front lateral raises",
            "seated dumbbel rear lateral raises",
        ],
    )

    fake.add_provider(chest_exercises_provider)
    fake.add_provider(back_exercises_provider)
    fake.add_provider(leg_exercises_provider)
    fake.add_provider(shoulder_exercises_provider)

    workout_chest_exercises = [fake.unique.chest_exercises() for _ in range(3)]
    workout_back_exercises = [fake.unique.back_exercises() for _ in range(3)]
    workout_leg_exercises = [fake.unique.leg_exercises() for _ in range(3)]
    workout_shoulder_exercises = [fake.unique.shoulder_exercises() for _ in range(3)]

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

    number_of_workouts = 2

    for workout in range(number_of_workouts):
        workout_date, workout_split = simulate_date_and_split()
        exercises = simulate_exercises(workout_split)
        data = attach_data_to_exercise(exercises)
        formatted_data = format_data(workout_date, workout_split, data)
        # pp(formatted_data)
        write_data(formatted_data)


if __name__ == "__main__":
    main()
