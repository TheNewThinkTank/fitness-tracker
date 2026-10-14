import os
import json
from pathlib import Path
import subprocess
import sys
from datetime import date
from uuid import UUID, uuid4

import click
from click.testing import CliRunner
import pytest
import yaml

from oxygen import cli as oxygen_cli
from src.common.workout_types import legacy_workout_id
from src.utils.config import PROJECT_ROOT, settings
from src.utils.set_db_and_table import TinyDBSingleton
from src.utils.state_store import state_store


@pytest.fixture
def cli_data(tmp_path):
    data = tmp_path / "workout data"
    data.mkdir()
    original = settings.get("STATE_DIR")
    settings.set("STATE_DIR", str(tmp_path / "state"))
    try:
        yield data
    finally:
        TinyDBSingleton.close_all()
        settings.set("STATE_DIR", original)


def _log(data: Path, performed: str, *, number: int | None = None, file_format: str = "yml", notes: str = "Fixture workout") -> Path:
    parsed = date.fromisoformat(performed)
    directory = data / "log_archive" / file_format.upper() / str(parsed.year) / parsed.strftime("%B")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"athlete_training_log_{performed}{'_' + str(number) if number is not None else ''}.{file_format}"
    record = {"date": performed, "split": "push", "start_time": "09:00", "end_time": "10:00", "notes": notes, "exercises": {"bb_bench_press": [{"set_number": 1, "reps": 5, "weight": "60 kg"}]}}
    if file_format == "json":
        path.write_text(json.dumps(record), encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(record), encoding="utf-8")
    return path


def _invoke(data: Path, *arguments: str):
    return CliRunner().invoke(oxygen_cli.cli, ["--data-dir", str(data), *arguments])


def _records(data: Path, year: int) -> list[dict]:
    return list(yaml.safe_load((data / f"{year}_workouts.yml").read_text(encoding="utf-8"))["weight_training_log"].values())


def test_insert_selects_the_requested_workout_year(cli_data):
    source = _log(cli_data, "2024-03-11")
    before = source.read_bytes()
    result = _invoke(cli_data, "insert", "--workout-date", "2024-03-11")
    assert result.exit_code == 0, result.output
    assert "1 imported, 0 skipped" in result.output
    assert _records(cli_data, 2024)[0]["date"] == "2024-03-11"
    assert UUID(_records(cli_data, 2024)[0]["id"]).version == 5
    assert not (cli_data / "2026_workouts.yml").exists()
    assert source.read_bytes() == before


def test_multiple_dates_and_numbered_workouts_are_routed_and_ordered(cli_data):
    _log(cli_data, "2023-12-31")
    _log(cli_data, "2024-01-01", notes="First")
    _log(cli_data, "2024-01-01", number=10, notes="Tenth")
    _log(cli_data, "2024-01-01", number=2, notes="Second")
    result = _invoke(cli_data, "insert", "-d", "2023-12-31,2024-01-01", "-d", "2024-01-01")
    assert result.exit_code == 0, result.output
    assert "4 imported, 0 skipped" in result.output
    assert len(_records(cli_data, 2023)) == 1
    assert [record["notes"] for record in _records(cli_data, 2024)] == ["First", "Second", "Tenth"]
    assert len({record["id"] for record in _records(cli_data, 2024)}) == 3


def test_repeated_import_skips_unchanged_files_and_rejects_changes(cli_data):
    path = _log(cli_data, "2024-03-11")
    assert _invoke(cli_data, "insert", "-d", "2024-03-11").exit_code == 0
    before = (cli_data / "2024_workouts.yml").read_bytes()
    result = _invoke(cli_data, "insert", "-d", "2024-03-11")
    assert result.exit_code == 0, result.output
    assert "0 imported, 1 skipped" in result.output
    assert (cli_data / "2024_workouts.yml").read_bytes() == before
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    record["notes"] = "Changed after import"
    path.write_text(yaml.safe_dump(record), encoding="utf-8")
    result = _invoke(cli_data, "insert", "-d", "2024-03-11")
    assert result.exit_code == 1
    assert "conflicts with existing data" in result.output
    assert (cli_data / "2024_workouts.yml").read_bytes() == before


def test_legacy_identity_can_be_reimported_without_mutating_its_archive(cli_data):
    path = _log(cli_data, "2024-03-11")
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    archive = cli_data / "2024_workouts.yml"
    archive.write_text(yaml.safe_dump({"weight_training_log": {"1": record}}), encoding="utf-8")
    before = archive.read_bytes()
    path.write_text(yaml.safe_dump({**record, "id": str(legacy_workout_id(2024, 1))}), encoding="utf-8")
    result = _invoke(cli_data, "insert", "-d", "2024-03-11")
    assert result.exit_code == 0, result.output
    assert "0 imported, 1 skipped" in result.output
    assert archive.read_bytes() == before


