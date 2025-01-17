"""
Plot weight-training data.
"""

from typing import Any
import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore
# import sys  # type: ignore
from src.crud.read import show_exercise  # type: ignore
from src.utils.get_exercises import get_available_exercises  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore
from src.utils.config_loader import ConfigLoader  # type: ignore

config = ConfigLoader.load_config()
IMG_PATH = config["img_path"]


def get_data(date: str, split: str) -> dict[str, pd.DataFrame] | dict:
    """Prepare pandas dataframes with training data for plotting.

    :param date: Date of the workout
    :type date: str
    :param split: Split of the workout
    :type split: str
    :return: Dataframes with training data
    :rtype: dict[str, pd.DataFrame] | dict
    """

    _, table, training_catalogue = set_db_and_table(datatype="real")
    exercises = get_available_exercises(training_catalogue, split)

    return {
        ex: df
        for ex in exercises
        if not (df := pd.DataFrame(data=show_exercise(table, ex, date))).empty
    }


def compare_workouts(dfs_1: dict, dfs_2: dict) -> tuple[dict[Any, Any], dict[Any, Any]]:
    """Compare two workouts and return common exercises.

    :param dfs_1: Dataframes with training data
    :type dfs_1: dict
    :param dfs_2: Dataframes with training data
    :type dfs_2: dict
    :return: Dataframes with common exercises
    :rtype: tuple[dict[Any, Any], dict[Any, Any]]
    """

    common_exercises = []
    for k in sorted(set(dfs_1.keys()).intersection(set(dfs_2.keys()))):
        common_exercises.append(k)

    dfs_1_common = {k: v for k, v in dfs_1.items() if k in common_exercises}
    dfs_2_common = {k: v for k, v in dfs_2.items() if k in common_exercises}

    return dfs_1_common, dfs_2_common


# TODO: Move to datetime package
def validate_date_format(date: str) -> str:
    """Validate date format and return year.

    :param date: Date of the workout
    :type date: str
    """

    if date[4] != "-":
        raise ValueError("Invalid date format. Should be YYYY-MM-DD.")
    return date[:4]


def create_barplots(dfs: dict, date: str) -> None:
    """Plot training data for specific date.

    :param dfs: Dataframes with training data
    :type dfs: dict
    :param date: Date of the workout
    :type date: str
    """

    # TODO: highten legend transparency
    # TODO: set figure-level x- and y labels ("set_number" and "Repetitions")

    year = validate_date_format(date)

    keys = list(dfs.keys())
    values = list(dfs.values())

    sns.set_theme(style="white", context="talk")

    match len(dfs):
        case 3:
            print("3 exercises to plot")
            f, axes = plt.subplots(len(dfs), 1, figsize=(11, 9), sharex=True)
            # Ensure axes is an iterable array even if it's a single Axes object
            if not isinstance(axes, np.ndarray):
                axes = np.array([axes])
            ax1, ax2, ax3 = axes
        case 4:
            print("4 exercises to plot")
            f, axes = plt.subplots(
                len(dfs), 1, figsize=(11, 9), sharex=True
            )
            if not isinstance(axes, np.ndarray):
                axes = np.array([axes])
            ax1, ax2, ax3, ax4 = axes

            sns.barplot(
                x=values[3]["set_number"],
                y=values[3]["reps"],
                hue=values[3]["weight"],
                palette="rocket",
                ax=ax4,
            )
            ax4.axhline(0, color="k", clip_on=False)
            ax4.set_ylabel(keys[3])
            ax4.bar_label(ax4.containers[0])
        case _:
            print("Wrong number of exercises. Should be 3 or 4.")

    sns.barplot(
        x=values[0]["set_number"],
        y=values[0]["reps"],
        hue=values[0]["weight"],
        palette="rocket",
        ax=ax1,
    )
    ax1.axhline(0, color="k", clip_on=False)
    ax1.set_ylabel(keys[0])
    ax1.bar_label(ax1.containers[0])

    sns.barplot(
        x=values[1]["set_number"],
        y=values[1]["reps"],
        hue=values[1]["weight"],
        palette="vlag",
        ax=ax2,
    )
    ax2.axhline(0, color="k", clip_on=False)
    ax2.set_ylabel(keys[1])
    ax2.bar_label(ax2.containers[0])

    sns.barplot(
        x=values[2]["set_number"],
        y=values[2]["reps"],
        hue=values[2]["weight"],
        palette="deep",
        ax=ax3,
    )
    ax3.axhline(0, color="k", clip_on=False)
    ax3.set_ylabel(keys[2])
    ax3.bar_label(ax3.containers[0])

    sns.despine(bottom=True)
    plt.setp(f.axes, yticks=[])
    plt.tight_layout(h_pad=2)
    plt.title(f"Workout date: {date}")
    sns.move_legend(ax1, "upper right", bbox_to_anchor=(1, 1))
    sns.move_legend(ax3, "center right", bbox_to_anchor=(1, 1))    

    plt.savefig(f"{IMG_PATH}{year}/workout_{date}.png")


def main() -> None:
    """Get data and create figure.
    """

    dates = [
        "2021-12-11",
        # "2022-03-14",
        "2022-05-28",
    ]

    split = "legs"

    dfs_first_leg_workout = get_data(dates[0], split)
    dfs_last_leg_workout = get_data(dates[-1], split)
    dfs_1_common, dfs_2_common = compare_workouts(
        dfs_first_leg_workout, dfs_last_leg_workout
    )

    create_barplots(dfs_1_common, dates[0])
    create_barplots(dfs_2_common, dates[-1])
    plt.show()


if __name__ == "__main__":
    main()
