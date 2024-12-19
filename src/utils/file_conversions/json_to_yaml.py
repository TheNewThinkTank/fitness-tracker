"""_summary_
"""

from utils.config_loader import ConfigLoader  # type: ignore
from file_convertion_tools.json_to_yaml import json_to_yaml  # type: ignore


def main():

    env_vars = ConfigLoader.load_env_variables()

    config = ConfigLoader.load_config(
        athlete=env_vars["athlete"],
        user=env_vars["user"],
        email=env_vars["email"],
    )

    in_file_name = "/db.json"  # f"/log_archive/JSON/2023/June/test.json"

    in_file = f'{config["google_drive_data_path"]}/{env_vars["athlete"]}{in_file_name}'

    # TODO: test that below command works
    json_to_yaml(in_file)


if __name__ == "__main__":
    main()
