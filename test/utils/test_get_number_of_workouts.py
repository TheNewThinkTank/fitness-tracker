
from src.utils.get_number_of_workouts import get_number_of_workouts  # type: ignore


def test_get_number_of_workouts():
    assert get_number_of_workouts("2021") == 8
    assert get_number_of_workouts("2022") == 107
    assert get_number_of_workouts("2023") == 72
    assert get_number_of_workouts("2024") == 66
