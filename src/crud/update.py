"""
Update or delete weight-training data.
"""

import re
from pprint import pformat  # type: ignore
from loguru import logger  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore


def filter_exercises_with_whitespace(workout_data: list) -> list[dict]:
    """Find exercises with whitespace.

    :param workout_data: Workout data
    :type workout_data: list
    :return: A list of workouts with exercises that contain whitespace
    :rtype: list
    """

    filtered_exercises = []
    for workout in workout_data:
        exercises_with_whitespace = [
            exercise for exercise in workout['exercises'].keys() if ' ' in exercise
        ]

        # If any exercise with whitespace is found, add the workout to the result
        if exercises_with_whitespace:
            filtered_exercises.append({
                'date': workout['date'],
                'split': workout['split'],
                'exercises_with_whitespace': exercises_with_whitespace
            })

    return filtered_exercises


def clean_exercise_name(exercise: str) -> str:
    """Cleans the name of an exercise by replacing spaces with underscores.

    :param exercise: The name of an exercise
    :type exercise: str
    :return: The cleaned exercise name
    :rtype: str
    """

    regex = r'[_\s]+'

    # Replace matches with a single underscore
    cleaned_exercise = re.sub(regex, '_', exercise)

    # Remove any trailing underscores
    cleaned_exercise = cleaned_exercise.removesuffix("_")

    return cleaned_exercise


def clean_exercise_names(table) -> None:
    """Cleans the names of exercises by replacing spaces with underscores
    and updating the database.

    :param table: The database table containing workout data.
    :type table: tinydb.table.Table
    :return: None
    :rtype: None
    """
    workout_data = table.all()
    updates = []
    for workout in workout_data:
        new_exercises = {
            clean_exercise_name(exercise): details
            for exercise, details in workout['exercises'].items()
            }
        workout['exercises'] = new_exercises
        # table.update(workout, Query().date == workout['date'])
        updates.append(workout)
    table.update_multiple(updates)


def main() -> None:
    """Clean exercise names in the database.

    Pass --dry-run to preview changes without writing them.
    """

    import argparse

    parser = argparse.ArgumentParser(description="Clean exercise names in the database.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to the database.",
    )
    parser.add_argument(
        "--datatype",
        type=str,
        default="real",
        choices=["real", "simulated"],
        help="Which database to operate on (default: real).",
    )
    args = parser.parse_args()

    _, table, _ = set_db_and_table(args.datatype, env="dev")

    dirty = filter_exercises_with_whitespace(table.all())
    if not dirty:
        logger.info("No exercises with whitespace found — nothing to do.")
        return

    logger.info("Exercises with whitespace:\n{}", pformat(dirty))

    if args.dry_run:
        logger.info("Dry run — no changes written.")
        return

    clean_exercise_names(table)
    logger.info("Exercise names cleaned successfully.")


if __name__ == "__main__":
    main()
