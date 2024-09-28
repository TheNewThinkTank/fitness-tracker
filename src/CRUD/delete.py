"""_summary_
"""

import os
# from pprint import pprint as pp
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from helpers.set_db_and_table import set_db_and_table  # type: ignore


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

    # remove_from_table(table)
    # truncate_table(table)


if __name__ == "__main__":
    main()
