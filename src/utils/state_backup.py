"""Private, consistent workout backups and non-destructive offline restores."""

import argparse
from contextlib import suppress
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import shlex
import shutil
import sqlite3
import stat
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Literal
from uuid import uuid4
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile

from pydantic import BaseModel, ConfigDict, Field

from src.utils.config import settings
from src.utils.set_db_and_table import get_available_years, get_database_path
from src.utils.state_store import SCHEMA_VERSION, StateStore, state_store
from src.utils.training_metadata import metadata_path

MAX_BYTES = 512 * 1024 * 1024
MAX_FILES = 256
STATE_MEMBER = ".state/tracker.sqlite3"
METADATA = {
    "TRAINING_CATALOGUE": "metadata/exercises.yml",
    "WORKOUT_PROGRAMS": "metadata/programs.yml",
    "PROGRAM_TARGETS": "metadata/targets.yml",
}


class BackupFile(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    size: int = Field(ge=0, le=MAX_BYTES)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class BackupManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    format: Literal["fitness-tracker-backup-v1"] = "fitness-tracker-backup-v1"
    created_at: datetime
    schema_version: int = Field(ge=1, le=SCHEMA_VERSION)
    workout_table: str = Field(default="weight_training_log", min_length=1, max_length=100)
    files: dict[str, BackupFile] = Field(min_length=1, max_length=MAX_FILES)


def _sources() -> dict[str, Path]:
    if not Path(settings.DATA_DIR).expanduser().is_dir():
        raise FileNotFoundError("The configured workout archive directory does not exist")
    sources = {f"{year:04d}_workouts.yml": get_database_path("real", year=year) for year in get_available_years()}
    sources.update({member: metadata_path(setting) for setting, member in METADATA.items() if metadata_path(setting).is_file()})
    return sources


def _signature(path: Path) -> tuple[int, int, int, int, int]:
    value = path.stat()
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns


def _describe(path: Path) -> BackupFile:
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    return BackupFile(size=path.stat().st_size, sha256=digest)


def _allowed_member(name: str) -> bool:
    return name == STATE_MEMBER or name in METADATA.values() or re.fullmatch(r"[0-9]{4}_workouts\.yml", name) is not None


def create_backup(directory: Path, *, store: StateStore = state_store) -> Path:
    directory = directory.expanduser().resolve()
    sources = _sources()
    versions = {name: _signature(path) for name, path in sources.items()}
    if len(sources) + 2 > MAX_FILES or sum(value[2] for value in versions.values()) > MAX_BYTES:
        raise ValueError("Backup exceeds the file-count or 512 MiB size limit")
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    with TemporaryDirectory(prefix="fitness-snapshot-") as temporary_directory:
        snapshot = Path(temporary_directory)
        for name, source in sources.items():
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copyfile(source, target)
            target.chmod(0o600)
        store.backup(snapshot / STATE_MEMBER)
        if _sources() != sources or any(_signature(path) != versions[name] for name, path in sources.items()):
            raise ValueError("Workout archives or metadata changed during backup; retry after the writer finishes")
        files = {name: _describe(snapshot / name) for name in (*sources, STATE_MEMBER)}
        manifest = BackupManifest(created_at=datetime.now(timezone.utc), schema_version=SCHEMA_VERSION, workout_table=str(settings.REAL_WEIGHT_TABLE), files=files)
        if sum(entry.size for entry in files.values()) > MAX_BYTES:
            raise ValueError("Backup exceeds the 512 MiB size limit")
        destination = directory / f"fitness-tracker-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{uuid4().hex}.zip"
        temporary_path = None
        try:
            with NamedTemporaryFile(dir=directory, prefix=".fitness-backup-", suffix=".tmp", delete=False) as output:
                temporary_path = Path(output.name)
                with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
                    for name in files:
                        archive.write(snapshot / name, name)
                    archive.writestr("manifest.json", manifest.model_dump_json(indent=2))
                output.flush()
                os.fsync(output.fileno())
            if destination.exists():
                raise FileExistsError(destination)
            os.replace(temporary_path, destination)
            return destination
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)


