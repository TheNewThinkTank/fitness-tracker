"""
"""

from datetime import datetime
from pprint import pformat  # type: ignore
from typing import Any
from loguru import logger  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import pandas as pd  # type: ignore
from src.common.metrics import canonical_exercise
from src.utils.training_metadata import load_programs, parse_target, program_for_date, split_id
from src.utils.workout_repository import WorkoutRepository


def extract_actual_rep_ranges(table, splits):
    frames = dict()
    selected_splits = {split_id(split) for split in splits}
    for item in table:
        if split_id(item.get("split") or "") not in selected_splits:
            continue

        date = item['date']
        frames.setdefault(date, {})
        for exercise in item['exercises']:
            identifier = canonical_exercise(exercise)
            frames[date].setdefault(identifier, [])
            for _set in item['exercises'][exercise]:
                frames[date][identifier].append(_set['reps'])

    return frames


def extract_recommended_rep_ranges(data, program_id="program_10"):
    rep_ranges = {}
    for exercises in data.get(program_id, {}).values():
        if not isinstance(exercises, dict):
            continue
        for exercise, details in exercises.items():
            target = parse_target(exercise, details)
            if target and target.reps_min is not None and target.reps_max is not None:
                rep_ranges[target.exercise_id] = (target.reps_min, target.reps_max)
    return rep_ranges


def main() -> None:
    current_year = datetime.now().year
    repository = WorkoutRepository()
    program = program_for_date(load_programs(), datetime.now().date())
    if program is None or not program.targets:
        logger.warning("No structured targets available for the current program.")
        return
    table = [record for _, record in repository.documents(current_year)]
    splits = program.splits

    logger.debug(pformat(extract_actual_rep_ranges(table, splits)))

    rep_ranges = {target.exercise_id: (target.reps_min, target.reps_max) for section in program.targets for target in section.targets if target.reps_min is not None and target.reps_max is not None}
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

    if not flat_data:
        logger.warning("No matching performed sets and numeric targets to plot.")
        return
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
