"""
Date: 2022-07-01
Purpose: Update or delete weight-training data
"""

import os
import sys

from icecream import ic  # type: ignore
from tinydb import Query  # type: ignore

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from helpers.set_db_and_table import set_db_and_table  # type: ignore


def update_table(table):
    """_summary_

    :param table: _description_
    :type table: _type_
    """

    Workout = Query()
    Exercise = Query()

    # groups.search(Group.permissions.any(Permission.type == 'read'))

    # data = {"weight": "BODYWEIGHT - 35 kg"}

    search = table.search(
        Workout.exercises.any(
            Exercise.assisted_pullup.weight == "BODYWEIGHT - 35 kg"
        )
    )

    # table.search(Check["json-object"]["test"].exists())
    # search = table.search(Workout.exercises.Exercise.fragment(data))

    # table.update({"reps": 10}, Item.exercises.chinup.reps == 6)

    return search


def remove_from_table(table) -> None:
    """_summary_

    :param table: _description_
    :type table: _type_
    """

    Workout = Query()
    table.remove(Workout.exercises.squat < 5)


def truncate_table(table) -> None:
    """truncate table

    :param table: _description_
    :type table: _type_
    """

    table.truncate()


def main() -> None:
    """_summary_"""

    datamodels = ["real", "simulated"]
    datatype = datamodels[1]

    db, table, _ = set_db_and_table(
        datatype,
        env="dev"
        )

    # ic(db)
    # ic(table)

    print(update_table(table))
    # remove_from_table(table)
    # truncate_table(table)


if __name__ == "__main__":
    main()
