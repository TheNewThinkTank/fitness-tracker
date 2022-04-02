"""
unit test suite for src folder
"""

import json
from tinydb import TinyDB
import pytest

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from src.CRUD.training import show_exercises


@pytest.fixture
def setup():
    datatype = "real"
    data = json.load(open(file="./config.json", encoding="utf-8"))
    db = (
        TinyDB(data["real_workout_database"])
        if datatype == "real"
        else TinyDB(data["simulated_workout_database"])
    )
    table = (
        db.table(data["real_weight_table"])
        if datatype == "real"
        else db.table(data["simulated_weight_table"])
    )
    # db = TinyDB("data/db.json")
    # log = db.table("log")
    return table


def test_show_exercises(setup):
    """Verify that test_show_exercises gives correct exercises for known workout."""
    assert show_exercises(setup, "2021-12-16") == [
        "cable extentions",
        "dumbbell front laterals",
        "seated rear dumbbell laterals",
        "barbell (pre-exhaust) shrugs",
        "hanging toes-to-bar",
    ]
