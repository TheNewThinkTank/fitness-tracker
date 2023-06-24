import json
import yaml


def json_to_yaml(in_file: str) -> None:
    """Create YAML file from JSON file, without sorting keys alphabetically.

    :param in_file: absolute path to JSON file
    :type in_file: str
    """

    with open(in_file, 'r') as rf, open(in_file.replace('json', 'yml'), "w") as wf:
        yaml.dump(json.load(rf), wf, sort_keys=False)


if __name__ == "__main__":
    in_file = "/Users/gustavcollinrasmussen/Library/CloudStorage/GoogleDrive-gcr84@hotmail.com/My Drive/DATA/fitness-tracker-data/gustav_rasmussen/log_archive/JSON/2023/June/test.json"
    json_to_yaml(in_file)
