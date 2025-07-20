"""
Validates workout data from a JSON or YAML file.
"""

import json
import yaml  # type: ignore
from pprint import pformat  # type: ignore
import re
from typing import Optional
from loguru import logger  # type: ignore
# import pydantic
from pydantic import BaseModel, field_validator  # type: ignore
from src.utils.config import settings  # type: ignore


class ExercisesFormatError(Exception):
    """Custom error that is raised when Exercises doesn't have the right format.
    """

    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)


class Workout(BaseModel):
    """Represents a Workout from a JSON or YAML file."""

    date: str
    start_time: str
    end_time: str
    split: str
    exercises: dict
    warmup: Optional[str] = None
    cooldown: Optional[str] = None
    gym: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("exercises")
    @classmethod
    def exercise_valid(cls, value) -> dict:
        """Validate exercises using the WorkoutValidator."""
        WorkoutValidator.validate_exercises(value)
        return value


class WorkoutValidator:
    """Handles validation of workout data."""

    @staticmethod
    def validate_exercises(value: dict) -> None:
        """Validator to check whether exercises are valid."""
        if not value:
            raise ExercisesFormatError(
                value=str(value),
                message="There must be at least 1 exercise."
                )

        for exercise in value.values():
            if not exercise:
                raise ExercisesFormatError(
                    value=str(value),
                    message="There must be at least 1 set."
                    )
            for training_set in exercise:
                WorkoutValidator._validate_training_set(training_set)

            WorkoutValidator._validate_set_numbers(exercise)

    @staticmethod
    def _validate_training_set(training_set: dict) -> None:
        """Validates individual training sets."""
        required_fields = {"set_number", "reps", "weight"}
        provided_keys = set(training_set.keys())
        missing_fields = required_fields - provided_keys
    
        # if not all(x in set(training_set.keys()) for x in required_fields):
        #     raise ExercisesFormatError(
        #         value=str(training_set),
        #         message=f"Each set should have: {required_fields}. Got: {set(training_set.keys())}",
        #     )

        if missing_fields:
            raise ExercisesFormatError(
                value=str(training_set),
                message=f"Missing required field(s): {', '.join(missing_fields)}",
            )

        if not isinstance(training_set["weight"], str):
            raise ExercisesFormatError(
                value=str(training_set),
                message=f"The weight must be a string. Got type: {type(training_set['weight'])}",
            )

        # TODO: Sidea_9012_Olympic_Hex_Bar
        # TODO: powerband_pattern = r"^POWERBAND_(GREEN|PURPLE|BLACK|RED)"
        weight_pattern = r"^(BODYWEIGHT|\d{1,3}(?:\.\d{1,2})?\skg)$"

        weight_regex = re.compile(weight_pattern, re.VERBOSE)
        if not re.match(weight_regex, training_set["weight"]):
            raise ExercisesFormatError(
                value=str(training_set),
                message=f"Weight must match regex: {weight_pattern}. Got: {training_set['weight']}",
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

    @staticmethod
    def create_workouts_from_yaml(file_path: str) -> list[Workout]:
        """Creates a list of Workout instances from a YAML file."""
        with open(file_path) as rf:
            try:
                # data = yaml.safe_load(rf)["weight_training_log"]
                # return [WorkoutFactory.create_workout(item) for item in data.values()]
                data = yaml.safe_load(rf)
                return [WorkoutFactory.create_workout(data)]
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in file {file_path}") from e


def main() -> None:
    """Main function."""

    import argparse
    import logging
    from logger_config import setup_logger, log_running_file  # type: ignore

    setup_logger(log_file="validate.log")
    log_running_file(__file__)

    parser = argparse.ArgumentParser(
        description="Validate workout data from a JSON or YAML file.",
    )

    parser.add_argument(
        "-f", "--file",
        help="Path to the JSON or YAML file to validate.",
        required=True
    )
    args = parser.parse_args()
    file = args.file

    logging.debug(f"Validating workout data from file: {file}")

    # file = settings["real_workout_database"].replace("<YEAR>", "2025")

    # process workout data using the factory
    # workouts = WorkoutFactory.create_workouts_from_json(file)
    workouts = WorkoutFactory.create_workouts_from_yaml(file)
    # Display exercises from the first workout for demonstration
    logger.debug(pformat(workouts[0].exercises))


if __name__ == "__main__":
    main()
