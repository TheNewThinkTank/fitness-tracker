"""Converts a JSON file to a YAML file.
"""

from pathlib import Path
from file_convertion_tools.json_to_yaml import json_to_yaml  # type: ignore
from src.utils.config_loader import config_data  # type: ignore


def main() -> None:
    """Convert a JSON file to a YAML file.
    """

    in_file_name = "/db.json"  # f"/log_archive/JSON/2023/June/test.json"
    in_file = f'{config_data["google_drive_data_path"]}/{config_data["athlete"]}{in_file_name}'

    json_to_yaml(Path(in_file))


if __name__ == "__main__":
    main()
