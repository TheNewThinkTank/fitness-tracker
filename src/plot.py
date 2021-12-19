"""
Date: 2021-12-19
Author: Gustav Collin Rasmussen
Purpose: Plot weight-training data
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from tinydb import TinyDB

from training import describe_workout, show_exercise

# import matplotlib
# print("matplotlib: {}".format(matplotlib.__version__))


def get_data(date, exercises):
    db = TinyDB("data/db.json")
    log = db.table("log")

    dfs = []
    for exercise in exercises:
        _ = show_exercise(log, exercise, date)
        dfs.append(pd.DataFrame(data=_))

    return dfs


def show_plot(dfs, date):
    """Plot training data from specific date"""
    sns.set_theme(style="white", context="talk")

    f, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5), sharex=True)

    sns.barplot(
        x=dfs[0]["set no."],
        y=dfs[0]["reps"],
        hue=dfs[0]["weight"],
        palette="rocket",
        ax=ax1,
    )
    ax1.axhline(0, color="k", clip_on=False)
    ax1.set_ylabel("squat, reps")
    ax1.bar_label(ax1.containers[0])

    sns.barplot(
        x=dfs[1]["set no."],
        y=dfs[1]["reps"],
        hue=dfs[1]["weight"],
        palette="vlag",
        ax=ax2,
    )
    ax2.axhline(0, color="k", clip_on=False)
    ax2.set_ylabel("leg extention, reps")
    ax2.bar_label(ax2.containers[0])

    sns.despine(bottom=True)
    plt.setp(f.axes, yticks=[])
    plt.tight_layout(h_pad=2)
    plt.title(f"Workout date: {date}")
    plt.savefig(f"img/workout_{date}.png")


def main(dfs, date):
    show_plot(dfs, date)


if __name__ == "__main__":
    date = "2021-12-11"
    dfs = get_data(date, ["squat", "leg extention"])
    # for df in dfs:
    #     print(df)
    main(dfs, date)
