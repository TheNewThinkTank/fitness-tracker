from datetime import date
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, contextmanager
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

import pytest

from src.common.measurements import BodyMeasurement
from src.utils.config import PROJECT_ROOT, settings
from src.utils.state_store import SCHEMA, StateStore, VersionConflict


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


def test_permission_failure_does_not_commit_a_workout(store, monkeypatch):
    store.configure("fixture", "existing database")
    original_chmod = Path.chmod

    def denied_permission(path, mode, *arguments, **options):
        if path == store.path:
            raise PermissionError("Cannot secure the state database")
        return original_chmod(path, mode, *arguments, **options)

    monkeypatch.setattr(Path, "chmod", denied_permission)
    record = {"id": store.new_id(), "date": "2026-01-01", "exercises": {}}
    with pytest.raises(PermissionError):
        store.save_workout(record)
    assert store.workout(record["id"]) is None


def test_schema_migration_preserves_unversioned_state(store):
    record = {"id": store.new_id(), "date": "2026-01-01", "exercises": {}}
    store.path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(store.path) as connection:
        connection.executescript(SCHEMA)
        connection.execute("INSERT INTO workouts VALUES (?, ?, ?, 0, 3)", (record["id"], record["date"], json.dumps(record)))
        connection.execute("INSERT INTO configuration VALUES (?, ?)", ("program:fixture", "legacy targets"))
        connection.execute("INSERT INTO sessions VALUES (?, ?, ?)", ("legacy-session", "csrf", 200))
    store.configure("fixture", "new setting")
    assert store.workout(record["id"]) == {"record": record, "deleted": False, "version": 3}
    assert store.configuration("program:fixture") == "legacy targets"
    assert store.session("legacy-session", 100)["csrf_token"] == "csrf"
    with store.connection() as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] > 0


def test_schema_from_newer_app_is_rejected_without_modification(store):
    store.configure("fixture", "existing setting")
    with sqlite3.connect(store.path) as connection:
        connection.execute("PRAGMA user_version = 999")
    before = store.path.read_bytes()
    with pytest.raises(sqlite3.DatabaseError, match="newer"):
        store.configuration("fixture")
    with pytest.raises(sqlite3.DatabaseError, match="newer"):
        store.configure("fixture", "must not be saved")
    assert store.path.read_bytes() == before


