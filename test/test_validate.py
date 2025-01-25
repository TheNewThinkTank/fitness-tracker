
import pytest
from unittest.mock import patch, mock_open
import json
from src.utils.validate import (  # type: ignore
    Workout,
    ExercisesFormatError,
    WorkoutValidator,
    WorkoutFactory,
)


def test_workout_model_valid():
    data = {
        "date": "2023-10-01",
        "start": "10:00",
        "end": "11:00",
        "split": "Upper Body",
        "exercises": {
            "pushup": [{"set_number": 1, "reps": 10, "weight": "BODYWEIGHT"}]
        },
        "warmup": None,  # Add optional fields
        "gym": None,
        "note": None,
    }
    workout = Workout(**data)
    assert workout.date == "2023-10-01"
    assert workout.exercises == {"pushup": [{"set_number": 1, "reps": 10, "weight": "BODYWEIGHT"}]}


def test_workout_model_invalid():
    data = {
        "date": "2023-10-01",
        "start": "10:00",
        "end": "11:00",
        "split": "Upper Body",
        "exercises": {},  # Invalid: No exercises
        "warmup": None,  # Add optional fields
        "gym": None,
        "note": None,
    }
    with pytest.raises(ExercisesFormatError, match="There must be at least 1 exercise."):
        Workout(**data)


def test_validate_exercises_valid():
    exercises = {"pushup": [{"set_number": 1, "reps": 10, "weight": "BODYWEIGHT"}]}
    WorkoutValidator.validate_exercises(exercises)


def test_validate_exercises_invalid_empty():
    exercises = {}
    with pytest.raises(
        ExercisesFormatError, match="There must be at least 1 exercise."
    ):
        WorkoutValidator.validate_exercises(exercises)


def test_validate_exercises_invalid_no_sets():
    exercises = {"pushup": []}
    with pytest.raises(ExercisesFormatError, match="There must be at least 1 set."):
        WorkoutValidator.validate_exercises(exercises)


def test_validate_training_set_valid():
    training_set = {"set_number": 1, "reps": 10, "weight": "50 kg"}
    WorkoutValidator._validate_training_set(training_set)


def test_validate_training_set_invalid_missing_fields():
    training_set = {"set_number": 1, "reps": 10}  # Missing "weight"
    with pytest.raises(ExercisesFormatError, match="Each set should have:"):
        WorkoutValidator._validate_training_set(training_set)


def test_validate_training_set_invalid_weight_type():
    training_set = {"set_number": 1, "reps": 10, "weight": 50}  # Weight is not a string
    with pytest.raises(ExercisesFormatError, match="The weight must be a string."):
        WorkoutValidator._validate_training_set(training_set)


def test_validate_training_set_invalid_weight_format():
    training_set = {
        "set_number": 1,
        "reps": 10,
        "weight": "50lbs",
    }  # Invalid weight format
    with pytest.raises(ExercisesFormatError, match="Weight must match regex:"):
        WorkoutValidator._validate_training_set(training_set)


def test_validate_training_set_invalid_reps():
    training_set = {"set_number": 1, "reps": 0, "weight": "50 kg"}  # Reps out of range
    with pytest.raises(
        ExercisesFormatError, match="The 'reps' value must be between 1 and 100."
    ):
        WorkoutValidator._validate_training_set(training_set)


def test_validate_set_numbers_valid():
    exercise = [
        {"set_number": 1, "reps": 10, "weight": "50 kg"},
        {"set_number": 2, "reps": 10, "weight": "50 kg"},
    ]
    WorkoutValidator._validate_set_numbers(exercise)


def test_validate_set_numbers_invalid_start():
    exercise = [
        {"set_number": 2, "reps": 10, "weight": "50 kg"},  # Starts with 2 instead of 1
    ]
    with pytest.raises(
        ExercisesFormatError, match="The first 'set_number' value must be 1."
    ):
        WorkoutValidator._validate_set_numbers(exercise)


def test_validate_set_numbers_invalid_sequence():
    exercise = [
        {"set_number": 1, "reps": 10, "weight": "50 kg"},
        {"set_number": 3, "reps": 10, "weight": "50 kg"},  # Skips 2
    ]
    with pytest.raises(
        ExercisesFormatError, match="'set_number' must be monotonically increasing."
    ):
        WorkoutValidator._validate_set_numbers(exercise)


def test_create_workout():
    data = {
        "date": "2023-10-01",
        "start": "10:00",
        "end": "11:00",
        "split": "Upper Body",
        "exercises": {
            "pushup": [{"set_number": 1, "reps": 10, "weight": "BODYWEIGHT"}]
        },
        "warmup": None,  # Add optional fields
        "gym": None,
        "note": None,
    }
    workout = WorkoutFactory.create_workout(data)
    assert isinstance(workout, Workout)
    assert workout.date == "2023-10-01"


def test_create_workouts_from_json():
    json_data = {
        "weight_training_log": {
            "1": {
                "date": "2023-10-01",
                "start": "10:00",
                "end": "11:00",
                "split": "Upper Body",
                "exercises": {
                    "pushup": [{"set_number": 1, "reps": 10, "weight": "BODYWEIGHT"}]
                },
                "warmup": None,  # Add optional fields
                "gym": None,
                "note": None,
            }
        }
    }
    mock_file = mock_open(read_data=json.dumps(json_data))
    with patch("builtins.open", mock_file):
        workouts = WorkoutFactory.create_workouts_from_json("dummy_path.json")
        assert len(workouts) == 1
        assert isinstance(workouts[0], Workout)
        assert workouts[0].date == "2023-10-01"
