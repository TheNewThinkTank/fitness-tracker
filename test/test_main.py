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