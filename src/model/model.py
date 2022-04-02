"""
    Date: 2021-12-21
    Author: Gustav Collin Rasmussen
    Purpose: Train a linear-regression model on simulated weight-training data,
             using the Scikit Learn library
"""

from datetime import datetime
import json
import pandas as pd  # type: ignore

import pathlib

# from sklearn import linear_model
from tinydb import TinyDB  # type: ignore


def get_df(
    log, splits: list = ["chest", "push"], exercise: str = "barbell_bench_press"
):
    """."""
    frames = []
    for item in log:
        if any(x in item["split"] for x in splits):
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
    import logging

    pathlib.Path("logs/").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M",
        filename="logs/model.log",
        filemode="w",
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    logging.info("Running %s ...", "/".join(__file__.split("/")[-4:]))
    logger1 = logging.getLogger("model.area1")
    logger2 = logging.getLogger("model.area2")

    data_models = ["real", "simulated"]
    datatype = data_models[0]

    data = json.load(open(file="./config.json", encoding="utf-8"))
    db = (
        TinyDB(data["real_workout_database"])
        if datatype == "real"
        else TinyDB(data["simulated_workout_database"])
    )
    table = (
        db.table(data["real_weight_table"])
        if datatype == "real"
        else db.table(data["simulated_weight_table"])
    )

    logger1.info("data_model: %s", datatype)
    logger1.debug("db: %s", db)
    logger1.debug("table: %s", table)

    df = get_df(table)
    df_1rm = one_rep_max_estimator(df)
    x, y = get_data(df_1rm)

    logger2.info("x, y: %s, %s", x, y)


if __name__ == "__main__":
    main()
