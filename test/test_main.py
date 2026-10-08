from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
import yaml
from fastapi.testclient import TestClient

from src.main import app
from src.utils.config import settings
from src.utils.custom_storage import YAMLStorage
from src.utils.set_db_and_table import TinyDBSingleton


def _record(date: str, split: str, exercise: str) -> dict:
    return {
        "date": date,
        "start_time": "09:00",
        "end_time": "10:00",
        "timezone": "CET",
        "split": split,
        "exercises": {
            exercise: [
                {"set_number": 1, "reps": 8, "weight": "40 kg"},
                {"set_number": 2, "reps": 6, "weight": "45 kg"},
            ]
        },
    }


def _write_database(path: Path, records: list[dict]) -> None:
    payload = {
        "weight_training_log": {
            str(index): record for index, record in enumerate(records, start=1)
        }
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


@pytest.fixture
def api_data(tmp_path: Path) -> Iterator[Path]:
    original_data_dir = settings.DATA_DIR
    original_database = settings.REAL_WORKOUT_DATABASE
    original_api_token = settings.API_TOKEN
    _write_database(
        tmp_path / "2022_workouts.yml",
        [
            _record("2022-02-08", "chest", "bench_press"),
            _record("2022-02-08", "back", "row"),
        ],
    )
    _write_database(
        tmp_path / "2024_workouts.yml",
        [
            _record("2024-03-11", "legs", "squat"),
            _record("2024-01-07", "push", "incline_press"),
        ],
    )
    settings.set("DATA_DIR", str(tmp_path))
    settings.set("REAL_WORKOUT_DATABASE", str(tmp_path / "<YEAR>_workouts.yml"))
    settings.set("API_TOKEN", "")
    TinyDBSingleton.close_all()
    yield tmp_path
    TinyDBSingleton.close_all()
    settings.set("DATA_DIR", original_data_dir)
    settings.set("REAL_WORKOUT_DATABASE", original_database)
    settings.set("API_TOKEN", original_api_token)


def test_years_and_latest_year_default(api_data: Path) -> None:
    with TestClient(app) as client:
        assert client.get("/years").json() == [2022, 2024]

        response = client.get("/workouts")

    assert response.status_code == 200
    assert response.json()["year"] == 2024
    assert response.json()["total"] == 2


def test_workout_pagination_and_global_order(api_data: Path) -> None:
    with TestClient(app) as client:
        newest = client.get("/workouts?year=2024&limit=1&offset=0&order=desc")
        oldest = client.get("/workouts?year=2024&limit=1&offset=0&order=asc")

    assert newest.json()["items"][0]["date"] == "2024-03-11"
    assert oldest.json()["items"][0]["date"] == "2024-01-07"
    assert newest.headers["cache-control"] == "private, max-age=60"


def test_duplicate_day_workouts_remain_distinct(api_data: Path) -> None:
    with TestClient(app) as client:
        response = client.get("/dates_and_splits?year=2022")

    items = response.json()
    assert response.status_code == 200
    assert len(items) == 2
    assert len({item["id"] for item in items}) == 2
    assert {item["split"] for item in items} == {"chest", "back"}


def test_stable_workout_id_loads_detail(api_data: Path) -> None:
    with TestClient(app) as client:
        workout_id = client.get("/workouts?year=2024").json()["items"][0]["id"]
        response = client.get(f"/workouts/{workout_id}")

    assert response.status_code == 200
    assert response.json()["split"] == "legs"
    assert response.json()["exercises"]["squat"][0]["weight"] == "40 kg"


def test_api_uses_persisted_id_after_document_renumbering(api_data: Path) -> None:
    workout_id = str(uuid4())
    record = {**_record("2024-03-11", "legs", "squat"), "id": workout_id}
    database_path = api_data / "2024_workouts.yml"
    _write_database(database_path, [record])

    with TestClient(app) as client:
        assert client.get("/workouts?year=2024").json()["items"][0]["id"] == workout_id
        database_path.write_text(
            yaml.safe_dump({"weight_training_log": {"99": record}}), encoding="utf-8"
        )
        response = client.get(f"/workouts/{workout_id}")

    assert response.status_code == 200
    assert response.json()["id"] == workout_id


def test_missing_year_is_non_mutating(api_data: Path) -> None:
    missing_database = api_data / "2026_workouts.yml"

    with TestClient(app) as client:
        response = client.get("/workouts?year=2026")

    assert response.status_code == 404
    assert not missing_database.exists()


def test_invalid_legacy_record_does_not_break_valid_workouts(api_data: Path) -> None:
    _write_database(
        api_data / "2024_workouts.yml",
        [
            _record("2024-02-30", "legs", "squat"),
            _record("2024-03-11", "legs", "squat"),
        ],
    )

    with TestClient(app) as client:
        response = client.get("/workouts?year=2024")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["date"] == "2024-03-11"


def test_query_validation_and_readiness(api_data: Path) -> None:
    with TestClient(app) as client:
        invalid_year = client.get("/workouts?year=1800")
        invalid_limit = client.get("/workouts?limit=101")
        readiness = client.get("/readyz")

    assert invalid_year.status_code == 422
    assert invalid_limit.status_code == 422
    assert readiness.status_code == 200


def test_empty_archive_is_ready_for_first_workout(api_data: Path) -> None:
    for path in api_data.glob("*_workouts.yml"):
        path.unlink()
    before = set(api_data.iterdir())
    with TestClient(app) as client:
        assert client.get("/readyz").status_code == 200
        assert client.get("/years").json() == []
        assert client.get("/analytics/overview").json()["workouts"] == 0
    assert set(api_data.iterdir()) == before


def test_repeated_reads_reuse_parsed_files(
    api_data: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    parsed_files: list[str] = []
    original_read = YAMLStorage.read

    def track_read(storage: YAMLStorage):
        parsed_files.append(storage.filename.name)
        return original_read(storage)

    monkeypatch.setattr(YAMLStorage, "read", track_read)
    with TestClient(app) as client:
        workout_id = client.get("/workouts?year=2022").json()["items"][0]["id"]
        assert client.get(f"/workouts/{workout_id}").status_code == 200
        assert parsed_files == ["2022_workouts.yml"]
        assert client.get("/workouts?year=2024").status_code == 200
        assert sorted(parsed_files) == ["2022_workouts.yml", "2024_workouts.yml"]
        parsed_files.clear()

        assert client.get(f"/workouts/{workout_id}").status_code == 200
        assert client.get("/workouts?year=2024").status_code == 200
        assert client.get("/dates?year=2022").status_code == 200
        assert client.get("/readyz").status_code == 200
        assert parsed_files == []

        replacement = api_data / "replacement.yml"
        _write_database(replacement, [_record("2024-04-01", "pull", "row")])
        replacement.replace(api_data / "2024_workouts.yml")
        response = client.get("/workouts?year=2024")
        assert response.json()["items"][0]["date"] == "2024-04-01"
        assert parsed_files == ["2024_workouts.yml"]


def test_indexed_detail_does_not_parse_an_unrelated_invalid_file(api_data: Path) -> None:
    with TestClient(app) as client:
        workout_id = client.get("/workouts?year=2024").json()["items"][0]["id"]
        (api_data / "2022_workouts.yml").write_text("workouts: [invalid", encoding="utf-8")

        response = client.get(f"/workouts/{workout_id}")

    assert response.status_code == 200
    assert response.json()["id"] == workout_id


def test_deleted_year_is_removed_from_workout_index(api_data: Path) -> None:
    with TestClient(app) as client:
        workout_id = client.get("/workouts?year=2022").json()["items"][0]["id"]
        assert client.get(f"/workouts/{workout_id}").status_code == 200
        (api_data / "2022_workouts.yml").unlink()

        assert client.get(f"/workouts/{workout_id}").status_code == 404
        assert client.get("/years").json() == [2024]
        assert not (api_data / "2022_workouts.yml").exists()


def test_index_tracks_workout_moved_between_files(api_data: Path) -> None:
    workout_id = str(uuid4())
    original = {**_record("2022-02-08", "back", "row"), "id": workout_id}
    _write_database(api_data / "2022_workouts.yml", [original])
    with TestClient(app) as client:
        assert client.get(f"/workouts/{workout_id}").json()["year"] == 2022
        _write_database(api_data / "2022_workouts.yml", [])
        _write_database(
            api_data / "2024_workouts.yml", [{**original, "date": "2024-02-08"}]
        )
        response = client.get(f"/workouts/{workout_id}")

    assert response.status_code == 200
    assert response.json()["year"] == 2024


@pytest.mark.parametrize(
    "invalid_token",
    [None, "wrong-token", b"\xff"],
    ids=["missing", "incorrect", "non-ascii"],
)
def test_configured_api_token_is_required(
    api_data: Path, invalid_token: str | bytes | None
) -> None:
    settings.set("API_TOKEN", "test-token")
    headers = {} if invalid_token is None else {"X-API-Key": invalid_token}

    with TestClient(app) as client:
        unauthorized = client.get("/years", headers=headers)
        authorized = client.get("/years", headers={"X-API-Key": "test-token"})
        health = client.get("/healthz")

    assert unauthorized.status_code == 401
    assert unauthorized.headers["www-authenticate"] == "ApiKey"
    assert authorized.status_code == 200
    assert health.status_code == 200


def test_openapi_metadata_has_single_identity(api_data: Path) -> None:
    with TestClient(app) as client:
        json_schema = client.get("/openapi.json").json()
        yaml_schema = yaml.safe_load(client.get("/openapi.yaml").text)

    assert json_schema["info"] == yaml_schema["info"]
    assert json_schema["info"]["title"] == "Fitness Tracker API"
    assert json_schema["info"]["version"] == "0.1.0"
    assert json_schema["components"]["securitySchemes"]["APIKeyHeader"] == {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
    }


def test_analytics_are_complete_and_not_tied_to_pagination(api_data: Path) -> None:
    with TestClient(app) as client:
        response = client.get("/analytics/overview?from=2022-01-01&to=2024-12-31&bucket=month")
        assert response.status_code == 200
        body = response.json()
        assert body["workouts"] == 4
        assert body["active_days"] == 3
        assert body["sets"] == 8
        assert body["volume_kg_reps"] == 2360
        assert len(body["buckets"]) == 36
        assert len(body["buckets"][1]["workout_ids"]) == 2
        assert body["excluded_load_sets"] == 0
        assert client.get("/workouts?year=2022&limit=1").json()["total"] == 2


def test_exercise_history_records_and_export(api_data: Path) -> None:
    with TestClient(app) as client:
        exercises = client.get("/exercises").json()
        assert "bench_press" in {exercise["id"] for exercise in exercises}
        history = client.get("/analytics/exercises/bb_bench_press?formula=epley").json()
        assert history["exercise_id"] == "bench_press"
        assert len(history["sessions"]) == 1
        assert history["sessions"][0]["volume_kg_reps"] == 590
        records = client.get("/analytics/records?exercise_id=bench_press").json()
        assert {record["metric"] for record in records} == {"load", "reps", "estimated_one_rm"}
        exported = client.get("/analytics/export?exercise_id=bench_press")
        assert exported.status_code == 200
        assert "590.0" in exported.text
        assert "text/csv" in exported.headers["content-type"]


def test_analytics_validate_ranges_and_preserve_empty_results(api_data: Path) -> None:
    with TestClient(app) as client:
        assert client.get("/analytics/overview?from=2024-02-01&to=2024-01-01").status_code == 422
        assert client.get("/analytics/overview?bucket=invalid").status_code == 422
        assert client.get("/analytics/exercises/squat?formula=invalid").status_code == 422
        empty = client.get("/analytics/overview?from=2026-01-01&to=2026-01-14").json()
        assert empty["workouts"] == 0
        assert empty["volume_kg_reps"] is None
        assert all(bucket["workouts"] == 0 for bucket in empty["buckets"])


@pytest.fixture
def signed_in(api_data: Path):
    from src.utils.access_control import hash_password
    from src.utils.state_store import state_store

    original = {key: settings.get(key) for key in ("STATE_DIR", "ENABLE_WRITES")}
    settings.set("STATE_DIR", str(api_data / "state"))
    settings.set("ENABLE_WRITES", True)
    state_store.configure("password_hash", hash_password("test-only-password"))
    with TestClient(app) as client:
        response = client.post("/auth/login", json={"password": "test-only-password"}, headers={"Origin": "http://testserver"})
        assert response.status_code == 200
        headers = {"Origin": "http://testserver", "X-CSRF-Token": response.json()["csrf_token"]}
        yield client, headers
    for key, value in original.items():
        settings.set(key, value)


def test_writes_require_session_origin_and_csrf(signed_in):
    client, headers = signed_in
    payload = _record("2026-01-01", "legs", "squat")
    assert client.post("/workouts", json=payload).status_code == 403
    assert client.post("/workouts", json=payload, headers={**headers, "Origin": "https://wrong.example"}).status_code == 403
    assert client.post("/workouts", json=payload, headers=headers).status_code == 201


def test_transactional_workout_edit_move_and_delete(signed_in):
    client, headers = signed_in
    original = client.get("/workouts?year=2022").json()["items"][0]
    payload = _record("2027-01-01", "legs", "squat")
    assert client.put(f"/workouts/{original['id']}", json=payload, headers=headers).status_code == 428
    updated = client.put(f"/workouts/{original['id']}", json=payload, headers={**headers, "If-Match": "1"})
    assert updated.status_code == 200
    assert updated.json()["id"] == original["id"]
    assert updated.json()["version"] == 2
    assert 2027 in client.get("/years").json()
    assert client.get("/workouts?year=2022").json()["total"] == 1
    assert client.put(f"/workouts/{original['id']}", json=payload, headers={**headers, "If-Match": "1"}).status_code == 409
    assert client.delete(f"/workouts/{original['id']}", headers={**headers, "If-Match": "2"}).status_code == 204
    assert client.get(f"/workouts/{original['id']}").status_code == 404


def test_measurement_import_is_atomic_and_uses_historical_mass(signed_in):
    client, headers = signed_in
    bad = "date,weight_kg\n2026-01-01,80\n2026-02-30,81\n"
    assert client.post("/body-metrics/import", content=bad, headers=headers).status_code == 422
    assert client.get("/body-metrics").json() == []
    good = "date,weight_kg\n2026-01-01,80\n2026-02-01,81\n"
    assert client.post("/body-metrics/import", content=good, headers=headers).json()["imported"] == 2
    workout = client.post("/workouts", json=_record("2026-01-05", "pull", "pullup"), headers=headers).json()
    payload = _record("2026-01-05", "pull", "pullup")
    payload["exercises"]["pullup"] = [{"set_number": 1, "reps": 5, "weight": "BODYWEIGHT - 20 kg"}]
    client.put(f"/workouts/{workout['id']}", json=payload, headers={**headers, "If-Match": "1"})
    session = client.get("/analytics/exercises/pullup?from=2026-01-01&to=2026-01-10").json()["sessions"][0]
    assert session["bodyweight_kg"] == 80
    assert session["volume_kg_reps"] == 300
    assert session["estimated_one_rm_kg"] is None


def test_measurement_csv_preserves_columns_not_in_the_file(signed_in):
    client, headers = signed_in
    assert client.post("/body-metrics", json={"date": "2026-01-01", "weight_kg": 80, "waist_cm": 85}, headers=headers).status_code == 200
    assert client.post("/body-metrics/import", content="date,weight_kg\n2026-01-01,81\n", headers=headers).status_code == 200
    assert client.get("/body-metrics").json()[0]["waist_cm"] == 85
    assert client.get("/body-metrics").json()[0]["weight_kg"] == 81


def test_program_targets_and_workout_import(signed_in):
    client, headers = signed_in
    payload = {"planned_workouts": 20, "targets": [{"id": "full_body_a", "targets": [{"exercise_id": "squat", "sets": 3, "reps_min": 4, "reps_max": 6}]}]}
    assert client.put("/programs/program_14/targets", json=payload, headers=headers).status_code == 200
    content = [_record("2026-01-01", "legs", "squat"), _record("2026-01-02", "legs", "squat")]
    assert client.post("/workouts/import", json=content, headers=headers).json()["imported"] == 2
    assert client.get("/workouts?year=2026").json()["total"] == 2


def test_password_change_revokes_existing_browser_session(signed_in):
    from src.utils.access_control import hash_password
    from src.utils.state_store import state_store

    client, _ = signed_in
    assert client.get("/years").status_code == 200
    state_store.configure("password_hash", hash_password("different-test-password"))
    assert client.get("/years").status_code == 401
    assert client.get("/healthz").status_code == 200


def test_import_keeps_metadata_and_rejects_deleted_id_reuse(signed_in):
    from src.utils.state_store import state_store

    client, headers = signed_in
    record = {**_record("2026-01-01", "legs", "squat"), "warmup": "Mobility"}
    assert client.post("/workouts/import", json=record, headers=headers).status_code == 200
    workout = client.get("/workouts?year=2026").json()["items"][0]
    updated = client.put(f"/workouts/{workout['id']}", json=_record("2026-01-02", "legs", "squat"), headers={**headers, "If-Match": "1"})
    assert updated.status_code == 200
    assert state_store.workout(workout["id"])["record"]["warmup"] == "Mobility"
    assert client.delete(f"/workouts/{workout['id']}", headers={**headers, "If-Match": "2"}).status_code == 204
    assert client.post("/workouts/import", json={**record, "id": workout["id"]}, headers=headers).status_code == 409