"""
Date: 2021-12-21
Author: Gustav Collin Rasmussen
Purpose: Train a linear-regression model on simulated weight-training data,
using the Scikit Learn library
"""

# TODO: load sim data into X and y
# TODO: print coefficients
# TODO: plot data and fit together in same figure

# from statistics import mean

import pandas as pd
from sklearn import linear_model
from tinydb import TinyDB

from CRUD.training import show_exercise

reg = linear_model.LinearRegression()
db = TinyDB("data/db.json")
log = db.table("log")

df1 = pd.DataFrame(data=show_exercise(log, "squat", "2021-12-11"))
df1["date"] = "2021-12-11"
df2 = pd.DataFrame(data=show_exercise(log, "squat", "2021-12-25"))
df2["date"] = "2021-12-25"

frames = [df1, df2]
df = pd.concat(frames)

# print(df)


def one_rep_max_estimator():
    """The ACSM (American College of Sports Medicine) protocol
    is used to implement the 1RM estimation
    """

    df["1RM"] = df["weight"].str.strip(" kg").astype(int) / (
        (100 - df["reps"] * 2.5) / 100
    )

    return df.groupby("date")[["1RM"]].agg("max")


print(one_rep_max_estimator())

# X: workout-dates as int  y: max 1RM estimate in kg, for squat
# X = [[0, 102.857143], [14, 91.428571]]  # [[0, 0], [1, 1], [2, 2]]
# y = [102.857143, 91.428571]  # [0, 1, 2]

# reg.fit(X, y)
# print(reg.coef_)
