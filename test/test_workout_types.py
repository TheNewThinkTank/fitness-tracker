from datetime import date

import pytest

from src.common.workout_types import WorkoutData, is_workout_record


def test_is_workout_record_accepts_valid_workout_payload():
    payload = {
        "date": "2024-01-01",
        "split": "push",
        "exercises": {
            "bench_press": [
                {"set_number": 1, "reps": 10, "weight": "100 kg"},
            ]
        },
    }

    assert is_workout_record(payload) is True


def test_is_workout_record_rejects_missing_exercise_shape():
    payload = {
        "date": "2024-01-01",
        "split": "push",
        "exercises": {"bench_press": [{"set_number": 1, "reps": 10}]},
    }

    assert is_workout_record(payload) is False


@pytest.mark.parametrize(
    "invalid_date",
    ["2024-02-30", "not-a-date", "20240101", "2024-01-01T09:00:00", 1704067200],
)
def test_is_workout_record_rejects_invalid_dates(invalid_date):
    assert is_workout_record({"date": invalid_date}) is False


def test_workout_data_normalizes_yaml_dates_and_preserves_extensions():
    payload = {
        "date": date(2024, 2, 29),
        "notes": "Deload",
        "exercises": {
            "squat": [
                {"set_number": 1, "reps": 8, "weight": "40 kg", "tempo": "3-1-1"}
            ]
        },
    }

    normalized = WorkoutData.model_validate(payload).model_dump(
        mode="json", exclude_unset=True
    )

    assert normalized == {**payload, "date": "2024-02-29"}


def test_workout_data_rejects_boolean_repetitions():
    payload = {
        "date": "2024-01-01",
        "exercises": {
            "squat": [{"set_number": 1, "reps": True, "weight": "40 kg"}]
        },
    }

    assert is_workout_record(payload) is False