@pytest.mark.parametrize("exercise", ["../outside", "bad\\name", "bad:name"])
def test_unsafe_exercise_filenames_are_rejected_before_import(cli_data, exercise):
    path = _log(cli_data, "2024-03-11")
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    record["exercises"] = {exercise: record["exercises"]["bb_bench_press"]}
    path.write_text(yaml.safe_dump(record), encoding="utf-8")
    result = _invoke(cli_data, "insert", "-d", "2024-03-11")
    assert result.exit_code == 1
    assert "Unsafe exercise name" in result.output
    assert not (cli_data / "2024_workouts.yml").exists()


def test_dry_run_validates_without_creating_archives_or_figures(cli_data):
    _log(cli_data, "2024-03-11")
    result = _invoke(cli_data, "run", "-d", "2024-03-11", "--dry-run")
    assert result.exit_code == 0, result.output
    assert "Dry run: 1 to import, 0 skipped" in result.output
    assert "Would prepare figures: March 2024" in result.output
    assert not (cli_data / "2024_workouts.yml").exists()
    assert not (cli_data / "img").exists()


def test_invalid_batch_fails_before_any_archive_is_written(cli_data):
    _log(cli_data, "2023-12-31")
    broken = _log(cli_data, "2024-01-01")
    broken.write_text("date: 2024-02-30\n", encoding="utf-8")
    result = _invoke(cli_data, "insert", "-d", "2023-12-31,2024-01-01")
    assert result.exit_code == 1
    assert "Cannot import" in result.output
    assert str(broken) in result.output
    assert not (cli_data / "2023_workouts.yml").exists()
    assert not (cli_data / "2024_workouts.yml").exists()


def test_json_selection_and_supplied_metadata_are_preserved(cli_data):
    _log(cli_data, "2024-03-11", file_format="json")
    selected = _log(cli_data, "2024-03-11", number=2, file_format="json")
    identifier = str(uuid4())
    record = json.loads(selected.read_text(encoding="utf-8"))
    record.update(id=identifier, gym="Fixture gym", warmup="Mobility", bodyweight_kg=80, rpe=8, rir=2)
    selected.write_text(json.dumps(record), encoding="utf-8")
    result = _invoke(cli_data, "insert", "-d", "2024-03-11", "-f", "JSON", "-w", "2")
    assert result.exit_code == 0, result.output
    assert _records(cli_data, 2024) == [record]


@pytest.mark.parametrize("value", ["2024-02-30", "20240311", "2024-3-11", "1899-12-31", "2101-01-01", "2024-03-11,"])
def test_invalid_dates_fail_without_writes(cli_data, value):
    result = _invoke(cli_data, "insert", "-d", value)
    assert result.exit_code == 2
    assert "Invalid value" in result.output
    assert list(cli_data.iterdir()) == []


def test_missing_logs_and_unsupported_format_are_not_success(cli_data):
    assert _invoke(cli_data, "insert", "-d", "2024-03-11").exit_code == 1
    assert _invoke(cli_data, "insert", "-d", "2024-03-11", "-f", "csv").exit_code == 2
    assert list(cli_data.iterdir()) == []


def test_default_date_is_computed_for_each_invocation(cli_data, monkeypatch):
    class Clock(date):
        current = date(2024, 3, 11)

        @classmethod
        def today(cls):
            return cls.current

    _log(cli_data, "2024-03-11")
    _log(cli_data, "2025-01-01")
    monkeypatch.setattr(oxygen_cli, "date", Clock)
    assert _invoke(cli_data, "insert").exit_code == 0
    Clock.current = date(2025, 1, 1)
    assert _invoke(cli_data, "insert").exit_code == 0
    assert _records(cli_data, 2024)[0]["date"] == "2024-03-11"
    assert _records(cli_data, 2025)[0]["date"] == "2025-01-01"


def test_help_alias_does_not_require_a_workout_directory(tmp_path):
    result = _invoke(tmp_path / "does-not-exist", "show_help")
    assert result.exit_code == 0, result.output
    assert "prepare-figures" in result.output
    assert not (tmp_path / "does-not-exist").exists()


