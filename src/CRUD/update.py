"""
Date: 2022-07-01
Purpose: Update or delete weight-training data
"""

__all__ = ["update_table", "remove_from_table", "truncate_table"]
__author__ = "Gustav Collin Rasmussen"
__version__ = "0.1.0"

from tinydb import Query  # type: ignore

from helpers.set_db_and_table import set_db_and_table  # type: ignore


def update_table(table) -> None:
    """_summary_"""

    Workout = Query()
    # Exercise = Query()
    # table.search(
    #     Workout.exercises.any(
    #         Exercise.chinup == [{"reps": 6, "set_number": 1, "weight": "13.43 kg"}]
    #     )
    # )
    # table.search(Check["json-object"]["test"].exists())
    # table.update({"reps": 10}, Item.exercises.chinup.reps == 6)
    table.search(Workout.exercises.Exercise.fragment({"foo": True, "bar": False}))


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

    db, table, _ = set_db_and_table(datatype)

    print(db, table)
    # update_table(table)
    # remove_from_table(table)
    truncate_table(table)


if __name__ == "__main__":
    main()
