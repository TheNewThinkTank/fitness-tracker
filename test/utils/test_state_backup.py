import json
import hashlib
import os
import sqlite3
import stat
import subprocess
import sys
from zipfile import ZipFile, ZipInfo

import pytest
import yaml

from src.utils.config import PROJECT_ROOT, settings
from src.utils.state_backup import METADATA, STATE_MEMBER, create_backup, restore_backup
from src.utils.state_store import StateStore
from src.utils.training_metadata import metadata_path


@pytest.fixture
def backup_state(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    original = {key: settings.get(key) for key in ("DATA_DIR", "REAL_WORKOUT_DATABASE")}
    settings.set("DATA_DIR", str(data))
    settings.set("REAL_WORKOUT_DATABASE", str(data / "<YEAR>_workouts.yml"))
    store = StateStore(tmp_path / "state/tracker.sqlite3")
    record = {"id": store.new_id(), "date": "2026-01-01", "notes": "Private workout notes", "exercises": {"squat": [{"set_number": 1, "reps": 5, "weight": "60 kg"}]}}
    (data / "2026_workouts.yml").write_text(yaml.safe_dump({"weight_training_log": {"1": record}}), encoding="utf-8")
    store.save_workout(record)
    store.save_workout(record, expected_version=1, deleted=True)
    store.configure("password_hash", "fixture-only-password-hash")
    store.configure("program:fixture", json.dumps({"planned_workouts": 20, "targets": []}))
    store.save_measurements([{"date": "2026-01-01", "weight_kg": 80}])
    store.create_session("session", "csrf", 200, 100)
    store.allow_login("client", 100)
    try:
        yield data, store, record
    finally:
        for key, value in original.items():
            settings.set(key, value)


def test_full_backup_restores_archives_metadata_and_private_state(backup_state, tmp_path):
    data, store, record = backup_state
    before = (data / "2026_workouts.yml").read_bytes()
    backup = create_backup(tmp_path / "backups", store=store)
    assert backup.stat().st_mode & 0o777 == 0o600
    with ZipFile(backup) as archive:
        assert {STATE_MEMBER, "manifest.json", "2026_workouts.yml"} <= set(archive.namelist())
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["format"] == "fitness-tracker-backup-v1"
        assert manifest["workout_table"] == settings.REAL_WEIGHT_TABLE
        assert "API_TOKEN" not in manifest
    restored = restore_backup(backup, tmp_path / "restored")
    restored_store = StateStore(restored / STATE_MEMBER)
    assert (restored / "2026_workouts.yml").read_bytes() == before
    assert (data / "2026_workouts.yml").read_bytes() == before
    assert restored_store.workout(record["id"]) == store.workout(record["id"])
    assert restored_store.workout(record["id"])["deleted"]
    assert restored_store.configuration("password_hash") == store.configuration("password_hash")
    assert restored_store.configuration("program:fixture") == store.configuration("program:fixture")
    assert restored_store.measurements() == store.measurements()
    assert restored_store.session("session", 100) is None
    assert restored_store.read("SELECT * FROM login_attempts") == []
    assert store.session("session", 100) is not None
    for setting, member in METADATA.items():
        if metadata_path(setting).is_file():
            assert (restored / member).read_bytes() == metadata_path(setting).read_bytes()
    assert restored.stat().st_mode & 0o777 == 0o700
    assert restored_store.path.stat().st_mode & 0o777 == 0o600


def test_restore_never_overwrites_an_existing_destination(backup_state, tmp_path):
    _, store, _ = backup_state
    backup = create_backup(tmp_path / "backups", store=store)
    destination = tmp_path / "existing"
    destination.mkdir()
    sentinel = destination / "keep.txt"
    sentinel.write_text("Keep existing data", encoding="utf-8")
    with pytest.raises(FileExistsError):
        restore_backup(backup, destination)
    assert sentinel.read_text(encoding="utf-8") == "Keep existing data"


def test_backup_rejects_archives_changed_during_the_snapshot(backup_state, tmp_path, monkeypatch):
    data, store, _ = backup_state
    original_backup = store.backup

    def concurrent_archive_change(destination):
        original_backup(destination)
        with (data / "2026_workouts.yml").open("a", encoding="utf-8") as archive:
            archive.write("\n")

    monkeypatch.setattr(store, "backup", concurrent_archive_change)
    with pytest.raises(ValueError, match="changed during backup"):
        create_backup(tmp_path / "backups", store=store)
    assert list((tmp_path / "backups").iterdir()) == []


@pytest.mark.parametrize("name", ["../outside", ".state/../../outside", "metadata/../../outside", "unexpected.txt"])
def test_restore_rejects_unexpected_paths_without_extracting(tmp_path, name):
    backup = tmp_path / "unsafe.zip"
    outside = tmp_path / "outside"
    outside.write_text("Keep existing data", encoding="utf-8")
    with ZipFile(backup, "w") as archive:
        archive.writestr("manifest.json", "{}")
        archive.writestr(name, "must not be extracted")
    with pytest.raises(ValueError, match="unexpected file path"):
        restore_backup(backup, tmp_path / "restored")
    assert outside.read_text(encoding="utf-8") == "Keep existing data"
    assert not (tmp_path / "restored").exists()


def test_restore_rejects_zip_symlinks(tmp_path):
    backup = tmp_path / "unsafe.zip"
    member = ZipInfo("2026_workouts.yml")
    member.external_attr = (stat.S_IFLNK | 0o777) << 16
    with ZipFile(backup, "w") as archive:
        archive.writestr("manifest.json", "{}")
        archive.writestr(member, "../outside")
    with pytest.raises(ValueError, match="symlink"):
        restore_backup(backup, tmp_path / "restored")
    assert not (tmp_path / "restored").exists()


def test_restore_rejects_duplicate_zip_entries(tmp_path):
    backup = tmp_path / "unsafe.zip"
    with ZipFile(backup, "w") as archive:
        archive.writestr("manifest.json", "{}")
        with pytest.warns(UserWarning, match="Duplicate name"):
            archive.writestr("manifest.json", "{}")
    with pytest.raises(ValueError, match="duplicate"):
        restore_backup(backup, tmp_path / "restored")


def test_restore_rejects_checksum_mismatch(backup_state, tmp_path):
    _, store, _ = backup_state
    backup = create_backup(tmp_path / "backups", store=store)
    corrupt = tmp_path / "corrupt.zip"
    with ZipFile(backup) as source, ZipFile(corrupt, "w") as target:
        for member in source.namelist():
            content = source.read(member)
            target.writestr(member, b"X" + content[1:] if member == "2026_workouts.yml" else content)
    with pytest.raises(ValueError, match="checksum"):
        restore_backup(corrupt, tmp_path / "restored")
    assert not (tmp_path / "restored").exists()


def test_restore_rejects_invalid_database_with_valid_payload_checksum(backup_state, tmp_path):
    _, store, _ = backup_state
    backup = create_backup(tmp_path / "backups", store=store)
    corrupt = tmp_path / "corrupt.zip"
    content = b"Not a SQLite database"
    with ZipFile(backup) as source, ZipFile(corrupt, "w") as target:
        manifest = json.loads(source.read("manifest.json"))
        manifest["files"][STATE_MEMBER] = {"size": len(content), "sha256": hashlib.sha256(content).hexdigest()}
        for member in source.namelist():
            if member == STATE_MEMBER:
                target.writestr(member, content)
            elif member == "manifest.json":
                target.writestr(member, json.dumps(manifest))
            else:
                target.writestr(member, source.read(member))
    with pytest.raises(sqlite3.DatabaseError):
        restore_backup(corrupt, tmp_path / "restored")
    assert not (tmp_path / "restored").exists()


def test_restore_enforces_uncompressed_size_limit(backup_state, tmp_path, monkeypatch):
    _, store, _ = backup_state
    backup = create_backup(tmp_path / "backups", store=store)
    monkeypatch.setattr("src.utils.state_backup.MAX_BYTES", 1)
    with pytest.raises(ValueError, match="size limit"):
        restore_backup(backup, tmp_path / "restored")
    assert not (tmp_path / "restored").exists()


def test_restore_rejects_a_dangling_destination_symlink(backup_state, tmp_path):
    _, store, _ = backup_state
    backup = create_backup(tmp_path / "backups", store=store)
    destination = tmp_path / "restored"
    target = tmp_path / "must-not-be-created"
    destination.symlink_to(target, target_is_directory=True)
    with pytest.raises(FileExistsError):
        restore_backup(backup, destination)
    assert destination.is_symlink()
    assert not target.exists()


def test_backup_and_restore_cli_round_trip(backup_state, tmp_path):
    data, store, record = backup_state
    environment = {**os.environ, "FITNESS_TRACKER_DATA_DIR": str(data), "FITNESS_TRACKER_STATE_DIR": str(store.path.parent)}
    result = subprocess.run([sys.executable, "-m", "src.utils.state_backup", "backup", str(tmp_path / "backups")], cwd=PROJECT_ROOT, env=environment, capture_output=True, text=True, check=True)
    assert "fixture-only-password-hash" not in result.stdout + result.stderr
    backup = next((tmp_path / "backups").glob("*.zip"))
    result = subprocess.run([sys.executable, "-m", "src.utils.state_backup", "restore", str(backup), str(tmp_path / "restored")], cwd=PROJECT_ROOT, env=environment, capture_output=True, text=True, check=True)
    assert "Existing sessions were revoked" in result.stdout
    assert "export FITNESS_TRACKER_DATA_DIR=" in result.stdout
    assert "export FITNESS_TRACKER_REAL_WORKOUT_DATABASE=" in result.stdout
    assert "export FITNESS_TRACKER_REAL_WEIGHT_TABLE=" in result.stdout
    assert StateStore(tmp_path / "restored" / STATE_MEMBER).workout(record["id"]) == store.workout(record["id"])


def test_backup_preserves_creation_keys_after_restore(backup_state, tmp_path):
    _, store, _ = backup_state
    payload = {"date": "2026-01-01", "exercises": {}}
    key = store.new_id()
    created = store.create_workout(payload, idempotency_key=key)
    backup = create_backup(tmp_path / "backups", store=store)
    restored = restore_backup(backup, tmp_path / "restored")
    assert StateStore(restored / STATE_MEMBER).create_workout(payload, idempotency_key=key) == created


def test_migration_cli_can_be_repeated_without_losing_state(backup_state):
    data, store, record = backup_state
    environment = {**os.environ, "FITNESS_TRACKER_DATA_DIR": str(data), "FITNESS_TRACKER_STATE_DIR": str(store.path.parent)}
    before = store.workout(record["id"])
    for attempt in range(2):
        result = subprocess.run([sys.executable, "-m", "src.utils.state_backup", "migrate"], cwd=PROJECT_ROOT, env=environment, capture_output=True, text=True, check=True)
        assert "State schema version 2 is ready" in result.stdout
    assert store.workout(record["id"]) == before

