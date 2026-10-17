"""Shared rotation and archival policy for single-writer diagnostic logs."""

import argparse
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import BinaryIO

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAX_LOG_BYTES = 10 * 1024 * 1024
EVENT_DATE = re.compile(rb"^(\d{4}-\d{2}-\d{2})[ T]\d{2}:\d{2}:\d{2}(?:[ .Z+-]|$)")
MONTH = re.compile(r"\d{4}-(?:0[1-9]|1[0-2])")
YEARLESS_EVENT = re.compile(rb"^\d{2}-\d{2} \d{2}:\d{2}\s")
MIGRATION_FILES = ("fitcli.log", "insert.log", "model.log", "validate.log")


@dataclass(frozen=True)
class LogInventory:
    source: Path
    signature: tuple[int, int, int, int, int]
    sha256: str
    lines: int
    period_bytes: dict[str, int]


def resolve_log_dir(log_dir: str | Path | None = None) -> Path:
    """Resolve relative log directories against the project, not the working directory."""
    if log_dir is None:
        from src.utils.config import settings

        log_dir = os.environ.get("FITNESS_TRACKER_LOG_DIR")
        if log_dir is None:
            log_dir = settings.get("LOG_DIR", "logs")
    directory = Path(log_dir)
    directory = directory.expanduser()
    if not directory.is_absolute():
        directory = PROJECT_ROOT / directory
    return directory.resolve()


def private_log_opener(filename: str, flags: int) -> int:
    return os.open(filename, flags | getattr(os, "O_NOFOLLOW", 0), 0o600)


def _regular_file(source: Path) -> None:
    if source.is_symlink() or (source.exists() and not source.is_file()):
        raise ValueError(f"Expected a regular diagnostic log: {source}")


def diagnostic_log_path(log_file: str, log_dir: str | Path | None = None) -> Path:
    if (
        Path(log_file).name != log_file
        or not log_file.endswith(".log")
        or log_file.startswith(".")
    ):
        raise ValueError("The log filename must be a basename ending in .log")
    directory = resolve_log_dir(log_dir)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    source = directory / log_file
    _regular_file(source)
    return source


def _event_month(line: bytes) -> str | None:
    match = EVENT_DATE.match(line)
    if match is None:
        return None
    try:
        return date.fromisoformat(match[1].decode("ascii")).strftime("%Y-%m")
    except ValueError:
        return None


def rotation_required(source: Path, message: str, now: datetime) -> bool:
    _regular_file(source)
    if not source.exists() or source.stat().st_size == 0:
        return False
    with source.open("rb") as stream:
        month = _event_month(stream.readline(64))
        stream.seek(-1, os.SEEK_END)
        if stream.read(1) != b"\n":
            return True
    return (
        month != now.strftime("%Y-%m")
        or source.stat().st_size + len(message.encode("utf-8")) > MAX_LOG_BYTES
    )


def _archive_month(source: Path) -> str:
    periods = inspect_log(source).period_bytes
    return next(iter(periods)) if len(periods) == 1 else "legacy"


def _signature(source: Path) -> tuple[int, int, int, int, int]:
    info = source.stat()
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _sync_directory(directory: Path) -> None:
    if os.name == "posix":
        descriptor = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def _archive_directory(directory: Path, period: str) -> Path:
    if period != "legacy" and MONTH.fullmatch(period) is None:
        raise ValueError("Invalid archive period")
    archive_root = directory / "archive"
    destination = archive_root / period
    for folder in (archive_root, destination):
        if folder.is_symlink():
            raise ValueError(f"Archive directories must not be symlinks: {folder}")
        existed = folder.exists()
        folder.mkdir(mode=0o700, parents=True, exist_ok=True)
        if not existed:
            _sync_directory(folder.parent)
    return destination


