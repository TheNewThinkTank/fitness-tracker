
import os
import pytest
from tinydb import TinyDB
from src.utils.custom_storage import YAMLStorage  # type: ignore
from src.crud.read import show_exercises  # type: ignore

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "..", "fixtures", "workouts_fixture.yml")


@pytest.fixture
def table():
    db = TinyDB(FIXTURE_PATH, storage=YAMLStorage)
    yield db.table("weight_training_log")
    db.close()


def test_show_exercises(table):
    """Verify that show_exercises returns the correct exercises for a known workout."""
    assert show_exercises(table, "2021-12-16") == [
        "cable_extention",
        "db_front_lateral",
        "seated_rear_db_lateral",
        "pre_exhaust_bb_shrug",
        "toe_to_bar",
    ]
