"""Load a yaml file into a dictionary.
"""

import yaml  # type: ignore


def load_yaml_file(file_path: str) -> dict:
    """Load a yaml file into a dictionary.

    :param file_path: File path to the yaml file.
    :type file_path: str
    :return: Dictionary containing the yaml file data.
    :rtype: dict
    """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
