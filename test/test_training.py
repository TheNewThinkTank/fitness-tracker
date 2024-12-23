"""
"""

from datetime import datetime
# from test.conftest import src
from src.crud.read import show_exercises  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore

_, table, _ = set_db_and_table(
    datatype="real",
    year=datetime.strptime("2021", "%Y").year
    )


def test_show_exercises():
    """Verify that test_show_exercises gives correct exercises for known workout."""
    assert show_exercises(table, "2021-12-16") == [
        "cable_extention",
        "db_front_lateral",
        "seated_rear_db_lateral",
        "pre_exhaust_bb_shrug",
        "toe_to_bar",
    ]