def test_failed_schema_migration_rolls_back_all_changes(store, monkeypatch):
    monkeypatch.setattr("src.utils.state_store.MIGRATIONS", (SCHEMA + "\nINVALID SQL;\n",))
    with pytest.raises(sqlite3.OperationalError):
        store.configure("fixture", "must not be saved")
    with sqlite3.connect(store.path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 0
        assert connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall() == []


def test_backup_includes_committed_wal_data_and_is_self_contained(store, tmp_path):
    store.configure("fixture", "original")
    destination = tmp_path / "backup/snapshot.sqlite3"
    with sqlite3.connect(store.path) as reader:
        reader.execute("PRAGMA journal_mode=WAL").fetchone()
        reader.execute("BEGIN")
        reader.execute("SELECT value FROM configuration").fetchall()
        store.configure("fixture", "committed in WAL")
        assert Path(str(store.path) + "-wal").stat().st_size > 0
        store.backup(destination)
        assert StateStore(destination).configuration("fixture") == "committed in WAL"
        with sqlite3.connect(destination) as snapshot:
            assert snapshot.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
        reader.rollback()
    assert destination.stat().st_mode & 0o777 == 0o600
    assert list(destination.parent.iterdir()) == [destination]


def test_backup_of_empty_state_does_not_create_live_database(store, tmp_path):
    destination = tmp_path / "backup/snapshot.sqlite3"
    store.backup(destination)
    assert not store.path.exists()
    assert StateStore(destination).workout_rows() == []


def test_backup_refuses_to_overwrite_existing_or_live_state(store, tmp_path):
    store.configure("fixture", "original")
    destination = tmp_path / "existing.sqlite3"
    destination.write_bytes(b"existing backup")
    with pytest.raises(FileExistsError):
        store.backup(destination)
    with pytest.raises(ValueError, match="live database"):
        store.backup(store.path)
    assert destination.read_bytes() == b"existing backup"
    assert store.configuration("fixture") == "original"


def test_backup_rejects_newer_state_without_leaving_a_partial_file(store, tmp_path):
    store.configure("fixture", "original")
    with sqlite3.connect(store.path) as connection:
        connection.execute("PRAGMA user_version=999")
    destination = tmp_path / "backup/snapshot.sqlite3"
    with pytest.raises(sqlite3.DatabaseError, match="newer"):
        store.backup(destination)
    assert not destination.exists()


def test_creation_key_replays_one_workout_without_deduplicating_dates(store):
    payload = {"date": "2026-01-01", "exercises": {}}
    key = store.new_id()
    created = store.create_workout(payload, idempotency_key=key)
    assert store.create_workout(payload, idempotency_key=key) == created
    distinct = store.create_workout(payload, idempotency_key=store.new_id())
    assert distinct["id"] != created["id"]
    assert len(store.workout_rows()) == 2
    with pytest.raises(VersionConflict, match="different workout data"):
        store.create_workout({**payload, "notes": "Changed payload"}, idempotency_key=key)
    assert len(store.workout_rows()) == 2


def test_creation_key_cannot_recreate_an_edited_or_deleted_workout(store):
    payload = {"date": "2026-01-01", "exercises": {}}
    key = store.new_id()
    created = store.create_workout(payload, idempotency_key=key)
    store.save_workout({**created, "notes": "Edited"}, expected_version=1)
    with pytest.raises(VersionConflict, match="changed or deleted"):
        store.create_workout(payload, idempotency_key=key)
    store.save_workout(created, expected_version=2, deleted=True)
    with pytest.raises(VersionConflict, match="changed or deleted"):
        store.create_workout(payload, idempotency_key=key)
    assert len(store.workout_rows()) == 1


def test_concurrent_creation_retries_commit_only_once(store):
    payload = {"date": "2026-01-01", "exercises": {}}
    key = store.new_id()

    def create(attempt):
        return store.create_workout(payload, idempotency_key=key)

    with ThreadPoolExecutor(max_workers=4) as executor:
        records = list(executor.map(create, range(8)))
    assert all(record == records[0] for record in records)
    assert len(store.workout_rows()) == 1


def test_version_one_schema_upgrades_for_creation_keys(store):
    store.path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(store.path) as connection:
        connection.executescript(SCHEMA)
        connection.execute("PRAGMA user_version=1")
    created = store.create_workout({"date": "2026-01-01", "exercises": {}}, idempotency_key=store.new_id())
    assert store.workout(created["id"])["version"] == 1
    with store.connection() as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2


def test_analytics_snapshot_is_consistent_during_a_concurrent_commit(store, monkeypatch):
    record = {"id": store.new_id(), "date": "2026-01-01", "notes": "Before", "exercises": {}}
    store.save_workout(record)
    store.save_measurements([{"date": "2026-01-01", "weight_kg": 80}])
    store.configure("program:fixture", "Before")
    store.configure("password_hash", "Must not be included in analytics")
    with closing(sqlite3.connect(store.path)) as connection:
        connection.execute("PRAGMA journal_mode=WAL").fetchone()
    original_connection = store.connection
    changed = False

    def concurrent_commit(statement):
        nonlocal changed
        if not changed and statement.startswith("SELECT document FROM measurements ORDER BY date"):
            changed = True
            with original_connection(write=True) as writer:
                writer.execute("UPDATE workouts SET document = ?, version = 2", (json.dumps({**record, "notes": "After"}),))
                writer.execute("UPDATE measurements SET document = ?", (json.dumps({"date": "2026-01-01", "weight_kg": 81}),))
                writer.execute("UPDATE configuration SET value = ? WHERE key = ?", ("After", "program:fixture"))

    @contextmanager
    def tracked_connection(*arguments, **options):
        with original_connection(*arguments, **options) as connection:
            connection.set_trace_callback(concurrent_commit)
            yield connection

    monkeypatch.setattr(store, "connection", tracked_connection)
    snapshot = store.snapshot()
    assert changed
    assert snapshot.workouts[0]["record"]["notes"] == "Before"
    assert snapshot.measurements[0]["weight_kg"] == 80
    assert snapshot.configuration == {"program:fixture": "Before"}
    assert store.workout(record["id"])["record"]["notes"] == "After"
    assert store.measurements()[0]["weight_kg"] == 81


def test_project_dotenv_loads_a_quoted_path_from_an_unrelated_directory(tmp_path):
    project = tmp_path / "project"
    configuration_file = project / "src/utils/config.py"
    configuration_file.parent.mkdir(parents=True)
    shutil.copyfile(PROJECT_ROOT / "src/utils/config.py", configuration_file)
    (project / ".config").mkdir()
    (project / ".config/settings.toml").write_text(
        '[default]\ndata_dir = "data"\nathlete = "default"\n', encoding="utf-8"
    )
    data_directory = tmp_path / "My Drive/fitness-tracker-data/test_athlete"
    data_directory.mkdir(parents=True)
    (project / ".env").write_text(
        f'FITNESS_TRACKER_DATA_DIR="{data_directory}"\n'
        "FITNESS_TRACKER_ATHLETE=test_athlete\n"
        "FITNESS_TRACKER_ENABLE_WRITES=true\n",
        encoding="utf-8",
    )
    environment = {
        key: value for key, value in os.environ.items()
        if not key.startswith(("FITNESS_TRACKER_", "DYNACONF_"))
    }
    result = subprocess.run(
        [sys.executable, "-c", (
            "import json, runpy, sys\n"
            "configuration = runpy.run_path(sys.argv[1])\n"
            "configuration['validate_settings']()\n"
            "settings = configuration['settings']\n"
            "print(json.dumps([settings.DATA_DIR, settings.ATHLETE, settings.ENABLE_WRITES]))\n"
        ), str(configuration_file)],
        cwd=tmp_path, env=environment, capture_output=True, text=True, check=True,
    )
    assert json.loads(result.stdout) == [str(data_directory), "test_athlete", True]


def test_default_data_directory_preserves_a_workout_across_processes(tmp_path):
    original = {key: settings.get(key) for key in ("DATA_DIR", "STATE_DIR")}
    data_directory = tmp_path / "My Drive/fitness-tracker-data/test_athlete"
    data_directory.mkdir(parents=True)
    settings.set("DATA_DIR", str(data_directory))
    settings.set("STATE_DIR", "")
    try:
        store = StateStore()
        assert store.path == data_directory / ".state/tracker.sqlite3"
        assert store.workout_rows() == []
        assert not store.path.exists()
        record = {"id": store.new_id(), "date": "2026-01-01", "exercises": {}}
        assert store.save_workout(record) == 1
        result = subprocess.run(
            [sys.executable, "-c", (
                "import json, sys\n"
                "from src.utils.state_store import state_store\n"
                "print(json.dumps(state_store.workout(sys.argv[1])))\n"
            ), record["id"]],
            cwd=PROJECT_ROOT,
            env={**os.environ, "FITNESS_TRACKER_DATA_DIR": str(data_directory), "FITNESS_TRACKER_STATE_DIR": ""},
            capture_output=True, text=True, check=True,
        )
        assert json.loads(result.stdout) == {"record": record, "deleted": False, "version": 1}
        assert store.path.stat().st_mode & 0o777 == 0o600
    finally:
        for key, value in original.items():
            settings.set(key, value)


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