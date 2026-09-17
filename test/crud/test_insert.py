import json
from datetime import date as calendar_date
from pathlib import Path
from uuid import UUID

import pytest
import yaml
from tinydb import table
from unittest.mock import MagicMock, call

import src.crud.insert as insert_module
from src.crud.insert import (  # type: ignore
    WorkoutDate,
    insert_all_logs,
    insert_log,
    insert_specific_log,
)
from src.utils.config import settings
from src.utils.set_db_and_table import TinyDBSingleton


def _workout_record(date: str = "2024-01-07") -> dict:
    return {
        "date": date,
        "split": "push",
        "exercises": {
            "bench_press": [
                {"set_number": 1, "reps": 8, "weight": "40 kg"},
            ]
        },
    }


def test_insert_log_json(tmp_path: Path) -> None:
    mock_table = MagicMock(spec=table.Table)
    content = _workout_record()
    log_path = tmp_path / "workout.json"
    log_path.write_text(json.dumps(content), encoding="utf-8")

    insert_log(mock_table, log_path, "json")

    mock_table.insert.assert_called_once_with(content)


def test_insert_log_yml(tmp_path: Path) -> None:
    mock_table = MagicMock(spec=table.Table)
    content = _workout_record()
    log_path = tmp_path / "workout.yml"
    log_path.write_text(yaml.safe_dump(content), encoding="utf-8")

    insert_log(mock_table, log_path, "yml")

    mock_table.insert.assert_called_once_with(content)


def test_insert_log_list(tmp_path: Path) -> None:
    mock_table = MagicMock(spec=table.Table)
    content = _workout_record()
    log_path = tmp_path / "workout.json"
    log_path.write_text(json.dumps(content), encoding="utf-8")

    insert_log(mock_table, [log_path], "json")

    mock_table.insert.assert_called_once_with(content)


def test_insert_log_invalid_format() -> None:
    mock_table = MagicMock(spec=table.Table)

    with pytest.raises(
        ValueError,
        match="Invalid file format: txt. Expected 'json' or 'yml'.",
    ):
        insert_log(mock_table, "workout.txt", "txt")


