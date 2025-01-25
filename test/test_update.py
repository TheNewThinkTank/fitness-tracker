
from unittest.mock import MagicMock
from tinydb import TinyDB
from src.crud.update import (  # type: ignore
    filter_exercises_with_whitespace,
    clean_exercise_name,
    clean_exercise_names
)

# def setup():
#     MOCK_DB = TinyDB("test/test_db.json")
#     test_table = MOCK_DB.table("test_log")
#     return test_table

# def test_clean_exercise_name():
#     assert clean_exercise_name("bench press") == "bench_press"
#     assert clean_exercise_name("bench  press") == "bench_press"
#     assert clean_exercise_name("bench_press") == "bench_press"
#     assert clean_exercise_name("bench_ press") == "bench_press"
#     assert clean_exercise_name("bench_  press") == "bench_press"
#     assert clean_exercise_name("bench  _  press") == "bench_press"
#     assert clean_exercise_name("shoulder press_") == "shoulder_press"


def test_filter_exercises_with_whitespace():
    workout_data = [
        {"date": "2023-10-01", "split": "Upper Body", "exercises": {"push up": []}},
        {"date": "2023-10-02", "split": "Lower Body", "exercises": {"squat": []}},
    ]

    results = filter_exercises_with_whitespace(workout_data)
    assert len(results) == 1
    assert results[0]["date"] == "2023-10-01"
    assert results[0]["exercises_with_whitespace"] == ["push up"]


def test_clean_exercise_name():
    # Test replacing spaces with underscores
    assert clean_exercise_name("push up") == "push_up"
    # Test replacing multiple spaces with a single underscore
    assert clean_exercise_name("push  up") == "push_up"
    # Test replacing underscores and spaces with a single underscore
    assert clean_exercise_name("push_up") == "push_up"
    # Test removing trailing underscores
    assert clean_exercise_name("push_up_") == "push_up"
    # Test mixed cases
    assert clean_exercise_name("push_up down") == "push_up_down"


def test_clean_exercise_names():
    mock_table = MagicMock()
    mock_table.all.return_value = [
        {"date": "2023-10-01", "split": "Upper Body", "exercises": {"push up": [{"reps": 10}]}},
        {"date": "2023-10-02", "split": "Lower Body", "exercises": {"squat": [{"reps": 5}]}},
    ]

    clean_exercise_names(mock_table)

    # Check if the table was updated with cleaned exercise names
    updates = mock_table.update_multiple.call_args[0][0]
    assert len(updates) == 2
    assert updates[0]["exercises"] == {"push_up": [{"reps": 10}]}
    assert updates[1]["exercises"] == {"squat": [{"reps": 5}]}
