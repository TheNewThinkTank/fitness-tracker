import datetime

from test.conftest import src
from src.utils.get_year_and_week import get_year_and_week


def test_get_year_and_week():
    test_dates = ["2022-10-29", "2022-10-30", "2021-01-01"]
    date_str = test_dates[-1]
    year, week = get_year_and_week(date_str)
    assert year == "2021"
    assert week == 1

    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    year, week, day_of_week = dt.isocalendar()
    assert year == 2020
    assert week == 53
    assert day_of_week == 5