@pytest.mark.parametrize("content", [{"key": "value"}, {"date": "2024-02-30"}])
def test_insert_log_rejects_invalid_record(tmp_path: Path, content: dict) -> None:
    mock_table = MagicMock(spec=table.Table)
    log_path = tmp_path / "workout.yml"
    log_path.write_text(yaml.safe_dump(content), encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid workout record"):
        insert_log(mock_table, log_path, "yml")

    mock_table.insert.assert_not_called()


def test_insert_all_logs_filters_by_format(tmp_path: Path) -> None:
    mock_table = MagicMock(spec=table.Table)
    first_record = _workout_record("2024-01-07")
    second_record = _workout_record("2024-01-10")
    (tmp_path / "first.json").write_text(json.dumps(first_record), encoding="utf-8")
    (tmp_path / "second.json").write_text(json.dumps(second_record), encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignore me", encoding="utf-8")

    insert_all_logs(mock_table, str(tmp_path), "json")

    assert mock_table.insert.call_count == 2
    mock_table.insert.assert_any_call(first_record)
    mock_table.insert.assert_any_call(second_record)


def test_insert_all_logs_empty_folder(tmp_path: Path) -> None:
    mock_table = MagicMock(spec=table.Table)

    insert_all_logs(mock_table, str(tmp_path), "json")

    mock_table.insert.assert_not_called()


def test_insert_all_logs_invalid_format(tmp_path: Path) -> None:
    mock_table = MagicMock(spec=table.Table)

    with pytest.raises(
        ValueError,
        match="Invalid file format: txt. Expected 'json' or 'yml'.",
    ):
        insert_all_logs(mock_table, str(tmp_path), "txt")


def test_insert_specific_log_uses_confined_archive_path(tmp_path: Path) -> None:
    mock_table = MagicMock(spec=table.Table)
    archive = tmp_path / "log_archive" / "YML" / "2024" / "January"
    archive.mkdir(parents=True)
    content = _workout_record()
    log_path = archive / "training_log_2024-01-07.yml"
    log_path.write_text(yaml.safe_dump(content), encoding="utf-8")
    original_data_dir = settings.DATA_DIR
    settings.set("DATA_DIR", str(tmp_path))

    try:
        insert_specific_log(WorkoutDate("2024-01-07"), mock_table)
    finally:
        settings.set("DATA_DIR", original_data_dir)

    mock_table.insert.assert_called_once_with(content)


@pytest.mark.parametrize(
    "unsafe_date",
    ["2024-01-*", "../../2024-01-07", "2024-13-01"],
)
def test_insert_specific_log_rejects_unsafe_dates(unsafe_date: str) -> None:
    mock_table = MagicMock(spec=table.Table)

    with pytest.raises(ValueError, match="date must use YYYY-MM-DD format"):
        insert_specific_log(WorkoutDate(unsafe_date), mock_table)


def test_insert_specific_log_rejects_nonpositive_workout_number() -> None:
    mock_table = MagicMock(spec=table.Table)

    with pytest.raises(ValueError, match="workout_number must be at least 1"):
        insert_specific_log(
            WorkoutDate("2024-01-07"),
            mock_table,
            workout_number=0,
        )


def test_cli_routes_each_date_to_its_year(monkeypatch: pytest.MonkeyPatch) -> None:
    first_table = MagicMock(spec=table.Table)
    second_table = MagicMock(spec=table.Table)
    select_database = MagicMock(
        side_effect=[
            (MagicMock(), first_table, "catalogue"),
            (MagicMock(), second_table, "catalogue"),
        ]
    )
    insert_workout = MagicMock()
    monkeypatch.setattr(
        "sys.argv",
        ["insert", "--datatype", "real", "--dates", "2022-02-08,2024-01-07"],
    )
    monkeypatch.setattr("src.utils.logger_config.setup_logger", MagicMock())
    monkeypatch.setattr("src.utils.logger_config.log_running_file", MagicMock())
    monkeypatch.setattr(insert_module, "set_db_and_table", select_database)
    monkeypatch.setattr(insert_module, "insert_specific_log", insert_workout)

    insert_module.main()

    assert select_database.call_args_list == [
        call("real", year=2022),
        call("real", year=2024),
    ]
    assert insert_workout.call_args_list == [
        call(WorkoutDate("2022-02-08"), first_table, "yml"),
        call(WorkoutDate("2024-01-07"), second_table, "yml"),
    ]


def test_cli_imports_historical_archives_with_permanent_ids(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dates = ["2022-02-08", "2024-01-07"]
    for date in dates:
        parsed_date = calendar_date.fromisoformat(date)
        archive = (
            tmp_path / "log_archive" / "YML"
            / str(parsed_date.year) / parsed_date.strftime("%B")
        )
        archive.mkdir(parents=True)
        (archive / f"training_log_{date}.yml").write_text(
            yaml.safe_dump(_workout_record(date)), encoding="utf-8"
        )
    original_data_dir = settings.DATA_DIR
    original_database = settings.REAL_WORKOUT_DATABASE
    settings.set("DATA_DIR", str(tmp_path))
    settings.set("REAL_WORKOUT_DATABASE", str(tmp_path / "<YEAR>_workouts.yml"))
    monkeypatch.setattr("sys.argv", ["insert", "--dates", ",".join(dates)])
    monkeypatch.setattr("src.utils.logger_config.setup_logger", MagicMock())
    monkeypatch.setattr("src.utils.logger_config.log_running_file", MagicMock())

    try:
        insert_module.main()
        for date in dates:
            database = yaml.safe_load((tmp_path / f"{date[:4]}_workouts.yml").read_text())
            records = list(database[settings.REAL_WEIGHT_TABLE].values())
            assert len(records) == 1
            assert records[0]["date"] == date
            assert UUID(records[0]["id"]).version == 4
        assert sorted(path.name for path in tmp_path.glob("*_workouts.yml")) == [
            "2022_workouts.yml", "2024_workouts.yml"
        ]
    finally:
        TinyDBSingleton.close_all()
        settings.set("DATA_DIR", original_data_dir)
        settings.set("REAL_WORKOUT_DATABASE", original_database)


def test_insert_rejects_record_from_the_wrong_date(tmp_path: Path) -> None:
    mock_table = MagicMock(spec=table.Table)
    log_path = tmp_path / "training_log_2024-01-07.yml"
    log_path.write_text(yaml.safe_dump(_workout_record("2022-02-08")), encoding="utf-8")

    with pytest.raises(ValueError, match="does not match 2024-01-07"):
        insert_log(mock_table, log_path, "yml", expected_date="2024-01-07")

    mock_table.insert.assert_not_called()