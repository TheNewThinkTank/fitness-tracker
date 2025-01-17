"""
Get all exercises available for a given musclegroup.
"""

from src.utils.set_db_and_table import set_db_and_table  # type: ignore
from src.utils.file_conversions.load_yaml import load_yaml_file  # type: ignore


def get_available_exercises(training_catalogue: str, split: str) -> list[str]:
    """Fetch musclegroup-exercises catalogue.

    :param training_catalogue: Exercises available for each musclegroup
    :type training_catalogue: str
    :param split: Name of musclegroup
    :type split: str
    :return: A list of available exercises for a given split / musclegroup
    :rtype: list
    """

    available_exercises = load_yaml_file(training_catalogue)

    return available_exercises[split]


def main() -> None:
    """Get all exercises available for a given musclegroup.
    """

    splits: list = [
        "back",
        # "chest",
        # "legs",
        # "shoulders",
    ]

    _, _, training_catalogue = set_db_and_table(datatype="real")

    for split in splits:
        print(get_available_exercises(training_catalogue, split))


if __name__ == "__main__":
    main()
