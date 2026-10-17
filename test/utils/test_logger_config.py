import gzip
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

import pytest

from src.utils.config import PROJECT_ROOT
from src.utils import log_archive
from src.utils.log_archive import (
    append_shell_log,
    archive_log,
    cleanup_archives,
    migrate_logs,
    resolve_log_dir,
)


def test_log_directory_does_not_depend_on_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("FITNESS_TRACKER_LOG_DIR", raising=False)
    assert resolve_log_dir() == PROJECT_ROOT / "logs"
    monkeypatch.setenv("FITNESS_TRACKER_LOG_DIR", "alternate-logs")
    assert resolve_log_dir() == PROJECT_ROOT / "alternate-logs"
    assert resolve_log_dir(tmp_path) == tmp_path


def test_file_logs_rotate_compress_and_preserve_archives(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys\n"
                "from src.utils.logger_config import logger, setup_logger\n"
                "from src.utils import log_archive\n"
                "log_archive.MAX_LOG_BYTES = 512\n"
                "setup_logger(log_dir=sys.argv[1])\n"
                "for number in range(20):\n"
                "    logger.debug('Record {}: {}', number, 'x' * 300)\n"
                "logger.remove()\n"
            ),
            str(tmp_path),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stderr == ""
    assert (tmp_path / "app.log").is_file()
    archives = list((tmp_path / "archive").glob("????-??/app.*.log.gz"))
    assert len(archives) == 19
    assert len(list(tmp_path.iterdir())) == 2
    active = (tmp_path / "app.log").read_text(encoding="utf-8")
    assert "Record 19:" in active
    assert re.match(
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{2}:\d{2} ", active
    )
    assert all(
        "Record " in gzip.decompress(path.read_bytes()).decode() for path in archives
    )


@pytest.mark.parametrize(
    "previous, current",
    [
        ("2026-09-30T23:59:59+00:00", "2026-10-01T00:00:00+00:00"),
        ("2025-12-31T23:59:59+00:00", "2026-01-01T00:00:00+00:00"),
    ],
)
def test_small_logs_rotate_on_calendar_boundaries_after_restart(
    tmp_path, previous, current
):
    original = f"{previous} - previous entry\n"
    (tmp_path / "fitcli.log").write_text(original, encoding="utf-8")
    line = append_shell_log(
        "fitcli.log", "new entry", tmp_path, now=datetime.fromisoformat(current)
    )
    archives = list((tmp_path / "archive" / previous[:7]).glob("*.gz"))
    assert len(archives) == 1
    assert gzip.decompress(archives[0].read_bytes()).decode() == original
    assert (tmp_path / "fitcli.log").read_text() == line


def test_python_logger_rotates_old_file_on_first_record(tmp_path):
    original = b"2024-07-17 17:02:10 - previous entry\n"
    (tmp_path / "insert.log").write_bytes(original)
    subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys\n"
                "from src.utils.logger_config import logger, setup_logger\n"
                "setup_logger('insert.log', sys.argv[1])\n"
                "logger.debug('new entry')\n"
                "logger.remove()\n"
            ),
            str(tmp_path),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    archives = list((tmp_path / "archive" / "2024-07").glob("*.gz"))
    assert len(archives) == 1
    assert gzip.decompress(archives[0].read_bytes()) == original
    assert "previous entry" not in (tmp_path / "insert.log").read_text()


def test_undated_logs_are_preserved_as_legacy(tmp_path):
    original = b"07-08 14:40 INFO workout date: 2026-01-01\n  continued details\n"
    (tmp_path / "insert.log").write_bytes(original)
    append_shell_log("insert.log", "new entry", tmp_path)
    archives = list((tmp_path / "archive" / "legacy").glob("*.gz"))
    assert len(archives) == 1
    assert gzip.decompress(archives[0].read_bytes()) == original


