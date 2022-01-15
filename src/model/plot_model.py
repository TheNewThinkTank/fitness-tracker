"""
Date: 2021-12-27
Author: Gustav Collin Rasmussen
Purpose: Plot weight-training data with fit
"""

import os
import sys
from datetime import datetime
from pprint import pprint as pp
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from tinydb import TinyDB

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from model import get_data, get_df, one_rep_max_estimator


def create_plots(x, y, exercise):
    """Plot training data with fit"""

    # plt.clf()
    plt.figure(figsize=(8, 8))

    # Only add confidence intervals if there are sufficient data points
    if len(x) < 10:
        sns.set_theme()
        ax = sns.scatterplot(x=x, y=y)
        ax.set_title(f"{exercise}")
    else:
        ax = sns.regplot(x=x, y=y, ci=68, truncate=False)
        ax.set_title(f"{exercise} w. 68 % confidence intervals")

    xticks = ax.get_xticks()
    xticks_dates = [datetime.fromtimestamp(x).strftime("%Y-%m-%d") for x in xticks]
    # pp(xticks_dates)
    ax.set_xticklabels(xticks_dates)
    plt.ylim(0, max(y) + 5)
    # plt.xlim(min(x), max(x))
    # ax.set_xlabel("workout date")
    plt.xticks(rotation=45)
    ax.set_ylabel(f"1 RM estimates [kg]")
    # plt.show()
    # print(x, y)
    plt.savefig(f"img/fitted_data_{exercise}.png")
    plt.clf()  # clear figure before next plot


def main():
    """Get data and create figure."""

    # datatypes = ["real", "simulated"]
    datatype = sys.argv[1]  # datatypes[1]
    db = TinyDB("data/db.json") if datatype == "real" else TinyDB("data/sim_db.json")
    table = db.table("weight_training_log")

    splits_and_key_exercises = [
        ("chest", "barbell_bench_press"),
        # ("back_and_biceps", "seated_row"),
        # ("back", "seated_row"),
        # ("legs", "squat"),
        # ("legs", "deadlift"),
        # ("legs", "legpress"),
    ]

    for split, exercise in splits_and_key_exercises:

        df = get_df(table, split, exercise)
        df_1rm = one_rep_max_estimator(df)
        x, y = get_data(df_1rm)
        # print(x, y)
        assert len(x) == len(y)
        create_plots(x, y, exercise)


if __name__ == "__main__":
    main()
