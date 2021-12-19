"""
Date: 2021-12-19
Author: Gustav Collin Rasmussen
Purpose: Plot weight-training data
"""

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from tinydb import TinyDB

from training import describe_workout, show_exercise


def get_data():
    db = TinyDB("data/db.json")
    log = db.table("log")

    # data = describe_workout(log, "2021-12-13")
    data = show_exercise(log, "squat", "2021-12-11")
    return data


def show_plot(data):
    """Plot training data from specific date"""
    sns.set_theme(style="white", context="talk")

    f, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5), sharex=True)

    x = np.array(["set 1", "set 2", "set 3", "set 4"])
    y1 = np.array([70, 80, 90, 90])
    sns.barplot(x=x, y=y1, palette="rocket", ax=ax1)
    ax1.axhline(0, color="k", clip_on=False)
    ax1.set_ylabel("squat")

    y2 = np.array([70, 80, 90, 90])
    sns.barplot(x=x, y=y2, palette="vlag", ax=ax2)
    ax2.axhline(0, color="k", clip_on=False)
    ax2.set_ylabel("deadlift")

    sns.despine(bottom=True)
    plt.setp(f.axes, yticks=[])
    plt.tight_layout(h_pad=2)
    plt.title("Leg day - reps and weight")
    # plt.legend(labels=["a", "b", "c", "d"])
    plt.savefig("img/legday.png")


def main(data):
    show_plot(data)


if __name__ == "__main__":
    data = get_data()
    # print(data)
    main(data)
