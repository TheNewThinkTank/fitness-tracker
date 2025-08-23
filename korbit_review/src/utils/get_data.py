"""
Get the data from the workout database for a given year.
"""

import os
from src.crud.read import get_all  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore


def get_data(year: str) -> list[dict]:
    """Get the data from the workout database for a given year.

    :param year: Year to get the data for.
    :type year: str
    :return: data from the workout database for a given year.
    :rtype: list[dict]
    """

    db, table, _ = set_db_and_table(
        datatype="real",
        athlete=os.getenv("ATHLETE", "donald_duck"),
        year=year,
        )

    data = get_all(table)
    # db.close()

    return data
