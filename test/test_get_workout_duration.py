from test.conftest import src
from src.helpers.get_workout_duration import get_workout_duration


def test_get_year_and_week():

    assert (
        get_workout_duration("14:45", "15:10") == 25
    )
