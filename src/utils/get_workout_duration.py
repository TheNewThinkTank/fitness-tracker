"""
Get the workout duration on each date in a given year.
In the case of multiple workouts on the same day,
the duration is the sum of the durations of the workouts.
"""

from datetime import datetime as dt
from pprint import pformat  # type: ignore
from typing import Any
from loguru import logger  # type: ignore
from profiling_tools.profiling_utils import profile  # type: ignore
from datetime_tools.get_duration import get_duration_minutes  # type: ignore
from src.utils.get_data import get_data  # type: ignore


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


@profile
def main() -> None:
    """Display the duration of each workout in a given year.
    """

    logger.debug(pformat(get_data("2024")))

    year = str(dt.now().year)
    date_and_duration = get_all_durations(year)
    for date, duration in date_and_duration.items():
        logger.debug(f"{date}, {duration}")


if __name__ == "__main__":
    main()