def archive_log(
    source: Path,
    log_file: str,
    log_dir: str | Path | None = None,
    *,
    period: str | None = None,
    remove_source: bool = True,
) -> Path:
    """Publish a verified gzip archive before removing a closed source file."""
    directory = resolve_log_dir(log_dir)
    diagnostic_log_path(log_file, directory)
    _regular_file(source)
    if not source.resolve().is_relative_to(directory):
        raise ValueError("Diagnostic logs must be inside the configured log directory")
    original_signature = _signature(source)
    destination = _archive_directory(directory, period or _archive_month(source))
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".archive-", suffix=".tmp", dir=destination
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            with source.open("rb") as original:
                expected_digest = hashlib.file_digest(original, "sha256").digest()
                original.seek(0)
                with gzip.GzipFile(
                    filename="", mode="wb", fileobj=output, mtime=0
                ) as compressed:
                    shutil.copyfileobj(original, compressed)
            output.flush()
            os.fsync(output.fileno())
        with gzip.open(temporary, "rb") as compressed:
            if hashlib.file_digest(compressed, "sha256").digest() != expected_digest:
                raise OSError("Compressed log verification failed; source preserved")
        if _signature(source) != original_signature:
            raise OSError("Diagnostic log changed during archival; source preserved")
        sequence = 1
        while True:
            archive = destination / f"{Path(log_file).stem}.{sequence:04d}.log.gz"
            try:
                os.link(temporary, archive)
                break
            except FileExistsError:
                sequence += 1
        _sync_directory(destination)
        if remove_source:
            source.unlink()
            _sync_directory(source.parent)
        return archive
    finally:
        temporary.unlink(missing_ok=True)


def cleanup_archives(
    log_file: str, log_dir: str | Path | None = None, *, now: datetime | None = None
) -> None:
    """Apply opt-in archive-age retention without touching legacy snapshots."""
    configured_days = os.environ.get("FITNESS_TRACKER_LOG_RETENTION_DAYS", "0")
    try:
        days = int(configured_days)
    except ValueError as exc:
        raise ValueError(
            "FITNESS_TRACKER_LOG_RETENTION_DAYS must be a non-negative integer"
        ) from exc
    if days < 0:
        raise ValueError(
            "FITNESS_TRACKER_LOG_RETENTION_DAYS must be a non-negative integer"
        )
    if days == 0:
        return
    archive_root = resolve_log_dir(log_dir) / "archive"
    if archive_root.is_symlink():
        raise ValueError("Archive directories must not be symlinks")
    if not archive_root.exists():
        return
    cutoff = ((now or datetime.now().astimezone()) - timedelta(days=days)).timestamp()
    filename_pattern = re.compile(re.escape(Path(log_file).stem) + r"\.\d{4,}\.log\.gz")
    for folder in archive_root.iterdir():
        if (
            MONTH.fullmatch(folder.name) is None
            or folder.is_symlink()
            or not folder.is_dir()
        ):
            continue
        for archived_file in folder.iterdir():
            if (
                filename_pattern.fullmatch(archived_file.name)
                and not archived_file.is_symlink()
                and archived_file.is_file()
                and archived_file.stat().st_mtime < cutoff
            ):
                archived_file.unlink()


def append_shell_log(
    log_file: str,
    message: str,
    log_dir: str | Path | None = None,
    *,
    now: datetime | None = None,
) -> str:
    moment = now or datetime.now().astimezone()
    source = diagnostic_log_path(log_file, log_dir)
    line = f"{moment.isoformat(timespec='milliseconds')} - {message}\n"
    cleanup_archives(log_file, source.parent, now=moment)
    if rotation_required(source, line, moment):
        archive_log(source, log_file, source.parent)
    with open(source, "a", encoding="utf-8", opener=private_log_opener) as output:
        output.write(line)
    return line


def inspect_log(source: Path) -> LogInventory:
    """Inventory event months without inferring execution years from message contents."""
    _regular_file(source)
    signature = _signature(source)
    digest = hashlib.sha256()
    periods: dict[str, int] = {}
    current_period = "legacy"
    uncertain_year = False
    lines = 0
    with source.open("rb") as original:
        for line in original:
            digest.update(line)
            month = _event_month(line)
            if (
                (lines == 0 and month is None)
                or YEARLESS_EVENT.match(line)
                or (EVENT_DATE.match(line) and month is None)
            ):
                uncertain_year = True
            current_period = month or current_period
            periods[current_period] = periods.get(current_period, 0) + len(line)
            lines += 1
    if _signature(source) != signature:
        raise OSError(f"Diagnostic log changed during inspection: {source}")
    if uncertain_year:
        periods = {"legacy": sum(periods.values())}
    return LogInventory(source, signature, digest.hexdigest(), lines, periods)


