"""
unit test suite for src folder
"""

# from tinydb import TinyDB
# import pytest

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from src.simulations.simulate_data import get_available_exercises


def test_get_available_exercises():
    """Verify that get_available_exercises includes required exercises for given muscle group."""
    assert all(
        x in get_available_exercises()
        for x in [
            {"barbell bench press": [50, 90]},
            {"dumbbell flys": [10, 18]},
            {"barbell incline press": [30, 70]},
        ]
    )
