"""
Get the data from the workout database for a given year.
"""

from __future__ import annotations

from typing import Any

from src.crud.read import get_all  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore


def get_data(year: int | str) -> list[dict[str, Any]]:
    """Get the data from the workout database for a given year.

    :param year: Year to get the data for.
    :type year: str
    :return: data from the workout database for a given year.
    :rtype: list[dict]
    """

    normalized_year = int(year)
    _, table, _ = set_db_and_table(
        datatype="real",
        year=normalized_year,
        create=False,
    )

    return get_all(table)
