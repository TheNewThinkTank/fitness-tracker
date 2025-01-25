
import json
from pathlib import Path
import yaml
import pytest
from unittest.mock import MagicMock, mock_open, patch
from tinydb import table
from src.crud.insert import (  # type: ignore
    insert_log,
    insert_all_logs,
    insert_specific_log
    )


def test_insert_log_json():
    mock_table = MagicMock(spec=table.Table)
    mock_content = {"key": "value"}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_content))):
        insert_log(mock_table, "dummy_path.json", "json")

    mock_table.insert.assert_called_once_with(mock_content)


def test_insert_log_yml():
    mock_table = MagicMock(spec=table.Table)
    mock_content = {"key": "value"}

    with patch("builtins.open", mock_open(read_data=yaml.dump(mock_content))):
        insert_log(mock_table, "dummy_path.yml", "yml")

    mock_table.insert.assert_called_once_with(mock_content)


def test_insert_log_list():
    mock_table = MagicMock(spec=table.Table)
    mock_content = {"key": "value"}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_content))):
        insert_log(mock_table, ["dummy_path.json"], "json")

    mock_table.insert.assert_called_once_with(mock_content)


def test_insert_log_with_path_object():
    mock_table = MagicMock(spec=table.Table)
    mock_content = {"key": "value"}
    log_path = Path("dummy_path.json")
    file_format = "json"

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_content))):
        insert_log(mock_table, log_path, file_format)

    mock_table.insert.assert_called_once_with(mock_content)


def test_insert_log_invalid_format():
    mock_table = MagicMock(spec=table.Table)

    with pytest.raises(
        ValueError, match="Invalid file format: txt. Expected 'json' or 'yml'."
        ):
        insert_log(mock_table, "dummy_path.txt", "txt")


def test_insert_all_logs():
    mock_table = MagicMock(spec=table.Table)
    mock_content = {"key": "value"}
    folderpath = "dummy_folder"
    file_format = "json"

    # Create a temporary directory with dummy files
    with patch("os.listdir", return_value=["file1.json", "file2.json"]):
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_content))):
            insert_all_logs(mock_table, folderpath, file_format)

    assert mock_table.insert.call_count == 2


def test_insert_all_logs_empty_folder():
    mock_table = MagicMock(spec=table.Table)
    folderpath = "dummy_folder"
    file_format = "json"

    with patch("os.listdir", return_value=[]):
        insert_all_logs(mock_table, folderpath, file_format)

    mock_table.insert.assert_not_called()


def test_insert_all_logs_invalid_format():
    mock_table = MagicMock(spec=table.Table)
    folderpath = "dummy_folder"
    file_format = "txt"

    with patch("os.listdir", return_value=["file1.txt"]):
        with pytest.raises(
            ValueError, match="Invalid file format: txt. Expected 'json' or 'yml'."
            ):
            insert_all_logs(mock_table, folderpath, file_format)


def test_insert_specific_log():
    mock_table = MagicMock(spec=table.Table)
    mock_content = {"key": "value"}
    date = "2023-10-01"
    file_format = "json"
    workout_number = 1
    
    # Mocking the ConfigLoader and get_year_and_month
    with patch("src.utils.config_loader.ConfigLoader.load_env_variables", return_value={"athlete": "test_athlete"}):
        with patch("src.utils.config_loader.ConfigLoader.load_config", return_value={"google_drive_data_path": "/dummy_path"}):
            with patch("datetime_tools.lookup.get_year_and_month", return_value=("2023", "10")):
                with patch("glob.glob", return_value=["/dummy_path/test_athlete/log_archive/JSON/2023/10/training_log_2023-10-01.json"]):
                    with patch("builtins.open", mock_open(read_data=json.dumps(mock_content))):
                        insert_specific_log(date, mock_table, file_format, workout_number)
    
    mock_table.insert.assert_called_once_with(mock_content)


def test_insert_specific_log_multiple_workouts():
    mock_table = MagicMock(spec=table.Table)
    mock_content = {"key": "value"}
    date = "2023-10-01"
    file_format = "json"
    workout_number = 2
    
    with patch("src.utils.config_loader.ConfigLoader.load_env_variables", return_value={"athlete": "test_athlete"}):
        with patch("src.utils.config_loader.ConfigLoader.load_config", return_value={"google_drive_data_path": "/dummy_path"}):
            with patch("datetime_tools.lookup.get_year_and_month", return_value=("2023", "10")):
                with patch("glob.glob", return_value=["/dummy_path/test_athlete/log_archive/JSON/2023/10/training_log_2023-10-01_2.json"]):
                    with patch("builtins.open", mock_open(read_data=json.dumps(mock_content))):
                        insert_specific_log(date, mock_table, file_format, workout_number)
    
    mock_table.insert.assert_called_once_with(mock_content)
