
import pytest
from src.utils.get_workout_duration import (  # type: ignore
    get_data,
    get_all_durations,
    get_number_of_workouts,
)


def test_get_data():
    year = "2021"
    expected_data = {
        "date": "2021-12-11",
        "split": "legs",
        "exercises": {
            "squat": [
                {"set_number": 1, "reps": 8, "weight": "70 kg"},
                {"set_number": 2, "reps": 8, "weight": "80 kg"},
                {"set_number": 3, "reps": 5, "weight": "90 kg"},
                {"set_number": 4, "reps": 5, "weight": "90 kg"},
            ],
            "deadlift": [
                {"set_number": 1, "reps": 8, "weight": "70 kg"},
                {"set_number": 2, "reps": 8, "weight": "80 kg"},
                {"set_number": 3, "reps": 5, "weight": "90 kg"},
                {"set_number": 4, "reps": 5, "weight": "90 kg"},
            ],
            "legpress": [
                {"set_number": 1, "reps": 8, "weight": "90 kg"},
                {"set_number": 2, "reps": 8, "weight": "90 kg"},
            ],
            "leg_extention": [
                {"set_number": 1, "reps": 15, "weight": "64 kg"},
                {"set_number": 2, "reps": 12, "weight": "73 kg"},
                {"set_number": 3, "reps": 10, "weight": "73 kg"},
                {"set_number": 4, "reps": 15, "weight": "64 kg"},
            ],
            "seated_calf_raise": [
                {"set_number": 1, "reps": 12, "weight": "82 kg"},
                {"set_number": 2, "reps": 12, "weight": "82 kg"},
                {"set_number": 3, "reps": 15, "weight": "82 kg"},
                {"set_number": 4, "reps": 15, "weight": "82 kg"},
            ],
            "lunge": [
                {"set_number": 1, "reps": 14, "weight": "0 kg"},
                {"set_number": 2, "reps": 14, "weight": "0 kg"},
                {"set_number": 3, "reps": 14, "weight": "0 kg"},
                {"set_number": 4, "reps": 14, "weight": "0 kg"},
                {"set_number": 5, "reps": 14, "weight": "0 kg"},
            ],
        },
    }

    assert get_data(year)[0] == expected_data


@pytest.mark.skip("Solve FileNotFoundError: No such file or directory: 'stats/get_all_durations.stats'")
def test_get_all_durations():
    year = "2024"
    expected_duration = {
        "2024-01-07": 32,
        "2024-01-10": 29,
        "2024-01-12": 40,
        "2024-01-18": 29,
        "2024-01-22": 27,
        "2024-01-27": 52,
        "2024-02-01": 32,
        "2024-02-11": 39,
        "2024-02-18": 62,
        "2024-02-20": 30,
        "2024-02-23": 34,
        "2024-02-25": 53,
        "2024-03-03": 35,
        "2024-03-05": 32,
        "2024-03-09": 50,
        "2024-03-16": 32,
        "2024-03-17": 28,
        "2024-03-24": 48,
        "2024-03-27": 31,
        "2024-03-28": 31,
        "2024-03-30": 38,
        "2024-04-01": 26,
        "2024-04-11": 30,
        "2024-04-12": 33,
        "2024-04-13": 25,
        "2024-04-20": 24,
        "2024-05-05": 37,
        "2024-06-08": 27,
        "2024-06-11": 20,
        "2024-06-13": 38,
        "2024-06-18": 24,
        "2024-06-29": 10,
        "2024-07-06": 43,
        "2024-07-07": 10,
        "2024-07-09": 30,
        "2024-07-11": 23,
        "2024-07-13": 29,
        "2024-07-15": 39,
        "2024-07-17": 36,
        "2024-07-18": 19,
        "2024-07-27": 19,
        "2024-07-29": 20,
        "2024-07-31": 19,
        "2024-08-04": 27,
        "2024-08-05": 25,
        "2024-08-06": 17,
        "2024-08-10": 45,
        "2024-08-15": 22,
        "2024-08-16": 14,
        "2024-08-22": 14,
        "2024-09-08": 29,
        "2024-09-16": 15,
        "2024-09-22": 11,
        "2024-10-05": 41,
        "2024-10-07": 16,
        "2024-10-10": 18,
        "2024-10-13": 19,
        "2024-10-28": 34,
        "2024-10-31": 30,
        "2024-11-09": 25,
        "2024-12-06": 17,
        "2024-12-07": 32,
        "2024-12-22": 36,
        "2024-12-23": 28,
        "2024-12-25": 32,
        "2024-12-28": 35,
    }

    assert get_all_durations(year) == expected_duration


def test_get_number_of_workouts():
    assert get_number_of_workouts("2021") == 8
    assert get_number_of_workouts("2022") == 107
    assert get_number_of_workouts("2023") == 72
    assert get_number_of_workouts("2024") == 66