def _check_unchanged(inventory: LogInventory) -> None:
    _regular_file(inventory.source)
    if _signature(inventory.source) != inventory.signature:
        raise OSError(
            f"Diagnostic log changed during migration; source preserved: {inventory.source}"
        )


def _stage_months(inventory: LogInventory, staging: Path) -> dict[str, Path]:
    destinations: dict[str, Path] = {}
    if "legacy" in inventory.period_bytes:
        return destinations
    digest = hashlib.sha256()
    period = "legacy"
    with ExitStack() as stack:
        outputs: dict[str, BinaryIO] = {}
        original = stack.enter_context(inventory.source.open("rb"))
        for line in original:
            digest.update(line)
            period = _event_month(line) or period
            if period not in outputs:
                destination = staging / f"{period}.log"
                outputs[period] = stack.enter_context(
                    open(destination, "wb", opener=private_log_opener)
                )
                destinations[period] = destination
            outputs[period].write(line)
        for output in outputs.values():
            output.flush()
            os.fsync(output.fileno())
    if digest.hexdigest() != inventory.sha256:
        raise OSError("Diagnostic log changed while partitioning; source preserved")
    return destinations


def migrate_logs(
    log_dir: str | Path | None = None,
    *,
    apply: bool = False,
    now: datetime | None = None,
) -> list[dict[str, object]]:
    """Preview or apply a lossless, per-file migration while CLI writers are stopped."""
    directory = resolve_log_dir(log_dir)
    current_period = (now or datetime.now().astimezone()).strftime("%Y-%m")
    inventories = []
    for filename in MIGRATION_FILES:
        source = directory / filename
        _regular_file(source)
        if source.exists():
            inventories.append(inspect_log(source))
    results: list[dict[str, object]] = []
    for inventory in inventories:
        needs_migration = any(
            period != current_period for period in inventory.period_bytes
        )
        result: dict[str, object] = {
            "file": inventory.source.name,
            "bytes": inventory.signature[2],
            "lines": inventory.lines,
            "sha256": inventory.sha256,
            "period_bytes": inventory.period_bytes,
            "retained_bytes": inventory.period_bytes.get(current_period, 0),
            "action": "migrate" if needs_migration else "unchanged",
            "applied": False,
        }
        results.append(result)
        if not apply or not needs_migration:
            continue
        _check_unchanged(inventory)
        backup = archive_log(
            inventory.source,
            inventory.source.name,
            directory,
            period="legacy",
            remove_source=False,
        )
        result["original_backup"] = str(backup.relative_to(directory))
        with tempfile.TemporaryDirectory(
            prefix=".log-migration-", dir=directory
        ) as temporary:
            staging = Path(temporary)
            partitions = _stage_months(inventory, staging)
            _check_unchanged(inventory)
            archives = []
            for period, partition in sorted(partitions.items()):
                if period != current_period:
                    archive = archive_log(
                        partition, inventory.source.name, directory, period=period
                    )
                    archives.append(str(archive.relative_to(directory)))
            replacement = partitions.get(current_period, staging / "empty.log")
            if not replacement.exists():
                with open(replacement, "wb", opener=private_log_opener) as output:
                    os.fsync(output.fileno())
            _check_unchanged(inventory)
            os.replace(replacement, inventory.source)
            _sync_directory(directory)
        result["archives"] = archives
        result["applied"] = True
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage diagnostic logs, not workout archives."
    )
    parser.add_argument("--log-dir", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("path", help="Print the resolved log directory")
    append = commands.add_parser("append", help="Append a timestamped shell message")
    append.add_argument("--file", required=True)
    append.add_argument("--message", required=True)
    migrate = commands.add_parser(
        "migrate", help="Preview migration of the four existing CLI logs"
    )
    migrate.add_argument(
        "--apply",
        action="store_true",
        help="Archive old records after preserving verified original snapshots",
    )
    arguments = parser.parse_args()
    try:
        if arguments.command == "path":
            print(resolve_log_dir(arguments.log_dir))
        elif arguments.command == "migrate":
            print(
                json.dumps(
                    migrate_logs(arguments.log_dir, apply=arguments.apply), indent=2
                )
            )
        else:
            print(
                append_shell_log(arguments.file, arguments.message, arguments.log_dir),
                end="",
            )
    except (OSError, ValueError) as exc:
        print(f"Diagnostic logging failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
