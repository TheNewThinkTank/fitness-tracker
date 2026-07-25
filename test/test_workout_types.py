from src.common.workout_types import is_workout_record


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
