"""Shared workout typing helpers for the fitness tracker domain."""

from __future__ import annotations

from typing import Any, TypedDict


class ExerciseSet(TypedDict, total=False):
    """Represents a single exercise set inside a workout record."""

    set_number: int
    reps: int
    weight: str


class WorkoutRecord(TypedDict):
    """Represents a normalized workout record stored in the database."""

    date: str
    split: str
    exercises: dict[str, list[ExerciseSet]]


def is_workout_record(value: Any) -> bool:
    """Return True when a value matches the shared workout record shape."""

    if not isinstance(value, dict):
        return False

    if not isinstance(value.get("date"), str):
        return False
    if not isinstance(value.get("split"), str):
        return False

    exercises = value.get("exercises")
    if not isinstance(exercises, dict):
        return False

    for exercise_sets in exercises.values():
        if not isinstance(exercise_sets, list):
            return False
        for set_data in exercise_sets:
            if not isinstance(set_data, dict):
                return False
            if not isinstance(set_data.get("set_number"), int):
                return False
            if not isinstance(set_data.get("reps"), int):
                return False
            if not isinstance(set_data.get("weight"), str):
                return False

    return True
