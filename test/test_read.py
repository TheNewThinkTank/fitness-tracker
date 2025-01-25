
from unittest.mock import MagicMock
from tinydb import Query  # type: ignore
from src.crud.read import (  # type: ignore
    get_bw_workouts,
    search_for_exercise,
    get_dates,
    get_dates_and_muscle_groups,
    show_exercises,
    get_all,
    describe_workout,
    show_exercise,
    analyze_workout,
    )


def test_get_bw_workouts():
    mock_table = MagicMock()
    mock_table.all.return_value = [
        {"exercises": {"pushup": [{"weight": "BODYWEIGHT"}]}},
        {"exercises": {"squat": [{"weight": "100kg"}]}},
    ]

    results = get_bw_workouts(mock_table)
    assert len(results) == 1
    assert results[0]["exercises"]["pushup"][0]["weight"] == "BODYWEIGHT"


def test_search_for_exercise():
    mock_table = MagicMock()
    mock_table.all.return_value = [
        {"exercises": {"assisted_pullup": [{"reps": 10}]}},
        {"exercises": {"squat": [{"reps": 5}]}},
    ]

    results = search_for_exercise(mock_table, "assisted_pullup")
    assert len(results) == 1
    assert "assisted_pullup" in results[0]


def test_get_dates():
    mock_table = MagicMock()
    mock_table.__iter__.return_value = [
        {"date": "2023-10-01"},
        {"date": "2023-10-02"},
    ]

    results = get_dates(mock_table)
    assert results == ["2023-10-01", "2023-10-02"]


def test_get_dates_and_muscle_groups():
    mock_table = MagicMock()
    mock_table.__iter__.return_value = [
        {"date": "2023-10-01", "split": "Upper Body"},
        {"date": "2023-10-02", "split": "Lower Body"},
    ]

    results = get_dates_and_muscle_groups(mock_table)
    assert results == {
        "2023-10-01": "Upper Body",
        "2023-10-02": "Lower Body",
    }


def test_show_exercises():
    mock_table = MagicMock()
    mock_table.__iter__.return_value = [
        {"date": "2023-10-01", "exercises": {"pushup": [], "squat": []}},
        {"date": "2023-10-02", "exercises": {"pullup": []}},
    ]

    results = show_exercises(mock_table, "2023-10-01")
    assert results == ["pushup", "squat"]


def test_get_all():
    mock_table = MagicMock()
    mock_table.all.return_value = [
        {"date": "2023-10-01"},
        {"date": "2023-10-02"},
    ]

    results = get_all(mock_table)
    assert results == [
        {"date": "2023-10-01"},
        {"date": "2023-10-02"},
    ]


def test_describe_workout():
    mock_table = MagicMock()
    mock_table.__iter__.return_value = [
        {"date": "2023-10-01", "exercises": {"pushup": [1, 2, 3], "squat": [1, 2]}},
    ]

    results = describe_workout(mock_table, "2023-10-01")
    assert results == {
        "Date of workout": "2023-10-01",
        "pushup": "3 sets",
        "squat": "2 sets",
    }


def test_describe_workout_not_found():
    mock_table = MagicMock()
    mock_table.__iter__.return_value = [
        {"date": "2023-10-01", "exercises": {"pushup": [1, 2, 3]}},
    ]

    results = describe_workout(mock_table, "2023-10-02")
    assert results is None


def test_show_exercise():
    mock_table = MagicMock()
    mock_table.__iter__.return_value = [
        {"date": "2023-10-01", "exercises": {"pushup": [{"reps": 10}]}},
    ]

    results = show_exercise(mock_table, "pushup", "2023-10-01")
    assert results == [{"reps": 10}]


def test_show_exercise_not_found():
    mock_table = MagicMock()
    mock_table.__iter__.return_value = [
        {"date": "2023-10-01", "exercises": {"pushup": [{"reps": 10}]}},
    ]

    results = show_exercise(mock_table, "squat", "2023-10-01")
    assert results == []


def test_analyze_workout():
    mock_table = MagicMock()
    mock_table.search.return_value = [
        {"exercises": {"pushup": [{"reps": 10}]}},
        {"exercises": {"pushup": [{"reps": 12}]}},
    ]

    results = analyze_workout(mock_table, "pushup")
    assert results == [[{"reps": 10}], [{"reps": 12}]]