def test_size_rotation_counts_encoded_bytes_and_does_not_overwrite_archives(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(log_archive, "MAX_LOG_BYTES", 220)
    moment = datetime(2026, 10, 17, tzinfo=timezone.utc)
    lines = [
        append_shell_log(
            "fitcli.log", f"message {number}: " + "\u00e9" * 40, tmp_path, now=moment
        )
        for number in range(3)
    ]
    archives = sorted((tmp_path / "archive" / "2026-10").glob("*.gz"))
    assert [archive.name for archive in archives] == [
        "fitcli.0001.log.gz",
        "fitcli.0002.log.gz",
    ]
    recovered = "".join(
        gzip.decompress(archive.read_bytes()).decode() for archive in archives
    )
    assert recovered + (tmp_path / "fitcli.log").read_text() == "".join(lines)
    assert all(archive.stat().st_mode & 0o777 == 0o600 for archive in archives)


def test_retention_is_opt_in_and_never_removes_legacy_or_unrelated_files(
    tmp_path, monkeypatch
):
    source = tmp_path / "fitcli.log"
    source.write_text("2025-01-01T00:00:00+00:00 - dated\n")
    dated = archive_log(source, "fitcli.log", tmp_path)
    source.write_text("undated\n")
    legacy = archive_log(source, "fitcli.log", tmp_path)
    unrelated = dated.with_name("notes.gz")
    unrelated.write_bytes(b"unrelated")
    for archived_file in (dated, legacy, unrelated):
        os.utime(archived_file, (0, 0))
    monkeypatch.delenv("FITNESS_TRACKER_LOG_RETENTION_DAYS", raising=False)
    cleanup_archives("fitcli.log", tmp_path)
    assert dated.exists()
    monkeypatch.setenv("FITNESS_TRACKER_LOG_RETENTION_DAYS", "365")
    cleanup_archives("fitcli.log", tmp_path)
    assert not dated.exists()
    assert legacy.exists() and unrelated.exists()


@pytest.mark.parametrize("failure", ["compression", "verification", "publication"])
def test_archive_failures_preserve_source_and_stop_append(
    tmp_path, monkeypatch, failure
):
    source = tmp_path / "fitcli.log"
    original = b"2024-07-17 17:02:10 - previous entry\n"
    source.write_bytes(original)

    def fail(*args, **kwargs):
        raise OSError("injected archive failure")

    if failure == "compression":
        monkeypatch.setattr(log_archive.gzip, "GzipFile", fail)
    elif failure == "verification":
        monkeypatch.setattr(
            log_archive.shutil,
            "copyfileobj",
            lambda original, compressed: compressed.write(b"incomplete"),
        )
    else:
        monkeypatch.setattr(log_archive.os, "link", fail)
    with pytest.raises(OSError):
        append_shell_log("fitcli.log", "must not append", tmp_path)
    assert source.read_bytes() == original
    assert not list(tmp_path.rglob("*.tmp"))
    assert not list(tmp_path.rglob("*.gz"))


def test_log_symlinks_are_rejected(tmp_path):
    external = tmp_path / "external"
    external.write_text("untouched")
    (tmp_path / "fitcli.log").symlink_to(external)
    with pytest.raises(ValueError, match="regular"):
        append_shell_log("fitcli.log", "must not append", tmp_path)
    assert external.read_text() == "untouched"


def test_migration_preserves_originals_multiline_records_and_current_month(tmp_path):
    old = b"2024-07-17 17:02:10 - old entry\n  multiline details\n"
    recent = b"2026-09-30T23:59:59+00:00 - recent entry\n"
    current = b"2026-10-01T00:00:00+00:00 - current entry without final newline"
    originals = {
        "fitcli.log": old + recent + current,
        "insert.log": b"07-08 14:40 INFO workout date: 2026-07-08\n  details\n",
        "model.log": b"09-28 10:45 INFO model\n",
        "validate.log": b"07-08 14:40 INFO validation\n",
    }
    for filename, content in originals.items():
        (tmp_path / filename).write_bytes(content)
    moment = datetime(2026, 10, 17, tzinfo=timezone.utc)
    preview = migrate_logs(tmp_path, now=moment)
    assert len(preview) == 4
    assert not (tmp_path / "archive").exists()
    assert all(
        (tmp_path / filename).read_bytes() == content
        for filename, content in originals.items()
    )

    result = migrate_logs(tmp_path, apply=True, now=moment)
    for entry in result:
        content = originals[entry["file"]]
        assert entry["sha256"] == hashlib.sha256(content).hexdigest()
        assert (
            gzip.decompress((tmp_path / entry["original_backup"]).read_bytes())
            == content
        )
        assert entry["applied"] is True
    assert (
        gzip.decompress((tmp_path / "archive/2024-07/fitcli.0001.log.gz").read_bytes())
        == old
    )
    assert (
        gzip.decompress((tmp_path / "archive/2026-09/fitcli.0001.log.gz").read_bytes())
        == recent
    )
    assert (tmp_path / "fitcli.log").read_bytes() == current
    assert all(
        (tmp_path / filename).read_bytes() == b""
        for filename in originals
        if filename != "fitcli.log"
    )
    archives_before = set(tmp_path.rglob("*.gz"))
    repeated = migrate_logs(tmp_path, apply=True, now=moment)
    assert all(entry["action"] == "unchanged" for entry in repeated)
    assert set(tmp_path.rglob("*.gz")) == archives_before


def test_migration_failure_keeps_source_and_verified_backup(tmp_path, monkeypatch):
    original = b"2024-07-17 17:02:10 - old entry\n"
    source = tmp_path / "fitcli.log"
    source.write_bytes(original)
    real_archive = log_archive.archive_log

    def fail_monthly_archive(source, filename, directory, **options):
        if options.get("period") != "legacy":
            raise OSError("injected monthly archive failure")
        return real_archive(source, filename, directory, **options)

    monkeypatch.setattr(log_archive, "archive_log", fail_monthly_archive)
    with pytest.raises(OSError, match="injected"):
        migrate_logs(tmp_path, apply=True)
    assert source.read_bytes() == original
    assert (
        gzip.decompress((tmp_path / "archive/legacy/fitcli.0001.log.gz").read_bytes())
        == original
    )
    assert not list(tmp_path.glob(".log-migration-*"))


def test_migration_does_not_replace_a_log_that_changes_during_staging(
    tmp_path, monkeypatch
):
    source = tmp_path / "fitcli.log"
    original = b"2024-07-17 17:02:10 - old entry\n"
    changed = original + b"2026-10-17 12:00:00 - another writer\n"
    source.write_bytes(original)
    real_stage = log_archive._stage_months

    def change_after_staging(inventory, staging):
        result = real_stage(inventory, staging)
        source.write_bytes(changed)
        return result

    monkeypatch.setattr(log_archive, "_stage_months", change_after_staging)
    with pytest.raises(OSError, match="changed during migration"):
        migrate_logs(tmp_path, apply=True)
    assert source.read_bytes() == changed


def test_migration_cli_defaults_to_preview_from_another_directory(tmp_path):
    directory = tmp_path / "logs with spaces"
    directory.mkdir()
    source = directory / "fitcli.log"
    original = b"2024-07-17 17:02:10 - old entry\n"
    source.write_bytes(original)
    environment = {**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.utils.log_archive",
            "--log-dir",
            str(directory),
            "migrate",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout)[0]["action"] == "migrate"
    assert source.read_bytes() == original
    assert not (directory / "archive").exists()


def test_python_logging_does_not_swallow_rotation_failures(tmp_path):
    original = b"2024-07-17 17:02:10 - previous entry\n"
    (tmp_path / "insert.log").write_bytes(original)
    (tmp_path / "archive").write_text("blocked")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys\n"
                "from src.utils.logger_config import logger, setup_logger\n"
                "setup_logger('insert.log', sys.argv[1])\n"
                "logger.debug('must not append')\n"
            ),
            str(tmp_path),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    preserved = list(tmp_path.glob("insert*.log"))
    assert len(preserved) == 1
    assert preserved[0].read_bytes() == original


