"""Get the number of workouts in a given year."""

from pprint import pformat  # type: ignore
from loguru import logger  # type: ignore
from src.utils.get_data import get_data  # type: ignore


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


def main() -> None:
    """Number of workouts in a given year.
    """

    logger.debug(pformat(get_data("2024")))

    logger.debug(pformat(get_number_of_workouts("2021")))
    logger.debug(pformat(get_number_of_workouts("2022")))
    logger.debug(pformat(get_number_of_workouts("2023")))
    logger.debug(pformat(get_number_of_workouts("2024")))


if __name__ == "__main__":
    main()
