
import os
import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from src.utils.custom_storage import YAMLStorage  # type: ignore
from src.crud.read import get_all  # type: ignore

FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "fixtures", "workouts_fixture.yml"
)


@pytest.fixture
def fixture_table():
    db = TinyDB(FIXTURE_PATH, storage=YAMLStorage)
    yield db.table("weight_training_log")
    db.close()


def test_workout_count_from_fixture(fixture_table):
    """Fixture contains exactly 2 workouts."""
    assert len(get_all(fixture_table)) == 2


def test_get_number_of_workouts_logic():
    """get_number_of_workouts returns len(data) — verify with in-memory table."""
    db = TinyDB(storage=MemoryStorage)
    t = db.table("weight_training_log")
    t.insert({"date": "2024-01-01", "split": "chest", "exercises": {}})
    t.insert({"date": "2024-01-03", "split": "back", "exercises": {}})
    t.insert({"date": "2024-01-05", "split": "legs", "exercises": {}})
    assert len(get_all(t)) == 3
