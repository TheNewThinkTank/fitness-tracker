"""
Date: 2021-12-19
Author: Gustav Collin Rasmussen
Purpose: Plot weight-training data
"""

import matplotlib.pyplot as plt
import pandas as pd

# import numpy as np
import seaborn as sns
from tinydb import TinyDB

from CRUD.training import show_exercise


def get_data(date, exercises):
    """Prepare pandas dataframes with training data for plotting"""
    db = TinyDB("data/db.json")
    log = db.table("log")

    return [pd.DataFrame(data=show_exercise(log, ex, date)) for ex in exercises]


def create_barplots(dfs, date):
    """Plot training data from specific date"""

    # TODO: highten legend transparency
    # TODO: set figure-level x- and y labels ("Set No." and "Repetitions")

    sns.set_theme(style="white", context="talk")

    f, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 7), sharex=True)

    sns.barplot(
        x=dfs[0]["set no."],
        y=dfs[0]["reps"],
        hue=dfs[0]["weight"],
        palette="rocket",
        ax=ax1,
    )
    ax1.axhline(0, color="k", clip_on=False)
    ax1.set_ylabel("squat")
    ax1.bar_label(ax1.containers[0])

    sns.barplot(
        x=dfs[1]["set no."],
        y=dfs[1]["reps"],
        hue=dfs[1]["weight"],
        palette="vlag",
        ax=ax2,
    )
    ax2.axhline(0, color="k", clip_on=False)
    ax2.set_ylabel("leg extention")
    ax2.bar_label(ax2.containers[0])

    sns.barplot(
        x=dfs[2]["set no."],
        y=dfs[2]["reps"],
        hue=dfs[2]["weight"],
        palette="deep",
        ax=ax3,
    )
    ax3.axhline(0, color="k", clip_on=False)
    ax3.set_ylabel("deadlift")
    ax3.bar_label(ax3.containers[0])

    sns.despine(bottom=True)
    plt.setp(f.axes, yticks=[])
    plt.tight_layout(h_pad=2)
    plt.title(f"Workout date: {date}")

    # plt.ylabel("Repetitions")
    # plt.xlabel("Set No.")

    sns.move_legend(ax1, "upper right", bbox_to_anchor=(1, 1))
    # sns.move_legend(ax2, "center right", bbox_to_anchor=(1, 1))
    sns.move_legend(ax3, "center right", bbox_to_anchor=(1, 1))

    # ax3.legend(fancybox=True, framealpha=0.5)

    plt.savefig(f"img/workout_{date}.png")


def main():
    """Get data and create figure."""
    date = "2021-12-11"
    dfs = get_data(date, ["squat", "leg extention", "deadlift"])
    print(dfs)
    # create_barplots(dfs, date)


if __name__ == "__main__":
    main()
