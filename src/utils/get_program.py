"""Get the workout program based on the workout date.
"""

import datetime
from functools import lru_cache
from pathlib import Path
from pprint import pformat  # type: ignore
from loguru import logger  # type: ignore
from src.utils.file_conversions.load_yaml import load_yaml_file  # type: ignore
from src.utils.config import settings  # type: ignore


def parse_date(date_str: str) -> datetime.date | None:
    """Parse a date string, returning None for unfilled template placeholders.

    :param date_str: date in the format 'YYYY-MM-DD', or a template string containing Y/M/D
    :type date_str: str
    :return: parsed date, or None if the string looks like an unfilled template
    :rtype: datetime.date | None
    """
    if not isinstance(date_str, str) or any(x in date_str for x in "YMD"):
        return None
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


@lru_cache(maxsize=1)
def _load_programs(path: str) -> list[dict]:
    """Load and parse workout programs from YAML, cached after first read."""
    available_programs = load_yaml_file(path)
    programs = []
    for pgm in available_programs["programs"].values():
        start = parse_date(pgm["start"])
        end = parse_date(pgm["end"])
        if start and end:
            programs.append({"name": pgm["name"], "start": start, "end": end})
    return programs


def get_pgm_from_date(workout_date: str) -> str | None:
    """Get the workout program based on the workout date.

    :param workout_date: date in the format 'YYYY-MM-DD'
    :type workout_date: str
    :return: name of the workout program
    :rtype: str | None
    """
    path = str(Path.cwd() / settings.workout_programs)
    programs = _load_programs(path)
    target = datetime.datetime.strptime(workout_date, "%Y-%m-%d").date()
    for pgm in programs:
        if pgm["start"] <= target <= pgm["end"]:
            return pgm["name"]
    return None


def main() -> None:
    """Get the workout program based on the workout date.
    """

    workout_date = "2022-01-01"
    logger.debug(pformat(get_pgm_from_date(workout_date)))


if __name__ == "__main__":
    main()
