"""
Date: 2021-12-20
Author: Gustav Collin Rasmussen
Purpose: Simulate weight-training data
"""

import json
import pathlib

from faker import Faker
from faker.providers import DynamicProvider

fake = Faker()


def simulate_data():
    """Simulate data for workout dates, splits and exercises."""

    workout_dates = [fake.date() for _ in range(10)]

    splits_provider = DynamicProvider(
        provider_name="splits",
        elements=["back", "chest", "legs", "shoulders"],
    )

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

    fake.add_provider(splits_provider)
    fake.add_provider(chest_exercises_provider)
    fake.add_provider(back_exercises_provider)
    fake.add_provider(leg_exercises_provider)
    fake.add_provider(shoulder_exercises_provider)

    workout_splits = [fake.splits() for _ in range(10)]
    workout_chest_exercises = [fake.unique.chest_exercises() for _ in range(3)]
    workout_back_exercises = [fake.unique.back_exercises() for _ in range(3)]
    workout_leg_exercises = [fake.unique.leg_exercises() for _ in range(3)]
    workout_shoulder_exercises = [fake.unique.shoulder_exercises() for _ in range(3)]

    # for wd, ws in zip(workout_dates, workout_splits):
    #     print(wd, ws)

    """
    for ce, be, le, se in zip(
        workout_chest_exercises,
        workout_back_exercises,
        workout_leg_exercises,
        workout_shoulder_exercises,
    ):
        print(ce, be, le, se)
    """
    return (
        workout_dates,
        workout_splits,
        workout_chest_exercises,
        workout_back_exercises,
        workout_leg_exercises,
        workout_shoulder_exercises,
    )


def format_data(sim_data):
    """Prepare data format for JSON file."""

    (
        workout_dates,
        workout_splits,
        workout_chest_exercises,
        workout_back_exercises,
        workout_leg_exercises,
        workout_shoulder_exercises,
    ) = sim_data

    date = workout_dates[0]
    split = workout_splits[0]

    split_exercises_map = {
        "chest": workout_chest_exercises,
        "back": workout_back_exercises,
        "legs": workout_leg_exercises,
        "shoulders": workout_shoulder_exercises,
    }

    exercises = split_exercises_map[split]
    # print(split, exercises)

    data = {
        "date": date,
        "split": workout_splits[0],
        "exercises": {
            exercises[0]: [
                {"set no.": 1, "reps": "null", "weight": "value kg"},
                {"set no.": 2, "reps": "null", "weight": "value kg"},
                {"set no.": 3, "reps": "null", "weight": "value kg"},
            ],
            exercises[1]: [
                {"set no.": 1, "reps": "null", "weight": "value kg"},
                {"set no.": 2, "reps": "null", "weight": "value kg"},
                {"set no.": 3, "reps": "null", "weight": "value kg"},
            ],
            exercises[2]: [
                {"set no.": 1, "reps": "null", "weight": "value kg"},
                {"set no.": 2, "reps": "null", "weight": "value kg"},
                {"set no.": 3, "reps": "null", "weight": "value kg"},
            ],
        },
    }

    return data


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
    """Simulate, format and insert data into JSON file."""
    sim_data = simulate_data()
    formatted_data = format_data(sim_data)
    write_data(formatted_data)


if __name__ == "__main__":
    main()
