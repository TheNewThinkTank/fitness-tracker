from datetime import date
import json
import os
import shutil
import subprocess
import sys

import pytest

from src.common.measurements import BodyMeasurement
from src.utils.config import PROJECT_ROOT, settings
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