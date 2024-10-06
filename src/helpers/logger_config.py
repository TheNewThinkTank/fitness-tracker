import logging
from pathlib import Path


def setup_logger(log_file: str = "insert.log", log_dir: str = "logs/"):
    # Create the log directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Configure the logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M",
        filename=f"{log_dir}/{log_file}",
        filemode="w",
    )

    # Console handler for the logger
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    console.setFormatter(formatter)

    # Add console handler to the root logger
    logging.getLogger("").addHandler(console)
    logging.info("Logger initialized")


def log_running_file(file_path):
    """Optional utility for logging the running file."""
    logging.info("Running %s ...", "/".join(file_path.split("/")[-4:]))
