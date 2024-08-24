"""
unit test suite for src folder
"""

from datetime import datetime

import pytest

from test.conftest import src

pytestmark = pytest.mark.skip(reason="Skip until ModuleNotFoundError is fixed")

from src.crud.read import show_exercises
from src.helpers.set_db_and_table import set_db_and_table  # type: ignore

import pytest


_, table, _ = set_db_and_table(
    datatype="real",
    year=datetime.strptime("2021", "%Y").year
    )


@pytest.mark.skip(reason="Skip until ModuleNotFoundError is fixed")
def test_show_exercises():
    """Verify that test_show_exercises gives correct exercises for known workout."""
    assert show_exercises(table, "2021-12-16") == [
        "cable_extention",
        "db_front_lateral",
        "seated_rear_db_lateral",
        "pre_exhaust_bb_shrug",
        "toe_to_bar",
    ]
