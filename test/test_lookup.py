from test.conftest import src
from src.utils.lookup import get_year_and_month


def test_get_year_and_month():
    assert get_year_and_month(date="2022-06-27") == ("2022", "June")
