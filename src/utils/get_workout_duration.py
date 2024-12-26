"""
Get the duration of each workout in a given year.
"""

import sys
from pathlib import Path
# Add the root directory to the PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from icecream import ic  # type: ignore
from datetime import datetime as dt
from profiling_tools.profiling_utils import profile  # type: ignore
from datetime_tools.get_duration import get_duration_minutes  # type: ignore
from src.crud.read import get_all  # type: ignore
from utils.set_db_and_table import set_db_and_table  # type: ignore


def get_data(year: str):
    """Get the data from the workout database for a given year.

    :param year: Year to get the data for.
    :type year: str
    :return: data from the workout database for a given year.
    :rtype: list[dict]
    """

    db, table, _ = set_db_and_table(
        datatype="real",
        year=year,
        )
    
    data = get_all(table)
    # db.close()

    return data


@profile
def get_all_durations(year: str) -> dict:
    """Get the duration of each workout in a given year.

    :return: Dictionary with the date as the key
        and the duration of the workout as the value.
    :rtype: dict
    """

    data = get_data(year)
    date_and_duration = {}
    for workout in data:
        if "start_time" not in workout:
            continue

        date = workout["date"]
        start_time = workout["start_time"]
        end_time = workout["end_time"]
        duration = get_duration_minutes(start_time, end_time)
        date_and_duration[date] = duration
    # pp(date_and_duration)
    return date_and_duration


def get_number_of_workouts(year: str) -> int:
    """Get the number of workouts in a given year.

    :param year: Year to get the number of workouts for.
    :type year: str
    :return: Number of workouts in a given year.
    :rtype: int
    """

    data = get_data(year)
    # ic(year, data)
    return len(data)


def main() -> None:
    """Display the duration of each workout in a given year.
    """

    # print(get_data("2024"))

    year = str(dt.now().year)
    date_and_duration = get_all_durations(year)
    for date, duration in date_and_duration.items():
        ic(date, duration)

    # ic(get_number_of_workouts("2021"))
    # ic(get_number_of_workouts("2022"))
    # ic(get_number_of_workouts("2023"))
    # ic(get_number_of_workouts("2024"))


if __name__ == "__main__":
    main()
