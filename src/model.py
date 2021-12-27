"""
Date: 2021-12-21
Author: Gustav Collin Rasmussen
Purpose: Train a linear-regression model on simulated weight-training data,
using the Scikit Learn library
"""

# TODO: plot data and fit together in same figure

from datetime import datetime

import pandas as pd
from sklearn import linear_model
from tinydb import TinyDB

from CRUD.training import show_exercise

reg = linear_model.LinearRegression()

datatypes = ["real", "simulated"]
datatype = datatypes[1]

db = TinyDB("data/db.json") if datatype == "real" else TinyDB("data/sim_db.json")
log = db.table("log")


def get_df(split="legs", exercise="squat"):
    """."""
    if datatype == "real":
        df1 = pd.DataFrame(data=show_exercise(log, exercise, "2021-12-11"))
        df1["date"] = "2021-12-11"
        df2 = pd.DataFrame(data=show_exercise(log, exercise, "2021-12-25"))
        df2["date"] = "2021-12-25"
        frames = [df1, df2]

    elif datatype == "simulated":
        frames = []
        for item in log:
            if item["split"] == split:
                if exercise in item["exercises"].keys():
                    df = pd.DataFrame(item["exercises"][exercise])
                    df["date"] = item["date"]
                    frames.append(df)

    else:
        return "Invalid datatype, choose between [real/simulated]"

    return pd.concat(frames)


def one_rep_max_estimator(df):
    """The ACSM (American College of Sports Medicine) protocol
    is used to implement the 1RM estimation
    """

    df["1RM"] = df["weight"].str.strip(" kg").astype(float) / (
        (100 - df["reps"] * 2.5) / 100
    )

    return df.groupby("date")[["1RM"]].agg("max")


def fit_data(df):
    """Lin reg
    X: workout-dates as int  y: max 1RM estimate in kg, for squat
    """
    date_strs = df.index.tolist()
    x = [datetime.fromisoformat(i).timestamp() for i in date_strs]
    y = df["1RM"].tolist()
    X = []
    for i, j in zip(x, y):
        X.append([i, j])
    reg.fit(X, y)
    return x, y, reg.coef_


def main():
    """Prepare dfs, calc 1RM and do linear regression."""
    df = get_df()
    df_1rm = one_rep_max_estimator(df)
    x, y, coeffs = fit_data(df_1rm)
    print(x, y, coeffs)


if __name__ == "__main__":
    main()
