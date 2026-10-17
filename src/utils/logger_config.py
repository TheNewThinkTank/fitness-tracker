"""Logging configuration for the project using loguru."""

import sys
from pathlib import Path
from loguru import logger  # type: ignore

from src.utils.log_archive import (
    archive_log,
    cleanup_archives,
    diagnostic_log_path,
    private_log_opener,
    rotation_required,
)


def setup_logger(log_file: str = "app.log", log_dir: str | Path | None = None) -> None:
    """Configure loguru for file + console output.

    :param log_file: Name of the log file, defaults to "app.log"
    :type log_file: str, optional
    :param log_dir: Log directory, defaults to FITNESS_TRACKER_LOG_DIR or project logs/
    :type log_dir: str, optional
    """
    source = diagnostic_log_path(log_file, log_dir)
    cleanup_archives(log_file, source.parent)

    def rotate(message, output):
        return rotation_required(
            Path(output.name), str(message), message.record["time"]
        )

    def compress(filename):
        archive_log(Path(filename), log_file, source.parent)
        cleanup_archives(log_file, source.parent)

    logger.remove()  # Remove default handler
    logger.add(sys.stderr, level="INFO", backtrace=False, diagnose=False)
    logger.add(
        source,
        level="DEBUG",
        format="{time:YYYY-MM-DDTHH:mm:ss.SSSZ} {name} {level} {message}",
        rotation=rotate,
        compression=compress,
        encoding="utf-8",
        opener=private_log_opener,
        catch=False,
        backtrace=False,
        diagnose=False,
    )


def log_running_file(file_path: str) -> None:
    """Log the currently-running script path."""
    logger.info("Running {} ...", "/".join(file_path.split("/")[-4:]))
