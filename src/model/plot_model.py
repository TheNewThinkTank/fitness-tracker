"""
Date: 2021-12-27
Author: Gustav Collin Rasmussen
Purpose: Plot weight-training data with fit
"""

import os
import sys

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import linear_model
from tinydb import TinyDB

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

reg = linear_model.LinearRegression()

datatypes = ["real", "simulated"]
datatype = datatypes[1]

db = TinyDB("data/db.json") if datatype == "real" else TinyDB("data/sim_db.json")
log = db.table("log")

from model import get_df, one_rep_max_estimator, fit_data


def get_data(split, exercise):
    """Prepare pandas dataframes with training data for plotting"""

    df = get_df(split, exercise)
    df_1rm = one_rep_max_estimator(df)
    x, y, coeffs = fit_data(df_1rm)

    return x, y, coeffs


def create_plots(x, y, exercise):
    """Plot training data with fit"""
    plt.figure(figsize=(6, 4))
    ax = sns.regplot(x=x, y=y, ci=68, truncate=False)
    ax.set_xlabel("date (timestamp)")
    ax.set_ylabel(f"1 RM estimates [kg]")
    ax.set_title(f"{exercise} w. 68 % confidence intervals")
    plt.savefig(f"img/fitted_data_{exercise}.png")
    plt.clf()  # clear figure before next plot


def main():
    """Get data and create figure."""

    splits_and_key_exercises = [
        ("chest", "barbell bench press"),
        ("legs", "squat"),
        ("legs", "deadlift"),
        ("legs", "legpress"),
    ]

    for split, exercise in splits_and_key_exercises:
        x, y, _ = get_data(split, exercise)
        create_plots(x, y, exercise)


if __name__ == "__main__":
    main()
