"""
Date: 2021-12-11
Purpose: Store and analyze weight-training data
https://tinydb.readthedocs.io/en/latest/getting-started.html
"""

import os
import sys

from tinydb import Query  # type: ignore

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from helpers.set_db_and_table import set_db_and_table  # type: ignore


def get_dates(table) -> list[str]:
    """Get all workout dates

    :param table: _description_
    :type table: _type_
    :return: _description_
    :rtype: list[str]
    """

    return [item["date"] for item in table]


def get_dates_and_muscle_groups(table) -> dict[str, str]:
    """Returns all workout dates with their corresponding muscle groups.

    :param table: A TinyDB table
    :type table: TinyDB table
    :return: A dictionary of workout dates and corresponding splits / musclegroup
    :rtype: dict[str, str]
    """

    return {item["date"]: item["split"] for item in table}


def show_exercises(table, date: str) -> list[str]:
    """Show all exercises for given workout date

    :param table: A TinyDB table
    :type table: TinyDB table
    :param date: Date of a given workout
    :type date: str
    :return: A list of exercises performed on a given date
    :rtype: list[str]
    """

    all_exercises_during_workout = []

    for item in table:
        if item["date"] == date:
            for k, _ in item["exercises"].items():
                all_exercises_during_workout.append(k)
    return all_exercises_during_workout


def get_all(table) -> list[dict]:
    """get all documents

    :param table: _description_
    :type table: _type_
    :return: _description_
    :rtype: list[dict]
    """

    return table.all()


def describe_workout(log, date: str) -> dict | None:
    """Simple summary statistics for each exercise

    :param log: _description_
    :type log: _type_
    :param date: _description_
    :type date: str
    :return: _description_
    :rtype: dict
    """

    # d = {}
    # for item in log:
    #     if item["date"] == date:
    #         d["Date of workout"] = date
    #         for k, v in item["exercises"].items():
    #             d[k] = f"{len(v)} sets"
    # return d

    # TODO: check if below works when workout date contains multiple workouts.
    # TODO: otherwise, use code above
    workout_data = next((item for item in log if item["date"] == date), None)
    if not workout_data:
        return None
    result = {"Date of workout": date}
    result.update({k: f"{len(v)} sets" for k, v in workout_data["exercises"].items()})
    return result


def show_exercise(log, exercise: str, date: str) -> list:
    """Show detailed data for selected exercise

    :param log: _description_
    :type log: _type_
    :param exercise: _description_
    :type exercise: str
    :param date: _description_
    :type date: str
    :return: _description_
    :rtype: list
    """

    for item in log:
        if item["date"] == date:
            return item["exercises"].get(exercise, [])
    return []


def analyze_workout(table, exercise: str) -> list:
    """Deeper analysis of workout

    :param table: A TinyDB table
    :type table: TinyDB table
    :param exercise: Name of exercise to analyze
    :type exercise: str
    :return: _description_
    :rtype: list
    """

    Log = Query()
    data = table.search(Log["exercises"][exercise].exists())

    return [d["exercises"][exercise] for d in data]


def main() -> None:
    """_summary_
    """

    from pprint import pprint as pp

    datamodels = ["real", "simulated"]
    datatype = datamodels[0]
    _EXERCISE = "squat"
    _WORKOUT_DATE = "2024-01-27"  # "2021-12-11"

    # _, table, _ = set_db_and_table(datatype)
    _, table, _ = set_db_and_table(datatype, env="dev")

    # dates_and_muscle_groups = get_dates_and_muscle_groups(table)
    # pp(dates_and_muscle_groups)
    # pp(show_exercises(table, _WORKOUT_DATE))
    # pp(get_all(table))
    # pp(describe_workout(table, _WORKOUT_DATE))
    # pp(show_exercise(table, _EXERCISE, _WORKOUT_DATE))
    # print(analyze_workout(table, _EXERCISE))


if __name__ == "__main__":
    main()
