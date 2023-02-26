from context import src
from src.helpers.get_program import get_pgm_from_date


def test_get_pgm_from_date():
    workout_date = "2022-01-01"
    assert get_pgm_from_date(workout_date) == "4-SPLIT"
