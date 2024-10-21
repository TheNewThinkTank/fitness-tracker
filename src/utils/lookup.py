"""
Convert month names from strings to integer representations
"""

from enum import Enum, unique


@unique
class Months(Enum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12


def get_year_and_month(date: str = "2022-06-27") -> tuple[str, str]:
    """_summary_

    :param date: _description_, defaults to "2022-06-27"
    :type date: str, optional
    :return: _description_
    :rtype: tuple[str, str]
    """

    month_zeropadded = date[5:7]
    month = int(month_zeropadded.removeprefix("0"))
    MONTH = Months(month).name.capitalize()
    YEAR = date[:4]

    return YEAR, MONTH


def main() -> None:
    print(get_year_and_month())


if __name__ == "__main__":
    main()