def restore_backup(backup: Path, destination: Path) -> Path:
    destination = destination.expanduser()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Restore requires a new destination directory")
    destination = destination.resolve()
    with ZipFile(backup.expanduser()) as archive:
        members = archive.infolist()
        names = [member.filename for member in members]
        if len(members) > MAX_FILES or len(names) != len(set(names)) or sum(member.file_size for member in members) > MAX_BYTES:
            raise ValueError("Backup has duplicate entries or exceeds its file-count or size limit")
        for member in members:
            if member.is_dir() or member.flag_bits & 1 or stat.S_IFMT(member.external_attr >> 16) not in (0, stat.S_IFREG):
                raise ValueError("Backup contains an unsupported file or symlink")
            if member.filename != "manifest.json" and not _allowed_member(member.filename):
                raise ValueError("Backup contains an unexpected file path")
        if "manifest.json" not in names or archive.getinfo("manifest.json").file_size > 65536:
            raise ValueError("Backup manifest is missing or too large")
        manifest = BackupManifest.model_validate_json(archive.read("manifest.json"))
        if set(names) != set(manifest.files) | {"manifest.json"} or STATE_MEMBER not in manifest.files:
            raise ValueError("Backup files do not match the manifest")
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with TemporaryDirectory(dir=destination.parent, prefix=".fitness-restore-") as temporary_directory:
            restored = Path(temporary_directory) / "restored"
            restored.mkdir(mode=0o700)
            for name, entry in manifest.files.items():
                if archive.getinfo(name).file_size != entry.size:
                    raise ValueError("Backup file size does not match its manifest")
                target = restored / name
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                with archive.open(name) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
                target.chmod(0o600)
                if _describe(target) != entry:
                    raise ValueError("Backup checksum verification failed")
            restored_store = StateStore(restored / STATE_MEMBER)
            with restored_store.connection() as connection:
                if connection.execute("PRAGMA user_version").fetchone()[0] != manifest.schema_version:
                    raise ValueError("Backup schema version does not match its manifest")
                if connection.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise sqlite3.DatabaseError("Backup database failed its integrity check")
                if connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal":
                    raise ValueError("Backup database must be self-contained, without WAL files")
            with restored_store.connection(write=True) as connection:
                connection.execute("DELETE FROM sessions")
                connection.execute("DELETE FROM login_attempts")
            destination.mkdir(mode=0o700)
            try:
                os.replace(restored, destination)
            except Exception:
                with suppress(OSError):
                    destination.rmdir()
                raise
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Create private full-state snapshots or restore into a new directory.")
    commands = parser.add_subparsers(dest="command", required=True)
    backup_command = commands.add_parser("backup")
    backup_command.add_argument("directory", type=Path)
    restore_command = commands.add_parser("restore")
    restore_command.add_argument("backup", type=Path)
    restore_command.add_argument("destination", type=Path)
    commands.add_parser("migrate")
    arguments = parser.parse_args()
    try:
        if arguments.command == "backup":
            print(f"Backup created: {create_backup(arguments.directory)}")
            print("This backup includes private workout and authentication data; keep it protected.")
        elif arguments.command == "migrate":
            state_store.migrate()
            print(f"State schema version {SCHEMA_VERSION} is ready.")
        else:
            restored = restore_backup(arguments.backup, arguments.destination)
            print(f"Restored into: {restored}. Existing sessions were revoked.")
            with ZipFile(arguments.backup.expanduser()) as archive:
                manifest = BackupManifest.model_validate_json(archive.read("manifest.json"))
            environment = {"DATA_DIR": restored, "STATE_DIR": restored / ".state", "REAL_WORKOUT_DATABASE": restored / "<YEAR>_workouts.yml", "REAL_WEIGHT_TABLE": manifest.workout_table, **{setting: restored / member for setting, member in METADATA.items()}}
            for setting, value in environment.items():
                print(f"export FITNESS_TRACKER_{setting}={shlex.quote(str(value))}")
    except (OSError, ValueError, sqlite3.Error, BadZipFile) as error:
        parser.exit(1, f"Backup operation failed: {error}\n")


if __name__ == "__main__":
    main()
