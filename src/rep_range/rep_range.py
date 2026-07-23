"""
"""

from datetime import datetime
from pprint import pformat  # type: ignore
from typing import Any
from loguru import logger  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import pandas as pd  # type: ignore
import yaml  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore


def extract_actual_rep_ranges(table, splits):
    frames = dict()
    for item in table:
        if not any(x in item["split"] for x in splits):
            continue

        date = item['date']
        frames[date] = {}
        for exercise in item['exercises']:
            frames[date][exercise] = []
            for _set in item['exercises'][exercise]:
                frames[date][exercise].append(_set['reps'])

    return frames


def extract_recommended_rep_ranges(data):
    rep_ranges = {}
    for section, exercises in data.get("program_10", {}).items():
        for exercise, details in exercises.items():
            parts = details.split(" of ")[-1].split(" reps")[0]
            rep_ranges[exercise] = tuple(map(int, parts.split("-")))
    return rep_ranges


def main() -> None:
    DATA_MODELS = ["real", "simulated"]
    datatype = DATA_MODELS[0]
    current_year = datetime.now().year
    _, table, _ = set_db_and_table(datatype, year=current_year)

    splits = [
        "upper_body_a",
        "lower_body_a",
        "upper_body_b",
        "lower_body_b",
    ]

    logger.debug(pformat(extract_actual_rep_ranges(table, splits)))

    in_file = "docs/project_docs/Workout-Programs/workout-program-detail.yml"
    with open(in_file, "r") as rf:
        data = yaml.safe_load(rf)

    rep_ranges = extract_recommended_rep_ranges(data)
    actual_reps = extract_actual_rep_ranges(table, splits)

    combined_data: dict[Any, Any] = {}
    for date, exercises in actual_reps.items():
        combined_data[date] = {}
        for exercise, performed_reps in exercises.items():
            if exercise in rep_ranges:
                min_reps, max_reps = rep_ranges[exercise]
                combined_data[date][exercise] = {
                    "performed_reps": performed_reps,
                    "recommended_range": (min_reps, max_reps),
                }

    logger.debug(pformat(combined_data))

    flat_data = []
    for date, exercises in combined_data.items():
        for exercise, details in exercises.items():
            min_reps, max_reps = details["recommended_range"]
            for i, reps in enumerate(details["performed_reps"], start=1):
                category = (
                    "too low" if reps < min_reps
                    else "too high" if reps > max_reps
                    else "within"
                )
                flat_data.append({
                    "Date": date,
                    "Exercise": exercise,
                    "Set": i,
                    "Reps": reps,
                    "Category": category,
                    "Min Reps": min_reps,
                    "Max Reps": max_reps,
                })

    df = pd.DataFrame(flat_data)

    g = sns.FacetGrid(
        df,
        col="Exercise",
        col_wrap=3,
        height=4,
        sharey=False,
        sharex=True,
    )
    g.map_dataframe(
        sns.scatterplot,
        x="Date",
        y="Reps",
        hue="Category",
        style="Category",
        palette={"too low": "red", "within": "green", "too high": "blue"},
        legend=False,
    )
    g.map_dataframe(sns.lineplot, x="Date", y="Min Reps", color="gray", linestyle="--", label="Min Recommended")
    g.map_dataframe(sns.lineplot, x="Date", y="Max Reps", color="gray", linestyle="--", label="Max Recommended")

    g.set_titles("{col_name}")
    g.set_axis_labels("Date", "Reps")
    g.figure.suptitle("Workout Reps vs Recommended Range", y=1.02)
    g.add_legend(title="Category")

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
