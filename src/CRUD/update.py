"""
Date: 2022-07-01
Purpose: Update or delete weight-training data
"""

import os
# from pprint import pprint as pp
import sys
from icecream import ic  # type: ignore
# from tinydb import Query, where  # type: ignore
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from helpers.set_db_and_table import set_db_and_table  # type: ignore


def main() -> None:
    """_summary_"""

    datamodels = ["real", "simulated"]
    datatype = datamodels[0]

    db, table, _ = set_db_and_table(
        datatype,
        env="dev"
        )

    ic(db)
    ic(table)
    # all_entries = table.all()
    # ic(all_entries)

    # remove_from_table(table)
    # truncate_table(table)


if __name__ == "__main__":
    main()
