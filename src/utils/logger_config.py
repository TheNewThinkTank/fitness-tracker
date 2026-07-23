"""Logging configuration for the project using loguru."""

import sys
from pathlib import Path
from loguru import logger  # type: ignore


def setup_logger(log_file: str = "app.log", log_dir: str = "logs/") -> None:
    """Configure loguru for file + console output.

    :param log_file: Name of the log file, defaults to "app.log"
    :type log_file: str, optional
    :param log_dir: Log directory, defaults to "logs/"
    :type log_dir: str, optional
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logger.remove()  # Remove default handler
    logger.add(sys.stderr, level="INFO")
    logger.add(
        f"{log_dir}/{log_file}",
        level="DEBUG",
        format="{time:MM-DD HH:mm} {name} {level} {message}",
        rotation="10 MB",
    )


def log_running_file(file_path: str) -> None:
    """Log the currently-running script path."""
    logger.info("Running {} ...", "/".join(file_path.split("/")[-4:]))
