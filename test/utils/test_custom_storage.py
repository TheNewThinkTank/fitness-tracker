from pathlib import Path
from uuid import UUID, uuid4

import pytest
import yaml
from tinydb import TinyDB

from src.common.workout_types import legacy_workout_id
from src.utils.custom_storage import YAMLStorage


def test_yaml_storage_round_trip_is_atomic(tmp_path: Path) -> None:
    database_path = tmp_path / "workouts.yml"
    storage = YAMLStorage(database_path)
    payload = {"weight_training_log": {"1": {"date": "2024-01-01"}}}

    storage.write(payload)

    assert storage.read() == payload
    assert list(tmp_path.glob("*.tmp")) == []


def test_yaml_storage_does_not_touch_existing_file(tmp_path: Path) -> None:
    database_path = tmp_path / "workouts.yml"
    database_path.write_text("weight_training_log: {}\n", encoding="utf-8")
    original_mtime = database_path.stat().st_mtime_ns

    YAMLStorage(database_path)

    assert database_path.stat().st_mtime_ns == original_mtime


def test_yaml_storage_surfaces_invalid_yaml(tmp_path: Path) -> None:
    database_path = tmp_path / "workouts.yml"
    database_path.write_text("workouts: [unterminated", encoding="utf-8")

    with pytest.raises(yaml.YAMLError):
        YAMLStorage(database_path).read()


def test_workout_id_is_not_reused_after_delete_and_reopen(tmp_path: Path) -> None:
    database_path = tmp_path / "2024_workouts.yml"
    options = {"workout_table": "weight_training_log", "workout_year": 2024}
    with TinyDB(database_path, storage=YAMLStorage, **options) as database:
        workout_table = database.table("weight_training_log")
        document_id = workout_table.insert({"date": "2024-01-01"})
        original_id = workout_table.get(doc_id=document_id)["id"]
        assert UUID(original_id).version == 4
        workout_table.remove(doc_ids=[document_id])

    with TinyDB(database_path, storage=YAMLStorage, **options) as database:
        workout_table = database.table("weight_training_log")
        replacement_id = workout_table.insert({"date": "2024-01-02"})
        assert replacement_id == document_id
        assert workout_table.get(doc_id=replacement_id)["id"] != original_id


def test_workout_ids_are_immutable_and_unique(tmp_path: Path) -> None:
    with TinyDB(
        tmp_path / "workouts.yml", storage=YAMLStorage,
        workout_table="weight_training_log", workout_year=2024,
    ) as database:
        workout_table = database.table("weight_training_log")
        document_id = workout_table.insert({"date": "2024-01-01"})
        original_id = workout_table.get(doc_id=document_id)["id"]

        with pytest.raises(ValueError, match="immutable"):
            workout_table.update({"id": str(uuid4())}, doc_ids=[document_id])
        with pytest.raises(ValueError, match="Invalid workout document"):
            workout_table.update({"id": "not-a-uuid"}, doc_ids=[document_id])
        with pytest.raises(ValueError, match="Duplicate workout ID"):
            workout_table.insert({"date": "2024-01-02", "id": original_id})

        workout_table.update({"date": "2024-02-01"}, doc_ids=[document_id])
        assert workout_table.get(doc_id=document_id)["id"] == original_id
        assert len(workout_table) == 1


def test_id_migration_preserves_legacy_links_and_is_idempotent(tmp_path: Path) -> None:
    database_path = tmp_path / "2024_workouts.yml"
    original = {"weight_training_log": {"7": {"date": "2024-01-01", "notes": "Keep"}}}
    database_path.write_text(yaml.safe_dump(original), encoding="utf-8")
    original_content = database_path.read_bytes()
    storage = YAMLStorage(
        database_path, workout_table="weight_training_log", workout_year=2024
    )

    assert storage.migrate_workout_ids(dry_run=True) == 1
    assert database_path.read_bytes() == original_content
    assert storage.migrate_workout_ids() == 1
    migrated_content = database_path.read_bytes()
    assert storage.read()["weight_training_log"]["7"] == {
        **original["weight_training_log"]["7"],
        "id": str(legacy_workout_id(2024, 7)),
    }
    assert storage.migrate_workout_ids() == 0
    assert database_path.read_bytes() == migrated_content