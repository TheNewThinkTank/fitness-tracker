"""
Get the data from the workout database for a given year.
"""

import os
from src.crud.read import get_all  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore


def get_data(year: int | str) -> list[dict]:
    """Get the data from the workout database for a given year.

    :param year: Year to get the data for.
    :type year: str
    :return: data from the workout database for a given year.
    :rtype: list[dict]
    """

    athlete = os.getenv("ATHLETE")
    if not athlete:
        raise ValueError("ATHLETE environment variable is not set.")
    normalized_year = int(year)
    db, table, _ = set_db_and_table(
        datatype="real",
        athlete=athlete,
        year=normalized_year,
        )

    data = get_all(table)
    # db.close()

    return data