def test_unterminated_record_is_archived_before_appending(tmp_path):
    original = b"2026-10-17T12:00:00+00:00 - no final newline"
    (tmp_path / "fitcli.log").write_bytes(original)
    moment = datetime(2026, 10, 17, 13, tzinfo=timezone.utc)
    line = append_shell_log("fitcli.log", "new entry", tmp_path, now=moment)
    archive = tmp_path / "archive/2026-10/fitcli.0001.log.gz"
    assert gzip.decompress(archive.read_bytes()) == original
    assert (tmp_path / "fitcli.log").read_text() == line


def test_log_directory_override_still_loads_dotenv_retention(tmp_path):
    isolated = tmp_path / "isolated"
    utilities = isolated / "src/utils"
    utilities.mkdir(parents=True)
    (isolated / "src/__init__.py").write_text("")
    (utilities / "__init__.py").write_text("")
    for filename in ("config.py", "log_archive.py"):
        shutil.copyfile(PROJECT_ROOT / "src/utils" / filename, utilities / filename)
    configuration = isolated / ".config"
    configuration.mkdir()
    (configuration / "settings.toml").write_text('[default]\nDATA_DIR = "data"\n')
    (isolated / ".env").write_text("FITNESS_TRACKER_LOG_RETENTION_DAYS=365\n")
    environment = {
        **os.environ,
        "PYTHONPATH": str(isolated),
        "FITNESS_TRACKER_LOG_DIR": "chosen-logs",
    }
    environment.pop("FITNESS_TRACKER_LOG_RETENTION_DAYS", None)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import os\n"
                "from src.utils.log_archive import resolve_log_dir\n"
                "print(resolve_log_dir())\n"
                "print(os.environ['FITNESS_TRACKER_LOG_RETENTION_DAYS'])\n"
            ),
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.splitlines() == [str(isolated / "chosen-logs"), "365"]
