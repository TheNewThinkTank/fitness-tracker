"""
unit test suite for simulations
"""

import pytest

from test.conftest import src
from src.simulations.workout_simulator import (
    ExerciseSelector,
    WorkoutSimulator,
    WorkoutFormatter
)


@pytest.mark.parametrize(
    "test_input_reps,expected",
    [
        (1, "9.75 kg"),
        (2, "9.50 kg"),
        (3, "9.25 kg"),
        (4, "9.00 kg"),
        (5, "8.75 kg"),
        (6, "8.50 kg"),
        (7, "8.25 kg"),
        (8, "8.00 kg"),
        (9, "7.75 kg"),
        (10, "7.50 kg"),
    ],
)
def test_high_reps_low_weight(test_input_reps, expected):
    """Verify that high_reps_low_weight gives lower weight for higher reps."""
    # simulated_workout = SimulateWorkout("2021-01-01", 1)
    # weight_choice = simulated_workout.high_reps_low_weight([2, 10], test_input_reps)
    # assert weight_choice == expected
    ...


'''
@pytest.mark.parametrize(
    "test_input_progression,expected",
    [
        (1, "8.75 kg"),
        (1.01, "8.84 kg"),
        (1.02, "8.93 kg"),
        (1.03, "9.01 kg"),
        (1.04, "9.10 kg"),
    ],
)
def test_progression(test_input_progression, expected):
    """Verify that progression factor estimates weights correctly"""
    simulated_workout = SimulateWorkout("2021-01-01", test_input_progression)
    weight_choice = simulated_workout.high_reps_low_weight([2, 10], 5)
    assert weight_choice == expected
'''
