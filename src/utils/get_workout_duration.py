"""
Get the workout duration on each date in a given year.
In the case of multiple workouts on the same day,
the duration is the sum of the durations of the workouts.
"""

from datetime import datetime as dt
import os
from pprint import pformat  # type: ignore
from typing import Any
from loguru import logger  # type: ignore
from profiling_tools.profiling_utils import profile  # type: ignore
from datetime_tools.get_duration import get_duration_minutes  # type: ignore
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


def get_all_durations(year: str) -> dict:
    """Get the total duration of all workouts in a given year,
    summing durations for the same date.

    :param year: Year to get the duration of each workout for.
    :type year: str
    :return: Dictionary with the date as the key
        and the duration of the workout as the value.
    :rtype: dict
    """

    data = get_data(year)
    date_and_duration: dict[Any, Any] = {}
    for workout in data:
        if "start_time" not in workout:
            continue

        date = workout["date"]
        start_time = workout["start_time"]
        end_time = workout["end_time"]
        duration = get_duration_minutes(start_time, end_time)

        # Sum durations for the same date
        if date in date_and_duration:
            date_and_duration[date] += duration
        else:
            date_and_duration[date] = duration

    logger.debug(pformat(date_and_duration))

    return date_and_duration


def get_number_of_workouts(year: str) -> int:
    """Get the number of workouts in a given year.

    :param year: Year to get the number of workouts for.
    :type year: str
    :return: Number of workouts in a given year.
    :rtype: int
    """

    data = get_data(year)
    logger.debug(f"{year}, {data}")
    return len(data)


@profile
def main() -> None:
    """Display the duration of each workout in a given year.
    """

    logger.debug(pformat(get_data("2024")))

    year = str(dt.now().year)
    date_and_duration = get_all_durations(year)
    for date, duration in date_and_duration.items():
        logger.debug(f"{date}, {duration}")

    logger.debug(pformat(get_number_of_workouts("2021")))
    logger.debug(pformat(get_number_of_workouts("2022")))
    logger.debug(pformat(get_number_of_workouts("2023")))
    logger.debug(pformat(get_number_of_workouts("2024")))


if __name__ == "__main__":
    main()
