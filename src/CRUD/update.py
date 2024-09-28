"""
Date: 2022-07-01
Purpose: Update or delete weight-training data
"""

import os
from pprint import pprint as pp
import sys

from icecream import ic  # type: ignore
from tinydb import Query, where  # type: ignore

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from helpers.set_db_and_table import set_db_and_table  # type: ignore


def get_bw_workouts(table):
    """get workouts where BODYWEIGHT was used
    """
    Workout = Query()
    results = []
    # Iterate over all entries in the table
    for entry in table.all():
        exercises = entry.get('exercises', {})
        # Check each exercise for BODYWEIGHT in weights
        for exercise, sets in exercises.items():
            for set_info in sets:
                if 'weight' in set_info and 'BODYWEIGHT' in set_info['weight']:
                    results.append(entry)  # Add the entire entry
    return results


def search_for_exercise(table, exercise: str="assisted_pullup"):
    """_summary_

    :param table: _description_
    :type table: _type_
    """

    results = []
    # Iterate over all entries in the table
    for entry in table.all():
        exercises = entry.get('exercises', {})
        if exercise in exercises:
            results.append(exercises)
    return results


def remove_from_table(table):
    """_summary_

    :param table: _description_
    :type table: _type_
    """

    # Workout = Query()
    # table.remove(Workout.exercises.squat < 5)

    return NotImplementedError


def truncate_table(table) -> None:
    """truncate table

    :param table: _description_
    :type table: _type_
    """

    table.truncate()


def main() -> None:
    """_summary_"""

    datamodels = ["real", "simulated"]
    datatype = datamodels[0]

    db, table, _ = set_db_and_table(
        datatype,
        env="dev"
        )

    # ic(db)
    # ic(table)
    # all_entries = table.all()
    # ic(all_entries)

    pp(search_for_exercise(table))
    # pp(get_bw_workouts(table))
    # remove_from_table(table)
    # truncate_table(table)


if __name__ == "__main__":
    main()
