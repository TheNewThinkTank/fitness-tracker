from datetime import date

import pytest

from src.common.measurements import BodyMeasurement
from src.utils.config import settings
from src.utils.state_store import StateStore, VersionConflict


@pytest.fixture
def store(tmp_path):
    original = settings.get("STATE_DIR")
    settings.set("STATE_DIR", str(tmp_path))
    yield StateStore()
    settings.set("STATE_DIR", original)


def test_reads_do_not_create_database_and_measurements_upsert_atomically(store):
    assert store.measurements() == []
    assert not store.path.exists()
    measurement = BodyMeasurement(date="2026-01-01", weight_kg=80).model_dump(mode="json")
    store.save_measurements([measurement])
    store.save_measurements([{**measurement, "weight_kg": 81}])
    assert len(store.measurements()) == 1
    assert store.measurements()[0]["weight_kg"] == 81
    assert store.delete_measurement("2026-01-01")


def test_workout_optimistic_concurrency_and_delete(store):
    record = {"id": store.new_id(), "date": "2026-01-01", "exercises": {}}
    assert store.save_workout(record) == 1
    assert store.save_workout(record, expected_version=1) == 2
    with pytest.raises(VersionConflict):
        store.save_workout(record, expected_version=1)
    assert store.save_workout(record, expected_version=2, deleted=True) == 3
    assert store.workout(record["id"])["deleted"]


def test_sessions_expire_and_password_changes_revoke_them(store):
    store.create_session("hash", "csrf", 200, 100)
    assert store.session("hash", 100)["csrf_token"] == "csrf"
    assert store.session("hash", 200) is None
    store.configure("password_hash", "new-hash")
    assert store.session("hash", 100) is None


def test_measurements_reject_unknown_fields_and_empty_values():
    with pytest.raises(ValueError):
        BodyMeasurement(date=date(2026, 1, 1))
    with pytest.raises(ValueError):
        BodyMeasurement(date="2026-02-30", weight_kg=80)
    with pytest.raises(ValueError):
        BodyMeasurement(date="2026-01-01", weight_kg=80, secret="ignored")