import pytest

from src.utils.get_program import get_pgm_from_date


@pytest.mark.parametrize(
    ("workout_date", "expected_program"),
    [("2022-01-01", "4-SPLIT"), ("2022-04-01", "PPL"), ("2022-07-01", "GVT")],
)
def test_get_pgm_from_date(workout_date, expected_program):
    assert get_pgm_from_date(workout_date) == expected_program
