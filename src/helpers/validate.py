"""_summary_
"""

import argparse
import json
# import os
from pprint import pprint as pp
import re
from typing import Optional
import yaml  # type: ignore

import pydantic


class ExercisesFormatError(Exception):
    """Custom error that is raised when Exercises doesn't have the right format."""

    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)


class Workout(pydantic.BaseModel):
    """Represents a Workout from a JSON file."""

    date: str
    split: str
    exercises: dict
    gym: Optional[str]
    note: Optional[str]  # example in workout 25

    @pydantic.field_validator("exercises")
    @classmethod
    def exercise_valid(cls, value) -> None:
        """Validator to check whether exercises are valid"""

        if not value:
            raise ExercisesFormatError(
                value=value, message="There must be at least 1 exercises."
            )

        for exercise in value.values():
            if not exercise:
                raise ExercisesFormatError(
                    value=value, message="There must be at least 1 set."
                )

            for training_set in exercise:
                if not set(training_set.keys()) == {"set_number", "reps", "weight"}:
                    raise ExercisesFormatError(
                        value=value,
                        message="Each set should have: 'set_number', 'reps' and 'weight'.\n"
                        f"Got: {set(training_set.keys())}",
                    )

                if not isinstance(training_set["weight"], str):
                    raise ExercisesFormatError(
                        value=value,
                        message="The weight must be a string.\n"
                        f"Got type: {type(training_set['weight'])}\n"
                        f"and value: {training_set['weight']}",
                    )

                result = re.match(r"\d{1,3}(?:\.\d{1,2})?\skg$", training_set["weight"])

                if result is None:
                    raise ExercisesFormatError(
                        value=value,
                        message=r"Weight field must match regex: \d{1,3}(?:\.\d{1,2})?\skg$"
                        f"\nreceived value: {training_set['weight']}",
                    )

                int_fields = ["set_number", "reps"]
                for int_field in int_fields:
                    if not isinstance(training_set[int_field], int):
                        raise ExercisesFormatError(
                            value=value,
                            message=f"The {int_field} must be an integer.\n"
                            f"Got type: {type(training_set[int_field])}\n"
                            f"and value: {training_set[int_field]}",
                        )

                if not 1 <= training_set["reps"] <= 100:
                    raise ExercisesFormatError(
                        value=value,
                        message=f"The {'reps'} field value must be between 1 and 100.\n"
                        f"Got value: {training_set['reps']}",
                    )

            training_sets = [s["set_number"] for s in exercise]

            if not training_sets[0] == 1:
                raise ExercisesFormatError(
                    value=value,
                    message="The first 'set_number' field value must be 1\n"
                    f"Got value: {training_sets[0]}",
                )

            def strictly_increasing(training_sets: list) -> bool:
                return all(x == y - 1 for x, y in zip(training_sets, training_sets[1:]))

            if not strictly_increasing(training_sets):
                raise ExercisesFormatError(
                    value=value,
                    message="The 'set_number' field must be monotonically increasing.\n"
                    f"Got values: {training_sets}",
                )

        return value


def main() -> None:
    """Main function."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--email", type=str)
    args = parser.parse_args()
    email = args.email

    with open("./config.yml", "r") as rf:
        DATA = yaml.safe_load(rf)

    # EMAIL = os.environ["EMAIL"]
    google_drive_data_path = (
        DATA["google_drive_data_path"]
        .replace("<USER>", "gustavcollinrasmussen")
        .replace("<EMAIL>", email)
    )

    # DATA = json.load(open(file="./config.json", encoding="utf-8"))

    file = (
        DATA["real_workout_database"]
        .replace("<GOOGLE_DRIVE_DATA_PATH>", google_drive_data_path)
        .replace("<ATHLETE>", "gustav_rasmussen")
    )

    with open(file) as rf:
        data = json.load(rf)["weight_training_log"]
        # print(data["1"]["date"])
        # print(data.keys())
        workouts: list[Workout] = [Workout(**item) for item in data.values()]
        # print(workouts)
        # print(workouts[0])
        pp(workouts[0].exercises)
        # print(workouts[0].dict(exclude={"squat"}))
        # print(workouts[1].copy())


if __name__ == "__main__":
    main()
