"""Converts a JSON file to a YAML file.
"""

from pathlib import Path
from utils.config_loader import ConfigLoader  # type: ignore
from file_convertion_tools.json_to_yaml import json_to_yaml  # type: ignore


def main():

    env_vars = ConfigLoader.load_env_variables()
    config = ConfigLoader.load_config()

    in_file_name = "/db.json"  # f"/log_archive/JSON/2023/June/test.json"
    in_file = f'{config["google_drive_data_path"]}/{env_vars["athlete"]}{in_file_name}'

    json_to_yaml(Path(in_file))


if __name__ == "__main__":
    main()
