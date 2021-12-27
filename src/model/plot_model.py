"""
Date: 2021-12-27
Author: Gustav Collin Rasmussen
Purpose: Plot weight-training data with fit
"""

import os
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn import linear_model
from tinydb import TinyDB

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import CRUD.training as training

reg = linear_model.LinearRegression()

datatypes = ["real", "simulated"]
datatype = datatypes[1]

db = TinyDB("data/db.json") if datatype == "real" else TinyDB("data/sim_db.json")
log = db.table("log")

from model import get_df, one_rep_max_estimator, fit_data


def get_data():
    """Prepare pandas dataframes with training data for plotting"""

    df = get_df()
    df_1rm = one_rep_max_estimator(df)
    x, y, coeffs = fit_data(df_1rm)

    return x, y, coeffs


def create_plots(x, y):
    """Plot training data with fit"""
    ax = sns.regplot(x=x, y=y, ci=68, truncate=False)
    ax.set_xlabel("date (timestamp)")
    ax.set_ylabel("1 RM estimate (squat) with fit")
    # plt.show()
    plt.savefig(f"img/fitted_data.png")


def main():
    """Get data and create figure."""
    x, y, _ = get_data()
    create_plots(x, y)


if __name__ == "__main__":
    main()
