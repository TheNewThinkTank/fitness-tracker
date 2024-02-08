"""
Date: 2022-07-01
Purpose: Update or delete weight-training data
"""

import os
import sys

from icecream import ic  # type: ignore
from tinydb import Query, where  # type: ignore

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from helpers.set_db_and_table import set_db_and_table  # type: ignore


def search_table(table):
    """_summary_

    :param table: _description_
    :type table: _type_
    """

    Workout = Query()
    # Exercise = Query()

    # table.search(Workout.Exercise.any(Exercise.weight == '35 kg'))
    # data = {"weight": "BODYWEIGHT - 35 kg"}

    # search_results = table.search(
    #     Workout.exercises.any(
    #         (Exercise.assisted_pullup.any(Exercise.weight == "BODYWEIGHT - 35 kg"))
    #     )
    # )

    # ic(table)
    # q = Query()
    # search_results = table.search(Workout.exercises.exists())
    # search_results = table.search(Workout.exercises.weight == "BODYWEIGHT - 35 kg")
    # search_results = table.search(where('exercises').weight == "BODYWEIGHT - 35 kg")
    # search_results = table.search(Query().fragment({'weight': "BODYWEIGHT - 35 kg"}))
    search_results = table.search(Workout.exercises.search('BODYWEIGHT'))

    # search_results = table.search(
    #     Workout.exercises.any(
    #         Workout.assisted_pullup.exists()
    #     )
    #     )

    # search_results = table.search(
    #     q.exercises.any(
    #         q.assisted_pullup.exists()
    #     )
    # )

    # search_results = table.search(
    #     q.exercises.any(
    #         q.assisted_pullup.any(q.weight == "BODYWEIGHT - 35 kg")
    #     )
    # )

    # search_results = table.search(
    #     q.exercises.any(
    #         q.assisted_pullup.any(q.weight.exists())
    #     )
    # )
    # search = table.search(Workout.exercises.Exercise.fragment(data))

    # table.update({"reps": 10}, Item.exercises.chinup.reps == 6)

    return search_results


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

    print(search_table(table))
    # remove_from_table(table)
    # truncate_table(table)


if __name__ == "__main__":
    main()
