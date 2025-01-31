"""Validates workout data from a JSON file.
"""

import json
from pprint import pprint as pp
import re
from typing import Optional
import pydantic
from src.utils.config import settings  # type: ignore


class ExercisesFormatError(Exception):
    """Custom error that is raised when Exercises doesn't have the right format.
    """

    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)


class Workout(pydantic.BaseModel):
    """Represents a Workout from a JSON file."""

    date: str
    start: str
    end: str
    split: str
    exercises: dict
    warmup: Optional[str]
    gym: Optional[str]
    note: Optional[str]

    @pydantic.field_validator("exercises")
    @classmethod
    def exercise_valid(cls, value) -> None:
        """Validate exercises using the WorkoutValidator."""
        WorkoutValidator.validate_exercises(value)
        return value


class WorkoutValidator:
    """Handles validation of workout data."""

    @staticmethod
    def validate_exercises(value: dict) -> None:
        """Validator to check whether exercises are valid."""
        if not value:
            raise ExercisesFormatError(value=str(value), message="There must be at least 1 exercise.")

        for exercise in value.values():
            if not exercise:
                raise ExercisesFormatError(value=str(value), message="There must be at least 1 set.")
            for training_set in exercise:
                WorkoutValidator._validate_training_set(training_set)

            WorkoutValidator._validate_set_numbers(exercise)

    @staticmethod
    def _validate_training_set(training_set: dict) -> None:
        """Validates individual training sets."""
        required_fields = {"set_number", "reps", "weight"}
        if not all(x in set(training_set.keys()) for x in required_fields):
            raise ExercisesFormatError(
                value=str(training_set),
                message=f"Each set should have: {required_fields}. Got: {set(training_set.keys())}",
            )

        if not isinstance(training_set["weight"], str):
            raise ExercisesFormatError(
                value=str(training_set),
                message=f"The weight must be a string. Got type: {type(training_set['weight'])}",
            )

        regex = re.compile(r"BODYWEIGHT|\d{1,3}(?:\.\d{1,2})?\skg$", re.VERBOSE)
        if not re.match(regex, training_set["weight"]):
            raise ExercisesFormatError(
                value=str(training_set),
                message=f"Weight must match regex: \\d{{1,3}}(?:\\.\\d{{1,2}})?\\skg$. Got: {training_set['weight']}",
            )

        for field in ["set_number", "reps"]:
            if not isinstance(training_set[field], int):
                raise ExercisesFormatError(
                    value=str(training_set),
                    message=f"The {field} must be an integer. Got type: {type(training_set[field])}",
                )

        if not 1 <= training_set["reps"] <= 100:
            raise ExercisesFormatError(
                value=str(training_set),
                message=f"The 'reps' value must be between 1 and 100. Got: {training_set['reps']}",
            )

    @staticmethod
    def _validate_set_numbers(exercise: list) -> None:
        """Validates set numbers are in correct sequence."""
        training_sets = [s["set_number"] for s in exercise]
        if training_sets[0] != 1:
            raise ExercisesFormatError(
                value=str(training_sets),
                message=f"The first 'set_number' value must be 1. Got: {training_sets[0]}",
            )

        if not all(x == y - 1 for x, y in zip(training_sets, training_sets[1:])):
            raise ExercisesFormatError(
                value=str(training_sets),
                message=f"'set_number' must be monotonically increasing. Got: {training_sets}",
            )


class WorkoutFactory:
    """Factory for creating Workout instances."""

    @staticmethod
    def create_workout(data: dict) -> Workout:
        """Create a Workout instance from the given data."""
        return Workout(**data)

    @staticmethod
    def create_workouts_from_json(file_path: str) -> list[Workout]:
        """Creates a list of Workout instances from a JSON file."""
        with open(file_path) as rf:
            data = json.load(rf)["weight_training_log"]
            return [WorkoutFactory.create_workout(item) for item in data.values()]


def main() -> None:
    """Main function."""

    file = settings["real_workout_database"]

    # process workout data using the factory
    workouts = WorkoutFactory.create_workouts_from_json(file)
    # Display exercises from the first workout for demonstration
    pp(workouts[0].exercises)


if __name__ == "__main__":
    main()
