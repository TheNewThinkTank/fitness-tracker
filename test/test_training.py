"""
unit test suite for src folder
"""

from tinydb import TinyDB
import pytest

# from ..src.training import show_exercises

# import src.training
# from .src.training import show_exercises
# from src.training import show_exercises


@pytest.fixture
def setup():
    db = TinyDB("data/db.json")
    log = db.table("log")
    return log


def test_show_exercises(setup):
    """unit test placeholder."""
    assert src.training.show_exercises(setup, "2021-12-16") == [
        "cable extentions",
        "dumbbell front laterals",
        "seated rear dumbbell laterals",
        "barbell (pre-exhaust) shrugs",
        "hanging toes-to-bar",
    ]