def test_installed_module_entrypoint_works_outside_the_checkout(tmp_path):
    environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    result = subprocess.run([sys.executable, "-I", "-m", "oxygen", "--help"], cwd=tmp_path, env=environment, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "Fitness Tracker" in result.stdout


def test_input_date_must_match_the_archive_filename(cli_data):
    path = _log(cli_data, "2024-03-11")
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    record["date"] = "2024-03-12"
    path.write_text(yaml.safe_dump(record), encoding="utf-8")
    result = _invoke(cli_data, "insert", "-d", "2024-03-11")
    assert result.exit_code == 1
    assert "does not match" in result.output
    assert not (cli_data / "2024_workouts.yml").exists()


def test_input_symlink_cannot_escape_the_archive(cli_data, tmp_path):
    path = _log(cli_data, "2024-03-11")
    outside = tmp_path / "outside.yml"
    outside.write_bytes(path.read_bytes())
    path.unlink()
    path.symlink_to(outside)
    result = _invoke(cli_data, "insert", "-d", "2024-03-11")
    assert result.exit_code == 1
    assert "escapes" in result.output
    assert not (cli_data / "2024_workouts.yml").exists()


def test_duplicate_input_ids_are_rejected_before_writes(cli_data):
    identifier = str(uuid4())
    for number in (1, 2):
        path = _log(cli_data, "2024-03-11", number=number)
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        path.write_text(yaml.safe_dump({**record, "id": identifier}), encoding="utf-8")
    result = _invoke(cli_data, "insert", "-d", "2024-03-11")
    assert result.exit_code == 1
    assert "Multiple input files" in result.output
    assert not (cli_data / "2024_workouts.yml").exists()


def test_write_failure_returns_nonzero_without_success_message(cli_data, monkeypatch):
    _log(cli_data, "2024-03-11")

    def cannot_write(*arguments, **options):
        raise PermissionError("Fixture archive is read-only")

    monkeypatch.setattr(oxygen_cli, "set_db_and_table", cannot_write)
    result = _invoke(cli_data, "insert", "-d", "2024-03-11")
    assert result.exit_code == 1
    assert "read-only" in result.output
    assert "1 imported" not in result.output


def test_run_without_figures_never_loads_plotting_or_opens_images(cli_data, monkeypatch):
    _log(cli_data, "2024-03-11")

    def forbidden(*arguments):
        raise AssertionError("Unexpected plotting or desktop interaction")

    monkeypatch.setattr(oxygen_cli, "_plotting", forbidden)
    monkeypatch.setattr(oxygen_cli, "_open", forbidden)
    result = _invoke(cli_data, "run", "-d", "2024-03-11", "--no-figures")
    assert result.exit_code == 0, result.output
    assert len(_records(cli_data, 2024)) == 1
    assert not (cli_data / "img").exists()


def test_run_prepares_each_period_once_and_is_headless_by_default(cli_data, monkeypatch):
    performed = ("2024-03-11", "2024-03-12", "2025-01-01")
    for value in performed:
        _log(cli_data, value)
    periods = []
    opened = []
    monkeypatch.setattr(oxygen_cli, "_plotting", lambda: None)
    monkeypatch.setattr(oxygen_cli, "_prepare", lambda configuration, year, month: periods.append((year, month)) or [])
    monkeypatch.setattr(oxygen_cli, "_open", lambda paths: opened.append(paths))
    result = _invoke(cli_data, "run", "-d", ",".join(performed))
    assert result.exit_code == 0, result.output
    assert periods == [(2024, "March"), (2025, "January")]
    assert opened == []


def test_missing_plot_dependencies_fail_before_import(cli_data, monkeypatch):
    _log(cli_data, "2024-03-11")

    def missing_plotting():
        raise click.ClickException("Install the analytics dependencies")

    monkeypatch.setattr(oxygen_cli, "_plotting", missing_plotting)
    result = _invoke(cli_data, "run", "-d", "2024-03-11")
    assert result.exit_code == 1
    assert "analytics dependencies" in result.output
    assert not (cli_data / "2024_workouts.yml").exists()


def test_open_requires_figures_before_importing(cli_data):
    _log(cli_data, "2024-03-11")
    result = _invoke(cli_data, "run", "-d", "2024-03-11", "--no-figures", "--open")
    assert result.exit_code == 2
    assert "--open requires --figures" in result.output
    assert not (cli_data / "2024_workouts.yml").exists()


def test_toml_configuration_paths_are_relative_to_config_and_restore_settings(cli_data, tmp_path, monkeypatch):
    _log(cli_data, "2024-03-11")
    configuration = tmp_path / "oxygen.toml"
    configuration.write_text('[oxygen]\ndata_dir = "workout data"\nimage_dir = "reports"\n', encoding="utf-8")
    original = {key: settings.get(key) for key in ("DATA_DIR", "IMG_PATH", "REAL_WORKOUT_DATABASE")}
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    result = CliRunner().invoke(oxygen_cli.cli, ["--config", str(configuration), "insert", "-d", "2024-03-11"])
    assert result.exit_code == 0, result.output
    assert len(_records(cli_data, 2024)) == 1
    assert {key: settings.get(key) for key in original} == original


def test_command_line_paths_override_toml_configuration(cli_data, tmp_path):
    _log(cli_data, "2024-03-11")
    configuration = tmp_path / "oxygen.toml"
    configuration.write_text('[oxygen]\ndata_dir = "missing"\n', encoding="utf-8")
    result = CliRunner().invoke(oxygen_cli.cli, ["--config", str(configuration), "--data-dir", str(cli_data), "insert", "-d", "2024-03-11"])
    assert result.exit_code == 0, result.output
    assert len(_records(cli_data, 2024)) == 1


def test_shell_configuration_is_not_executed(cli_data, tmp_path):
    configuration = tmp_path / "unsafe.conf"
    marker = tmp_path / "must-not-exist"
    configuration.write_text(f"touch '{marker}'\n", encoding="utf-8")
    result = CliRunner().invoke(oxygen_cli.cli, ["--config", str(configuration), "insert", "-d", "2024-03-11"])
    assert result.exit_code == 1
    assert not marker.exists()


def test_prepare_uses_local_edits_and_publishes_figures_in_year_directory(cli_data, tmp_path, monkeypatch):
    _log(cli_data, "2024-03-11")
    assert _invoke(cli_data, "insert", "-d", "2024-03-11").exit_code == 0
    record = _records(cli_data, 2024)[0]
    state_store.save_workout({**record, "notes": "Edited in app"}, expected_version=1)
    captured = []

    def render(table, year, month, image_dir):
        captured.extend(dict(item) for item in table)
        for relative in (f"{year}/{year}_workout_frequency.png", f"{year}/workout_duration_{month}_{year}.png", "all_years/workout_duration_volume_1rm_bb_bench_press.png"):
            path = image_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fixture PNG")

    monkeypatch.setattr(oxygen_cli, "_render", render)
    destination = tmp_path / "reports with spaces"
    result = CliRunner().invoke(oxygen_cli.cli, ["--data-dir", str(cli_data), "--image-dir", str(destination), "prepare_figures", "-y", "2024", "-m", "03"])
    assert result.exit_code == 0, result.output
    assert captured[0]["notes"] == "Edited in app"
    assert len(list((destination / "2024").glob("*.png"))) == 3
    assert not (destination / "all_years").exists()


def test_no_data_and_invalid_periods_do_not_create_archives(cli_data):
    assert _invoke(cli_data, "prepare-figures", "-y", "2024", "-m", "March").exit_code == 1
    assert _invoke(cli_data, "prepare-figures", "-y", "1800").exit_code == 2
    assert _invoke(cli_data, "prepare-figures", "-m", "13").exit_code == 2
    assert list(cli_data.iterdir()) == []


def test_failed_render_does_not_replace_previous_figures(cli_data, monkeypatch):
    _log(cli_data, "2024-03-11")
    assert _invoke(cli_data, "insert", "-d", "2024-03-11").exit_code == 0
    previous = cli_data / "img/2024/2024_workout_frequency.png"
    previous.parent.mkdir(parents=True)
    previous.write_bytes(b"Previous good PNG")
    monkeypatch.setattr(oxygen_cli, "_render", lambda *arguments: None)
    result = _invoke(cli_data, "prepare-figures", "-y", "2024", "-m", "March")
    assert result.exit_code == 1
    assert "No figures could be generated" in result.output
    assert previous.read_bytes() == b"Previous good PNG"


def _one_figure(table, year, month, image_dir):
    generated = image_dir / str(year) / f"{year}_workout_frequency.png"
    generated.parent.mkdir(parents=True)
    generated.write_bytes(b"New PNG")


def test_partial_figure_copy_does_not_damage_previous_output(cli_data, monkeypatch):
    _log(cli_data, "2024-03-11")
    assert _invoke(cli_data, "insert", "-d", "2024-03-11").exit_code == 0
    previous = cli_data / "img/2024/2024_workout_frequency.png"
    previous.parent.mkdir(parents=True)
    previous.write_bytes(b"Previous good PNG")
    monkeypatch.setattr(oxygen_cli, "_render", _one_figure)

    def partial_copy(source, destination):
        Path(destination).write_bytes(b"Partial copy")
        raise OSError("Fixture copy failure")

    monkeypatch.setattr(oxygen_cli.shutil, "copyfile", partial_copy)
    result = _invoke(cli_data, "prepare-figures", "-y", "2024", "-m", "March")
    assert result.exit_code == 1
    assert "Fixture copy failure" in result.output
    assert previous.read_bytes() == b"Previous good PNG"
    assert list(previous.parent.iterdir()) == [previous]


def test_symlinked_output_cannot_escape_image_directory(cli_data, tmp_path, monkeypatch):
    _log(cli_data, "2024-03-11")
    assert _invoke(cli_data, "insert", "-d", "2024-03-11").exit_code == 0
    outside = tmp_path / "outside"
    outside.mkdir()
    previous = outside / "2024_workout_frequency.png"
    previous.write_bytes(b"Previous outside PNG")
    image_dir = cli_data / "img"
    image_dir.mkdir()
    (image_dir / "2024").symlink_to(outside, target_is_directory=True)
    monkeypatch.setattr(oxygen_cli, "_render", _one_figure)
    result = _invoke(cli_data, "prepare-figures", "-y", "2024", "-m", "March")
    assert result.exit_code == 1
    assert "escapes" in result.output
    assert previous.read_bytes() == b"Previous outside PNG"


@pytest.mark.parametrize("platform, launcher", [("darwin", "open"), ("linux", "xdg-open")])
def test_open_images_uses_a_cross_platform_argument_list(cli_data, monkeypatch, platform, launcher):
    image = cli_data / "img/2024/2024_workout_frequency.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"fixture PNG")
    opened = []
    monkeypatch.setattr(oxygen_cli.sys, "platform", platform)
    monkeypatch.setattr(oxygen_cli.shutil, "which", lambda command: f"/fixture/{command}")
    monkeypatch.setattr(oxygen_cli.subprocess, "run", lambda arguments, **options: opened.append((arguments, options)))
    result = _invoke(cli_data, "open-images", "-y", "2024", "-m", "mar")
    assert result.exit_code == 0, result.output
    assert opened == [([f"/fixture/{launcher}", str(image)], {"check": True})]


def test_open_images_uses_windows_startfile(cli_data, monkeypatch):
    image = cli_data / "img/2024/2024_workout_frequency.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"fixture PNG")
    opened = []
    monkeypatch.setattr(oxygen_cli.sys, "platform", "win32")
    monkeypatch.setattr(oxygen_cli.os, "startfile", lambda path: opened.append(path), raising=False)
    result = _invoke(cli_data, "open_images", "-y", "2024", "-m", "3")
    assert result.exit_code == 0, result.output
    assert opened == [str(image)]


def test_open_images_fails_without_images_or_viewer(cli_data, monkeypatch):
    assert _invoke(cli_data, "open-images", "-y", "2024").exit_code == 1
    image = cli_data / "img/2024/2024_workout_frequency.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"fixture PNG")
    monkeypatch.setattr(oxygen_cli.sys, "platform", "linux")
    monkeypatch.setattr(oxygen_cli.shutil, "which", lambda command: None)
    result = _invoke(cli_data, "open-images", "-y", "2024")
    assert result.exit_code == 1
    assert "No desktop image opener" in result.output


def test_real_figures_are_pngs_without_a_desktop(cli_data):
    for dependency in ("matplotlib", "pandas", "seaborn", "datetime_tools"):
        pytest.importorskip(dependency)
    _log(cli_data, "2024-03-11")
    _log(cli_data, "2024-03-18")
    result = _invoke(cli_data, "run", "-d", "2024-03-11,2024-03-18", "--no-open")
    assert result.exit_code == 0, result.output
    images = list((cli_data / "img/2024").glob("*.png"))
    assert len(images) == 3
    assert all(path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n") for path in images)


def test_help_does_not_import_optional_analytics_packages():
    result = subprocess.run(
        [sys.executable, "-c", (
            "import importlib.abc, sys\n"
            "class BlockAnalytics(importlib.abc.MetaPathFinder):\n"
            "    def find_spec(self, fullname, path=None, target=None):\n"
            "        if fullname.split('.')[0] in {'numpy', 'pandas', 'matplotlib', 'seaborn', 'datetime_tools'}:\n"
            "            raise ModuleNotFoundError('Analytics import blocked: ' + fullname, name=fullname)\n"
            "sys.meta_path.insert(0, BlockAnalytics())\n"
            "from oxygen.cli import cli\n"
            "cli(['--help'])\n"
        )],
        cwd=PROJECT_ROOT, env={**os.environ, "PYTHONPATH": os.pathsep.join((str(PROJECT_ROOT / "oxygen"), str(PROJECT_ROOT)))},
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Fitness Tracker" in result.stdout
