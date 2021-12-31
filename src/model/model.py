"""
    Date: 2021-12-21
    Author: Gustav Collin Rasmussen
    Purpose: Train a linear-regression model on simulated weight-training data,
             using the Scikit Learn library
"""

# from datetime import datetime

from datetime import datetime
import pandas as pd

# from sklearn import linear_model
from tinydb import TinyDB


def get_df(log, split="legs", exercise="squat"):
    """."""
    frames = []
    for item in log:
        if item["split"] == split:
            if exercise in item["exercises"].keys():
                df = pd.DataFrame(item["exercises"][exercise])
                df["date"] = item["date"]
                frames.append(df)
    return pd.concat(frames)


def one_rep_max_estimator(df):
    """The ACSM (American College of Sports Medicine) protocol
    is used to implement the 1RM estimation
    """
    df["1RM"] = df["weight"].str.strip(" kg").astype(float) / (
        (100 - df["reps"] * 2.5) / 100
    )
    return df.groupby("date")[["1RM"]].agg("max")


def get_data(df):
    """
    date_strs: workout-dates, y: max 1RM estimate in kg
    """
    date_strs = df.index.tolist()
    x = [datetime.fromisoformat(i).timestamp() for i in date_strs]
    y = df["1RM"].tolist()
    y = [float("{:.2f}".format(x)) for x in y]
    return x, y


def main():
    """Prepare dfs, calc 1RM and do linear regression."""

    datatypes = ["real", "simulated"]
    datatype = datatypes[0]
    db = TinyDB("data/db.json") if datatype == "real" else TinyDB("data/sim_db.json")
    table = db.table("weight_training_log")

    df = get_df(table)
    df_1rm = one_rep_max_estimator(df)
    x, y = get_data(df_1rm)
    print(x, y)


if __name__ == "__main__":
    main()
