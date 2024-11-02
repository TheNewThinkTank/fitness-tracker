"""_summary_
"""

from file_convertion_tools.json_to_yaml import json_to_yaml  # type: ignore


def main():
    # TODO: make user and athlete dynamic
    user = "gustavcollinrasmussen"
    athlete = "gustav_rasmussen"
    data_path = f"/Users/{user}/Library/CloudStorage/GoogleDrive-gcr84@hotmail.com/My Drive/DATA/fitness-tracker-data/{athlete}"

    in_file_name = "/db.json"  # f"/log_archive/JSON/2023/June/test.json"
    in_file = data_path + in_file_name

    json_to_yaml(in_file)


if __name__ == "__main__":
    main()
