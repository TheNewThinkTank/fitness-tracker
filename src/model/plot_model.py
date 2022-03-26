"""
Date: 2021-12-27
Author: Gustav Collin Rasmussen
Purpose: Plot weight-training data with fit
"""

import os
import sys
from datetime import datetime

# from pprint import pprint as pp
import matplotlib.pyplot as plt  # type: ignore

# import matplotlib.ticker as mticker  # type: ignore
import seaborn as sns  # type: ignore
from tinydb import TinyDB  # type: ignore

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from model import get_data, get_df, one_rep_max_estimator


def create_plots(datatype: str, x: list, y: list, exercise: str) -> None:
    """Plot training data with fit"""

    plt.figure(figsize=(8, 8))

    # Only add confidence intervals if there are sufficient data points
    if len(x) < 5:
        sns.set_theme()
        ax = sns.scatterplot(x=x, y=y)
        ax.set_title(f"{exercise}")
    else:
        ax = sns.regplot(x=x, y=y, ci=68, truncate=False)
        ax.set_title(f"{exercise} w. 68 % confidence intervals")

    xticks = ax.get_xticks()
    xticks_dates = [datetime.fromtimestamp(x).strftime("%Y-%m-%d") for x in xticks]

    ax.set_xticklabels(xticks_dates)
    plt.ylim(0, max(y) + 5)
    plt.xticks(rotation=45)
    ax.set_ylabel("1 RM estimates [kg]")
    plt.savefig(f"img/{datatype}_fitted_data_{exercise}.png")
    plt.clf()  # clear figure before next plot


def main() -> None:
    """Get data and create figure."""

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--datatype", type=str, required=True)  # real/simulated
    args = parser.parse_args()
    datatype = args.datatype

    db = TinyDB("data/db.json") if datatype == "real" else TinyDB("data/sim_db.json")
    table = db.table("weight_training_log")

    splits_and_key_exercises = [
        (["chest", "push"], "barbell_bench_press"),
        (["back"], "seated_row"),
        (["legs"], "squat"),
        (["legs"], "deadlift"),
        (["legs"], "legpress"),
    ]

    for splits, exercise in splits_and_key_exercises:

        df = get_df(table, splits, exercise)
        df_1rm = one_rep_max_estimator(df)
        x, y = get_data(df_1rm)
        create_plots(datatype, x, y, exercise)


if __name__ == "__main__":
    main()
