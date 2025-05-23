"""Get the workout program based on the workout date.
"""

from datetime import datetime as dt
from pathlib import Path
from pprint import pformat  # type: ignore
from loguru import logger  # type: ignore
from src.utils.file_conversions.load_yaml import load_yaml_file  # type: ignore
from src.utils.config import settings  # type: ignore


# TODO: Move to datetime package
def parse_date(date_str: str) -> dt | None:
    """Parse the date string.

    :param date_str: date in the format 'YYYY-MM-DD'
    :type date_str: str
    :return: date object
    :rtype: dt | None
    """
    if isinstance(date_str, str) and any(x in date_str for x in "YMD"):
        return None
    return dt.strptime(date_str, "%Y-%m-%d") if isinstance(date_str, str) else date_str


def get_pgm_from_date(workout_date: str) -> str | None:
    """Get the workout program based on the workout date.

    :param workout_date: date in the format 'YYYY-MM-DD'
    :type workout_date: str
    :return: name of the workout program
    :rtype: str
    """

    workout_programs_path = Path.cwd() / settings.workout_programs
    available_programs = load_yaml_file(workout_programs_path)

    programs = []
    for pgm in available_programs["programs"].values():
        start = parse_date(pgm["start"])
        end = parse_date(pgm["end"])
        if start and end:
            programs.append({"name": pgm["name"], "start": start, "end": end})

    workout_date_dt = dt.strptime(workout_date, "%Y-%m-%d").date()
    for pgm in programs:
        if pgm["start"] <= workout_date_dt <= pgm["end"]:
            return pgm["name"]

    return None


def main() -> None:
    """Get the workout program based on the workout date.
    """

    workout_date = "2022-01-01"
    logger.debug(pformat(get_pgm_from_date(workout_date)))


if __name__ == "__main__":
    main()
