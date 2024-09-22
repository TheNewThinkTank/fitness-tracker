"""_summary_
"""

import json
import yaml  # type: ignore


def json_to_yaml(in_file: str) -> None:
    """Create YAML file from JSON file, without sorting keys alphabetically.

    :param in_file: absolute path to JSON file
    :type in_file: str
    """

    with open(in_file, 'r') as rf, open(in_file.replace('json', 'yml'), "w") as wf:
        yaml.dump(json.load(rf), wf, sort_keys=False)


def main():
    # TODO: make user and athlete dynamic
    user = "gustavcollinrasmussen"
    athlete = "gustav_rasmussen"
    data_path = f"/Users/{user}/Library/CloudStorage/GoogleDrive-gcr84@hotmail.com/My Drive/DATA/fitness-tracker-data/{athlete}"

    # in_file = data_path + f"/log_archive/JSON/2023/June/test.json"
    in_file = data_path + "/db.json"

    json_to_yaml(in_file)


if __name__ == "__main__":
    main()
